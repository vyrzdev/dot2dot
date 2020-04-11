from flask import Markup
from . import fields


class Form:
    def __init__(self, action, method, fields=[]):
        self.action = action  # URL form response will be sent to...
        self.method = method  # Method response will be sent with...
        self.fieldObjects = fields  # Fields that will be in form by default.

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

    def addDefaultValues(self, existingObject):
        objectDict = existingObject.to_mongo().to_dict()
        for fieldObject in self.fieldObjects:
            if "__" in fieldObject.name:
                path = fieldObject.name.split("__")
                current = objectDict
                for pathItem in path:
                    current = current.get(pathItem)
                fieldObject.value = current
            else:
                fieldObject.value = objectDict.get(fieldObject.name)

    def addErrorMessages(self, errorDict):
        for fieldObject in self.fieldObjects:
            fieldObject.errorMessage = dict(enumerate(errorDict.get(fieldObject.name))).get(0)

    def buildFromSchema(self, Schema):
        fieldClassLookup = {
            "text": fields.Field,
            "textarea": fields.TextAreaField,
            "boolean": fields.BooleanField,
            "select": fields.SelectField,
            "list": fields.ListField
        }
        self.fieldObjects = []
        for fieldName in Schema.keys():
            details = Schema.get(fieldName)
            fieldType = details.get("type")
            fieldClass = fieldClassLookup.get(fieldType)
            if fieldType in ["text", "textarea", "list"]:
                field = fieldClass(fieldName, label=details.get("label"), required=details.get("required"))
            elif fieldType == "boolean":
                field = fieldClass(fieldName, label=details.get("label"))
            elif fieldType == "select":
                field = fieldClass(fieldName, label=details.get("label"), options=details.get("options"), allowMultiple=details.get("allowMultiple"), required=details.get("required"))
            self.fieldObjects.append(field)

    # On parse, we need to check every input, against its validation method, then we need to log if there is an error, return that, along with the parsed input.
    # Errors will be passed as dict: {"name": "ErrorMsg"}
    # Response will be passed as JSON.
    # Variable passed into parseResponse is request.form
    def parseResponse(self, formResponse):
        build = {
            "valid": True,
            "values": dict(),
            "errors": dict()
        }

        for fieldObject in self.fieldObjects:
            # Field specific parseMethods will return like: (value, errorList)
            # Get this specific fields response, in list form to support multiple selections.
            response = formResponse.getlist(fieldObject.name)
            # Pass this response into this specific fields parseMethod.
            value, errors = fieldObject.parseResponse(response)
            # If there is an error, the overall form is invalid.
            # This will likely cause the webserver to return a redirect with errors printed next to the applicable field.
            if len(errors) > 0:
                build["valid"] = False
            # Set this field values and errors in the entire forms JSON.
            build["values"][fieldObject.name] = value
            build["errors"][fieldObject.name] = errors
        return build

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
