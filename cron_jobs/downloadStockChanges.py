import database
import config


DBInstance = database.DBInstance(config.config.DBConfig)
APIChanges = DBInstance.APIHandler.getStockChanges()

# Apply changes internally

DBInstance.stockHandler.applyChangesToInternalStock(APIChanges)
