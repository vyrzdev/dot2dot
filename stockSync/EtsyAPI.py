from . import database

import requests
from oauthlib import oauth1
import json


class productNotFoundOnDatabase(Exception):
    pass


class productNotIndexedOnEtsy(Exception):
    pass
    # Index Maybe?


class EtsyListener:
    def __init__(self, consumer_key, consumer_secret, resource_owner_key, resource_owner_secret, shop_id):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.resource_owner_key = resource_owner_key
        self.resource_owner_secret = resource_owner_secret
        self.shop_id = shop_id

        self.oauthclient = self.regen()

    # Authentication and client code.
    def regen(self):
        client = oauth1.Client(self.consumer_key,
                               client_secret=self.consumer_secret,
                               resource_owner_key=self.resource_owner_key,
                               resource_owner_secret=self.resource_owner_secret,
                               signature_method=sig)
        return client

    ###########################
    # Stock and Listener Code #
    ###########################
    def getEtsyIDs(self, sku):
        productObject = database.models.product.objects(sku=sku).first()
        if productObject is None:
            raise productNotFoundOnDatabase
        etsyListingID = productObject.metaData.get("etsyListingID")
        etsyProductID = productObject.metaData.get("etsyProductID")
        if (etsyListingID is None) or (etsyProductID is None):
            raise productNotIndexedOnEtsy
        return etsyListingID, etsyProductID
        # Unfortunately, currently Etsy has no way to query by SKU

    def getProductSKU(self, listingID, productID):
        query = {"metaData__etsyListingID": listingID, "metaData__etsyProductID": productID}
        productObject = database.models.product.objects(**query).first()
        if productObject is None:
            raise productNotFoundOnDatabase
        else:
            if __name__ == '__main__':
                return productObject.sku

    # A very costly (computationally) function to grab all listings from ETSY, read their skus and their ids.
    def indexEtsy(self):
        listings = self.api.get_listings(self.shop_id, page_size=100)
        for listing in listings:
            for product in listing.get_products():
                try:
                    dbProduct = database.models.product.objects(sku=product.sku).first()
                    if dbProduct is None:
                        print("Error! This product is not stored on database!")
                        raise productNotFoundOnDatabase
                    dbProduct.metaData["etsyListingID"] = listing.id
                    dbProduct.metaData["etsyProductID"] = product.id
                    dbProduct.save()
                except productNotFoundOnDatabase:
                    pass

    def listen(self):
        while True:
            # Make the request.
            r = requests.session()
            uri, headers, body = self.oauthclient.sign("https://openapi.etsy.com/v2/shops/{}/transactions".format(self.shop_id))
            response = r.get(uri, headers=headers, data=body)
            responseJSON = response.json()
            orders = responseJSON.get("results")

            for order in orders:
                productSKU = order.get("product_data").get("sku")
                if ((productSKU != "") and (productSKU is not None)) and (productSKU[0] !="X"):
                    dbProduct = database.models.product.objects(sku=productSKU).first()
                    if dbProduct is None:
                        pass
                    else:
                        newChange = database.models.stockChange(originPlatform="etsy", action="subtract")
                else:
                    pass


    # Object creation and unpacking.
    def get_listings(self, shop_id, page_size=25, limit=None):
        results = []
        offest = 0
        while True:
            uri, headers, body = self.oauthclient.sign(
                f"https://openapi.etsy.com/v2/shops/{shop_id}/listings/active?limit={page_size}&offset={offest}")
            r = requests.session()
            a = r.get(uri, headers=headers, data=body)
            ajson = a.json()

            results += ajson["results"]
            offest = ajson["pagination"]["next_offset"]
            if offest is None:
                break

            if limit is not None and limit < offest:
                break
        build = []
        for r in results:
            if limit is not None and len(build) == limit:
                break
            build.append(etsyListing(self, r))
        return build

    def getListing(self, id):
        uri, headers, body = self.oauthclient.sign(
            f"https://openapi.etsy.com/v2/listings/{id}?includes=Inventory")
        r = requests.session()
        a = r.get(uri, headers=headers, data=body)
        a = a.json()["results"][0]
        build = etsyListing(self, a)
        return build


class etsyListing:
    def __init__(self, client, raw):
        self.client = client
        self.raw = raw
        self.id = raw["listing_id"]
        self.state = raw["state"]
        self.user_id = raw["user_id"]
        self.category_id = raw["category_id"]
        self.title = raw["title"]
        self.description = raw["description"]
        self.price = float(raw["price"])
        self.currency = raw["currency_code"]
        self.tags = raw["tags"]
        self.quantity = int(raw["quantity"])
        self.url = raw["url"]

    def __str__(self):
        return f"BetsyListing({self.id})"

    def __repr__(self):
        return self.__str__()

    def get_products(self):
        uri, headers, body = self.client.oauthclient.sign(
            f"https://openapi.etsy.com/v2/listings/{self.id}/inventory")
        r = requests.session()
        a = r.get(uri, headers=headers, data=body)
        ajson = a.json()
        build = []
        for prod in ajson["results"]["products"]:
            build.append(etsyProduct(self.client, self, prod))
        return build

    def get_product(self, id):
        r = self.raw["Inventory"][0]["products"]
        for x in r:
            if str(x["product_id"]) == id:
                return etsyProduct(self.client, self, x)
            else:
                pass
        print("Product Does Not Exist!")


class etsyProduct:
    def __init__(self, client, listing, raw):
        self.client = client
        self.listing = listing
        self.raw = raw
        self.sku = raw["sku"]

        self.id = self.raw["product_id"]

        self.properties = []
        for prop in self.raw["property_values"]:
            self.properties.append(etsyProductProperty(prop))

        self.offerings = []
        for off in self.raw["offerings"]:
            self.offerings.append(etsyProductOffering(self.client, self, off))

    def __str__(self):
        return f"BetsyProduct({self.listing.id}, {self.id})"

    def __repr__(self):
        return self.__str__()

    @property
    def offering(self):
        if len(self.offerings) == 0:
            return None
        return self.offerings[0]

    @property
    def property(self):
        if len(self.properties) == 0:
            return None
        return self.properties[0]


class etsyProductProperty:
    def __init__(self, raw):
        self.id = raw["property_id"]
        self.name = raw["property_name"]
        self.scale_id = raw["scale_id"]
        self.scale_name = raw["scale_name"]
        self.values = raw["values"]
        self.values_ids = raw["value_ids"]

    @property
    def value(self):
        return self.values[0]

    @property
    def value_id(self):
        return self.values_ids[0]

    def __str__(self):
        return f"BetsyProductProperty({self.id}, {self.name}, {self.values})"

    def __repr__(self):
        return self.__str__()


class etsyProductOffering:
    def __init__(self, client, product, raw):
        self.client = client
        self.product = product
        self.raw = raw

        self.id = self.raw["offering_id"]
        self.price = float(self.raw["price"]["currency_formatted_raw"])
        self.quantity = int(self.raw["quantity"])

    def __str__(self):
        return f"BetsyProductOffering({self.product.listing.id}, {self.product.id}, {self.id})"

    def __repr__(self):
        return self.__str__()

    def update_quantity(self, value):
        uri, headers, body = self.client.regen(sig=oauth1.SIGNATURE_PLAINTEXT).sign(
            f"https://openapi.etsy.com/v2/listings/{self.product.listing.id}/inventory")
        r = requests.session()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        #################### Body Construction ########################
        products = self.product.listing.raw["Inventory"][0]["products"]
        for x in products:
            if x["product_id"] == self.product.id:
                x["offerings"] = [{"offering_id": self.id, "quantity": value, "price": self.price}]
            else:
                pass
        data = {
                "listing_id": self.product.listing.id,
                "products": json.dumps(products),
                'price_on_property': [200],
                'quantity_on_property': [200],
                'sku_on_property': [200]
        }

        ######################### Packet Send #########################
        a = r.put(uri, headers=headers, data=data)

        if a.status_code != 200:
            print(a.text)
            raise Exception("Something went wrong")
