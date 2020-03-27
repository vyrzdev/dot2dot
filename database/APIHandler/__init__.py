# from . import APIEtsy, APISquare, APIWooCommerce
from . import APISquare


class APIHandler:
    def __init__(self, APIHandlerConfig):
        self.APISquare = APISquare.APISquare(APIHandlerConfig.APISquareConfig)
        # self.APIEtsy = APIEtsy.APIEtsy(APIConfig.APIEtsyConfig)
        # self.APIWooCommerce = APIWooCommerce.APIWooCommerce(APIConfig.APIWooCommerceConfig)
        # self.APIArray = [self.APISquare, self.APIEtsy, self.APIWooCommerce]

    def getStockChanges(self, interval=30):
        stockChanges = list()
        for API in self.APIArray:
            stockChanges = stockChanges + API.getStockChanges(interval)
        for change in stockChanges:
            change.stage = 1
            change.save()
        # TODO: Add error catching
        return stockChanges

    def applyStockChange(self, changeObject):
        for API in self.APIArray:
            API.applyStockChange(changeObject)
        # TODO: Add error catching
