from .models import product, stockChange


class stockHandler:
    def __init__(self, stockHandlerConfig):
        self.placeholder = "foo"

    def applyChangesToInternalStock(self, changeArray):
        changeArray.sort(key=(lambda c: c.time_created))
        for change in changeArray:
            if change.changeType == "set":
                change.product.metaData["changesAppliedToAPI"] = False
                change.product.quantity = change.quantity
            elif change.changeType == "add":
                change.product.metaData["changesAppliedToAPI"] = False
                change.product.quantity = change.product.quantity + change.quantity
            elif change.changeType == "subtract":
                change.product.metaData["changesAppliedToAPI"] = False
                change.product.quantity = change.product.quantity - change.quantity
            else:
                print("Invalid Change Type:{}".format(change.changeType))
        change.save()

    def generateExternalChanges(self):
        externalChanges = list()
        for productObject in product.objects(metaData__changesAppliedToAPI=False):  # TODO: Review dot notation.
            generatedChange = stockChange(
                product=productObject,
                stage=2,
                originService="dot2dotdb",
                changeType="set",
                quantity=productObject.quantity
            )
            generatedChange.save()
            externalChanges.append(generatedChange)
        return externalChanges
