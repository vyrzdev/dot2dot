import database
import config
from . import createProduct

DBInstance = database.DBInstance(config.config.DBConfig)


class CLIInterface:
    def __init__(self):
        print("Dot To Dot DB 2.0 ~ MongoDB")
        print("Create a Product?")
        input("- ")
        createProduct.productCreator().run()
