# Take request.form, and orginal formObj, validate Input.
from flask import Markup

class Form:
    def __init__(self, action, method, fields=[]):
        self.action = action # URL form response will be sent to...
        self.method = method # Method response will be sent with...
        self.fieldObjects = fields # Fields that will be in form by default.

    # Add a field
    def addField(self, fieldObject):
        self.fieldObjects.append(fieldObject)

    # Delete a field.
    def removeField(self, fieldName):
        for field in self.fieldObjects:
            if field.name == fieldName:
                self.fieldObjects.remove(field)
            else:
                pass

    # Test responses against each fields validators
    def checkInputs(self, response):
        for field in self.fieldObjects:
            if field.checkInput():
                pass
            else:
                return False

    # Build form HTML...
    def render(self):
        fields = [field.render() for field in self.fieldObjects]
        containerClass = "formContainer"
        markup = f'''
            <div class={containerClass}>
                <form action="{self.action}" method="{self.method}">
                    {"".join(fields)}
                    <input type="submit">
                </form>
            </div>
        '''
        return Markup(markup)
