import mongoengine
from ..config import config
from . import models, stockHandler
# APIHandler


mongoengine.connect("dot-to-dot-test")


class DBInstance:
    def __init__(self, DBConfig):
        self.stockHandler = stockHandler.stockHandler(DBConfig.stockHandlerConfig)
        # self.APIHandler = APIHandler.APIHandler(DBConfig.APIHandlerConfig)
