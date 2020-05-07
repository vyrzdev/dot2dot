# Likely a useless file.




from . import database
import requests
from square.client import Client
import uuid
import strict_rfc3339
import datetime


class InvalidChange(Exception):
    pass


class SquareListener:
    def __init__(self, access_token, locationID, environment="production"):
        self.access_token = access_token
        self.locationID = locationID
        self.environment = environment
        self.interface = None
        self.interface = Client.API(environment=self.environment, access_token=self.access_token)

    def getStock(self, sku):
        ID = self.getID(sku)
        responseJSON = self.interface.inventory.retrieve_inventory_count(ID)
        stock = float(responseJSON.body["counts"][0]["quantity"])
        return stock

    def getProductID(self, sku):
        requestJSON = {
            "query": {
                "exact_query": {
                    "attribute_name": "sku",
                    "attribute_value": sku,
                }
            }
        }
        responseJSON = self.interface.catalog.search_catalog_objects(requestJSON)
        ID = responseJSON.body["objects"][0]["id"]
        return ID

    def getSKU(self, productID):
        # TODO: Actually make this function.
        requestJSON = {
            "query": None
        }
        response = self.interface.catalog.search_catalog_objects(requestJSON)
        sku = response.body.get("objects")
        return sku

    def listen(self):
        while True:
            response = self.interface.inventory.batch_recieve_inventory_changes()
            if response.body is None:
                pass
            else:
                rawChanges = response.body["changes"]
                for change in rawChanges:
                    try:
                        productSKU = self.getSKU(change.get("catalog_object_id"))
                        productObject = database.models.product.objects(sku=productSKU).first()
                        if productObject is None:
                            print("This Product is not stored on our database!")
                        else:
                            newChange = database.models.stockChange(product=productObject,
                                                                    originPlatform="square",
                                                                    originPlatformOrderID=change.get(),
                                                                    originPlatformProductID=change.get("catalog_object_id"),
                                                                    )
                            if change["type"] == "PHYSICAL_COUNT":
                                newChange.action = "set"
                            elif (change["type"] == "ADJUSTMENT") and (change["adjustment"]["to_state"] in ["SOLD", "WASTE", "NONE"]):
                                newChange.action = "subtract"
                            elif (change["type"] == "ADJUSTMENT") and (change["adjustment"]["to_state"] in ["IN_STOCK"]):
                                newChange.action = "add"
                            elif (change["type"] == "ADJUSTMENT") and (change["adjustment"]["to_state"] in ["RETURNED_BY_CUSTOMER"]):
                                raise InvalidChange  # Deliberately trigger an error, thus causing this product to be skipped.
                            else:
                                raise InvalidChange


                            newChange.time_occurred = datetime.fromtimestamp(strict_rfc3339.rfc3339_to_timestamp(change["occurred_at"]))
                    except InvalidChange:
                        print("There was an invalid change!!! Dumping Change here: {}".format(change))

