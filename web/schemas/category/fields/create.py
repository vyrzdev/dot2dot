Schema = {
    "name": {
        "type": "text",
        "label": "Field Name",
        "required": True
    },
    "fieldType": {
        "type": "select",
        "options": [
            "text",
            "textarea",
            "boolean",
            "select"
        ],
        "label": "Field Type",
        "required": True
    }
}
FinalizeSchemas = {
    "text": {
        "details__required": {
            "type": "boolean",
            "label": "Field Required?"
        },
        "details__label": {
            "type": "text",
            "label": "Field Label",
            "required": True
        }
    },
    "textarea": {
        "details__required": {
            "type": "boolean",
            "label": "Field Required?"
        },
        "details__label": {
            "type": "text",
            "label": "Field Label",
            "required": True
        }
    },
    "boolean": {
        "details__label": {
            "type": "text",
            "label": "Field Label",
            "required": True
        }
    },
    "select": {
        "details__required": {
            "type": "boolean",
            "label": "Field Required?"
        },
        "details__label": {
            "type": "text",
            "label": "Field Label",
            "required": True
        },
        "details__options": {
            "type": "list",
            "label": "Options ~ (A comma sepererated list like: option1, option2, option3",
            "required": True,
        },
        "details__allowMultiple": {
            "type": "boolean",
            "label": "Allow Multiple Selections?"
        }
    }
}
