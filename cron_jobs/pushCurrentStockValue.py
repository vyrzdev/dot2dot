import database
import config

DBInstance = database.DBInstance(config.config.DBConfig)

# Get local changes.
changesToApply = DBInstance.stockHandler.generateExternalChanges()

# Apply to external services.
for change in changesToApply:
    DBInstance.APIHandler.applyStockChange(change)
