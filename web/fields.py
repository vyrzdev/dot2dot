import validator_collection
from flask import Markup
# TODO: Actually display errors, in render.
# Data Flow: User Makes Error -> Error Logged -> Error added to form object -> Applicable error added to field objects -> Form Rendered with errors.


# Base Field class. In usage simply is a text-input.
class Field:
    def __init__(self, name, validators=[], label=None, required=False):
        # Label is displayed to user, name is the dict key of the response.
        # Validators are currently actually 'checkers', they return True or False depending on if input meets certain criteria.
        # We should migrate soon over to validators, with try & except statements... This would enable us to get detailed error
        # messages.
        if label is None: label = name
        self.name = name
        self.label = label
        self.validators = validators
        if required: self.validators.append(validator_collection.is_not_empty)

    def parseResponse(self, response):
        if len(response) > 1:
            # As this field is a simple text input, only 1 value is allowed.
            return "error", ["Multiple responses are not allowed for type Field"]
        elif len(response) == 0:
            # Prevents KeyError. If empty input is disallowed, it will fail the validator checks.
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
                    pass
                else:
                    # If validator denys, return an error. We need to use proper validators, not checkers. ~ Gets us an error.
                    return "error", ["Failed a validator check. This input must be invalid. Proper error reporting is a future goal, find me in fields.py"]
            # If no validators return false, input must be valid!
            return response, []

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


# A large text field input.
# TODO: Fix this, parseResponse.
class TextAreaField:
    def __init__(self, name, label=None, validators=[], required=False):
        if label is None: label = name
        self.name = name
        self.label = label
        self.validators = validators
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
                <input type="textarea" class="{inputClass}" name="{self.name}">
            </div>
        '''
        return Markup(markup)


class BooleanField:
    def __init__(self, name, label=None):
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
        containerClass = "fieldContainer"
        labelClass = "fieldLabel"
        inputClass = "tickboxInput"
        markup = f'''
            <div class="{containerClass}">
                <label class="{labelClass}">{self.label}</label>
                <input type="checkbox" name="{self.name}" class="{inputClass}">
            </div>
        '''
        return Markup(markup)


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


# class LabelledSelectField:
#     def __init__(self, name, optionsDict, label=None, allowMultiple=False, required=False):
#         if label is None: label=name
#         self.options = optionsDict
#         self.optionLabels = list(optionsDict.keys())
#         self.optionItems = list(optionsDict.keys())
#         self.name = name
#         self.label = label
#         self.allowMultiple = allowMultiple
#         self.required = required
#
#     def checkInput(self, userInput):
#         # Assume input is not a List.
#         isList = False
#         if self.allowMultiple:
#             # If it is a List, as if self.allowMultiple: the form will return a list.
#             isList = True
#         if isList:
#             if len(userInput) == 0:
#                 if self.required: return False
#                 else: return True
#             else:
#                 for input in userInputList:
#                     if input in self.optionLabels:
#                         pass
#                     else:
#                         return False
#                     return True
#         else:
#             if userInput in self.optionLabels:
#                 return True
#             elif userInput is None and (not self.required):
#                 return True
#             else:
#                 return False
#
#     def parseInput(self, userInputList):


class WeightField:
    def __init__(self, name, label="Weight in kg:", errorMsg="Invalid Weight! Must not have units.", required=False):
        self = Field(name, validator_collection.is_numeric, errorMsg=errorMsg, label=label, required=required)


class LengthField:
    def __init__(self, name, label="Length in cm:", errorMsg="Invalid Length! Must not have units.", required=False):
        self = Field(name, validator_collection.is_numeric, errorMsg=errorMsg, label=label, require=required)
