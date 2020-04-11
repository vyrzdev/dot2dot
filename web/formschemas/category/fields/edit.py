Schema = {
    "name": {
        "type": "text",
        "label": "Field Name",
        "required": True
    },
    "details__label": {
        "type": "text",
        "label": "Field Label",
        "required": True
    },
    # Removed Type Option ~ Since changing type is a bad idea.
    "details__required": {
        "type": "boolean",
        "label": "Field Required? (Editing is potentially risky, as existing products wont have this info!)",
    }
}
