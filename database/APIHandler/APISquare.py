from square.client import Client
from ..models import stockChange, product
import uuid
import strict_rfc3339
import datetime


class APISquare:
    def __init__(self, config):
        self.interface = Client.API(
            environment=config.APIConfig.APISquare.environment,
            access_token=config.APIConfig.APISquare.access_token,
        )
        self.locationID = config.APIConfig.APISquare.locationID

    def pushProduct(self, productObject):
        pass

    def getStock(self, productObject):
        ID = self.getID(productObject)
        responseJSON = self.interface.inventory.retrieve_inventory_count(ID)
        stock = float(responseJSON.body["counts"][0]["quantity"])
        return stock

    def getProduct(self, ID):
        responseJSON = self.interface.catalog.retrieve_catalog_object(ID)
        sku = responseJSON.body["object"]["item_variation_data"]["sku"]
        productObject = product.objects(sku=sku)
        return productObject

    def getID(self, productObject):
        requestJSON = {
            "query": {
                "exact_query": {
                    "attribute_name": "sku",
                    "attribute_value": productObject.sku,
                }
            }
        }
        responseJSON = self.interface.catalog.search_catalog_objects(requestJSON)
        ID = responseJSON.body["objects"][0]["id"]
        return ID

    def getStockChanges(self, interval):
        requestJSON = {
            "updated_after": strict_rfc3339.timestamp_to_rfc3339_utcoffset((datetime.datetime.now() - datetime.timedelta(seconds=interval)).timestamp())
        }
        responseJSON = self.interface.inventory.batch_recieve_inventory_changes(requestJSON)
        if responseJSON.body == {}:
            return None
        rawChanges = responseJSON.body["changes"]
        changes = list()
        for change in rawChanges:
            try:
                productObject = self.getProduct(change["catalog_object_id"])
                newChange = stockChange(product=productObject, originService="square")
                if change["type"] == "PHYSICAL_COUNT":
                    newChange.changeType = "set"
                elif (change["type"] == "ADJUSTMENT") and (change["adjustment"]["to_state"] in ["SOLD", "WASTE", "NONE"]):
                    newChange.changeType = "subtract"
                elif (change["type"] == "ADJUSTMENT") and (change["adjustment"]["to_state"] in ["IN_STOCK"]):
                    newChange.changeType = "add"
                elif (change["type"] == "ADJUSTMENT") and (change["adjustment"]["to_state"] in ["RETURNED_BY_CUSTOMER"]):
                    newChange = None  # Deliberately trigger an error, thus causing this product to be skipped.
                    # TODO: Define a custom exception.
                else:
                    newChange = None
                newChange.time_created = datetime.fromtimestamp(strict_rfc3339.rfc3339_to_timestamp(change["occurred_at"]))
                changes.append(newChange)
            except:
                pass
        return changes

    def applyStockChange(self, changeObject):
        ID = self.getID(changeObject.product)
        lookup = {
            "set": ("PHYSICAL_COUNT", "IN_STOCK"),
            "add": ("ADJUSTMENT", "IN_STOCK"),
            "subtract": ("ADJUSTMENT", "SOLD")
        }
        changeType, state = lookup[changeObject.changeType]
        key = changeType.lower()
        requestJSON = {
            "idempotency_key": str(uuid.uuid4()),
            "changes": [
                {
                    "type": changeType,
                    key: {
                        "location": self.locationID,
                        "state": state,
                        "catalog_object_id": ID,
                        "quantity": changeObject.quantity,
                        "occurred_at": strict_rfc3339.timestamp_to_rfc3339_utcoffset(datetime.datetime.now().timestamp())
                    }
                }
            ]
        }
        return self.interface.inventory.batch_change_inventory(requestJSON)
