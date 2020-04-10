Schema = {
    "name": {
        "type": "text",
        "label": "Field Name",
        "required": True
    },
    "label": {
        "type": "text",
        "label": "Field Label",
        "required": True
    },
    "type": {
        "type": "select",
        "options": [
            "text",
            "textarea",
            "boolean",
            "select"
        ],
        "label": "Field Type",
        "required": True
    },
    "required": {
        "type": "boolean",
        "label": "Field Required?",
    }
}
