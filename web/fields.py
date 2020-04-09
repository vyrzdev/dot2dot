import validator_collection
from flask import Markup
# TODO: Actually display errors, in render. ~ In Progress
# Data Flow: User Makes Error -> Error Logged -> Error added to form object -> Applicable error added to field objects -> Form Rendered with errors.

# TODO: Bring SelectFields and TextAreaField up to date.


# Base Field class. In usage simply is a text-input.
class Field:
    def __init__(self, name, validators=None, label=None, required=False, value=None, errorMessage=None):
        # Label is displayed to user, name is the dict key of the response.
        # Validators are currently actually 'checkers', they return True or False depending on if input meets certain criteria.
        # We should migrate soon over to validators, with try & except statements... This would enable us to get detailed error
        # messages.
        if label is None: label = name
        if validators is None: validators = list()
        self.value = value
        self.name = name
        self.label = label
        self.validators = validators
        self.errorMessage = errorMessage
        if required: self.validators.append(validator_collection.is_not_empty)

    def parseResponse(self, response):
        if len(response) > 1:
            # As this field is a simple text input, only 1 value is allowed.
            return "error", ["Multiple responses are not allowed for type Field"]
        elif len(response) == 0:
            response = ""
        else:
            # Pull the actual input.
            response = response[0]
        # Check if the input needs to be validated at all...
        if len(self.validators) == 0:
            # Return the input, with no errors.
            return response, []
        else:
            # Check input against each validator
            for validator in self.validators:
                if validator(response):
                    # If validator accepts, pass by.
                    print(f"{self.name} Passed Validator check!")
                else:
                    print(f"{self.name} Failed Validator check! Applied Validators: {self.validators}")
                    # If validator denys, return an error. We need to use proper validators, not checkers. ~ Gets us an error.
                    return "error", ["Failed a validator check. This input must be invalid. Proper error reporting is a future goal, find me in fields.py"]
            # If no validators return false, input must be valid!
            return response, []

    def render(self):
        conditional = ""
        if self.value is not None: conditional = f'value="{self.value}"'
        containerClass = "fieldContainer"
        labelClass = "fieldLabel"
        inputClass = "fieldInput"
        errorClass = "fieldError"
        markup = f'''
            <div class="{containerClass}">
                <label class="{labelClass}">{self.label}</label>
                <input type="text" class="{inputClass}" name="{self.name}" {conditional}>
                <p class="{errorClass}">{self.errorMessage}</p>
            </div>
        '''
        return Markup(markup)


# A large text field input.
# TODO: Fix this, parseResponse.
class TextAreaField:
    def __init__(self, name, label=None, validators=list(), required=False, value=None):
        if label is None: label = name
        self.value = value
        self.name = name
        self.label = label
        self.validators = validators
        if required: self.validators.append(validator_collection.is_not_empty)

    def render(self):
        conditional = ""
        if self.value is not None:
            conditional = f'value="{self.value}"'
        containerClass = "fieldContainer"
        labelClass = "fieldLabel"
        inputClass = "fieldInput"
        markup = f'''
            <div class="{containerClass}">
                <label class="{labelClass}">{self.label}</label>
                <input type="textarea" class="{inputClass}" name="{self.name}" placeholder="{self.placeholder}" {conditional}>
            </div>
        '''
        return Markup(markup)


class BooleanField:
    def __init__(self, name, label=None, value=None, required=None):
        self.value = value
        if label is None: label = name
        self.label = label
        self.name = name

    def parseResponse(self, response):
        if len(response) == 0:
            return False, []
        elif len(response) > 1:
            return "error", ["Multiple values are not allowed for this input type."]
        elif response[0] == "on":
            return True, []
        else:
            return "error", [f"Illegal value recieved! : {response}"]

    def render(self):
        conditional = ""
        if self.value is not None:
            conditional = "checked"
        containerClass = "fieldContainer"
        labelClass = "fieldLabel"
        inputClass = "tickboxInput"
        markup = f'''
            <div class="{containerClass}">
                <label class="{labelClass}">{self.label}</label>
                <input type="checkbox" name="{self.name}" class="{inputClass}" {conditional}>
            </div>
        '''
        return Markup(markup)


# TODO: Migrate to new value system, still on placeholder.
class SelectField:
    def __init__(self, name, options, label=None, required=False, allowMultiple=False):
        if label is None: label = name
        self.label = label
        self.name = name
        self.options = options
        self.required = required
        self.allowMultiple = allowMultiple

    def parseResponse(self, response):
        if len(response) == 0 and self.required:
            return "error", ["Input required"]
        elif len(response) > 1 and (not self.allowMultiple):
            return "error", ["Multiple values are not allowed for this Field Instance."]
        else:
            for item in response:
                if item not in self.options:
                    return "error", ["Invalid Value!"]
                else:
                    pass
            if self.allowMultiple:
                return response, []
            else:
                return response[0], []

    def render(self):
        tag = ""
        containerClass = "fieldContainer"
        labelClass = "fieldLabel"
        selectClass = "selectField"
        optionClass = "selectFieldOption"
        optionButtons = str()
        if self.allowMultiple: tag = "multiple"
        for option in self.options:
            optionButtons = f'{optionButtons}<option class="{optionClass}" value="{option}">{option}</option>'
        markup = f'''
            <div class={containerClass}>
                <label class="{labelClass}">{self.label}</label>
                <select name="{self.name}" class="{selectClass}" size="{len(self.options)}" {tag}>
                    {optionButtons}
                </select>
            </div>
        '''
        return Markup(markup)


# A SelectField, except that it allows users to select an object based on a dict of {"<button text>": <object>}
class TranslatedSelectField(SelectField):
    def __init__(self, name, optionsDict, label=None, required=False, allowMultiple=False):
        if label is None: label = name
        self.label = label
        self.name = name
        self.required = required
        self.options = list(optionsDict.keys())
        self.optionsDict = optionsDict
        self.allowMultiple = allowMultiple

    def parseResponse(self, response):
        unparsedValue, errors = super.parseResponse(response)
        if unparsedValue == "error":
            return unparsedValue, errors
        else:
            return self.optionsDict[unparsedValue], errors
