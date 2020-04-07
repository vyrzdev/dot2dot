import validator_collection
from flask import Markup

class Field:
    def __init__(self, name, validators=[], label=None, errorMsg="", required=False):
        if label is None: label = name
        self.name = name
        self.label = label
        self.validators = validators
        self.errorMsg = errorMsg
        if required: self.validators.append(validator_collection.is_not_empty)

    def checkInput(self, userInput):
        # Check if there are validators...
        if validators == []:
            return True
        # If there are validators, proceed to test them.
        else:
            for validator in self.validators:
                if validator(userInput):
                    pass
                else:
                    return False
            # If all of those validators succeed, return True.
            return True

    def render(self):
        containerClass = "fieldContainer"
        labelClass = "fieldLabel"
        inputClass = "fieldInput"
        markup = f'''
            <div class="{containerClass}">
                <label class="{labelClass}">{self.label}</label>
                <input type="text" class="{inputClass}" name="{self.name}">
            </div>
        '''
        return Markup(markup)

class TextAreaField:
    def __init__(self, name, label=None, validators=[], errorMsg="", required=False):
        if label is None: label = name
        self.name = name
        self.label = label
        self.validators = validators
        self.errorMsg = errorMsg
        if required: self.validators.append(validator_collection.is_not_empty)

    def checkInput(self, userInput):
        # Check if there are validators...
        if validators == []:
            return True
        # If there are validators, proceed to test them.
        else:
            for validator in self.validators:
                if validator(userInput):
                    pass
                else:
                    return False
            # If all of those validators succeed, return True.
            return True

    def render(self):
        containerClass = "fieldContainer"
        labelClass = "fieldLabel"
        inputClass = "fieldInput"
        markup = f'''
            <div class="{containerClass}">
                <label class="{labelClass}">{self.label}</label>
                <input type="text" class="{inputClass}" name="{self.name}">
            </div>
        '''
        return Markup(markup)



class BooleanField:
    def __init__(self, name, label=None):
        if label is None: label = name
        self.label = label
        self.name = name

    def checkInput(self, userInput):
        # No need for check, as it is selected by tickbox.
        return True

class SelectField:
    def __init__(self, name, options, label=None):
        if label is None: label = name
        self.label = label
        self.name = name
        self.options = options

    def checkInput(self, userInput):
        if userInput in self.options:
            return True
        else:
            return False

class WeightField:
    def __init__(self, name, label="Weight in kg:", errorMsg="Invalid Weight! Must not have units.", required=False):
        self = Field(name, validator_collection.is_numeric, errorMsg=errorMsg, label=label, required=required)

class LengthField:
    def __init__(self, name, label="Length in cm:", errorMsg="Invalid Length! Must not have units.", required=False):
        self = Field(name, validator_collection.is_numeric, errorMsg=errorMsg, label=label, require=required)
