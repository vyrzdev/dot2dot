Schema = {
    "name": {
        "type": "text",
        "label": "Manufacturer Name",
        "required": True
    },
    "contactInfo__tel": {
        "type": "text",
        "label": "Contact Phone",
        "required": False
    },
    "contactInfo__email": {
        "type": "text",
        "label": "Contact Email",
        "required": False
    },
    "contactInfo__valid": {
        "type": "boolean",
        "label": "Is this data valid?",
    }
}
