from .. import models
Schema = {
    "field": {
        "meta": {
            "name": "field",
            "label": "Field",
            "endpoint": "/field",
            "redirect": "/field/view",
            "dbModel": models.fieldStore,
        },
        "actions": [
            {
                "name": "create",
                "label": "Create",
                "scope": "class",
                "function": "create",
                "stages": 2
            },
            {
                "name": "edit",
                "label": "Edit",
                "scope": "object",
                "function": "edit"
            },
            {
                "name": "view",
                "label": "View",
                "scope": "dynamic",
                "function": "view"
            }
        ],
        "stages": {
            1: {
                "name": "Stage 1",
                "dependent_field": None,
                "fields": [
                    {
                        "name": "name",
                        "label": "Field Name",
                        "type": "text",
                        "required": True,
                        "protected": False,
                        "overview": True
                    },
                    {
                        "name": "fieldType",
                        "label": "Field Type",
                        "type": "select",
                        "required": True,
                        "protected": True,
                        "overview": True
                    },
                ]
            },
            2: {
                "name": "Stage 2",
                "dependent_field": "fieldType",
                "fields": [
                    {
                        "name": "required",
                        "label": "Field Required?",
                        "type": "boolean",
                        "protected": False,
                        "overview": True,
                        "dependent": ["text", "textarea", "select"]
                    }
                ]
            }
        }
    },
    "category": {
        "meta": {
            "name": "category",
            "label": "Category",
            "endpoint": "/category",
            "redirect": "/category/view",
            "dbModel": models.category,
        },
        "actions": [
            {
                "name": "create",
                "label": "Create",
                "scope": "class",
                "function": "create",
                "stages": 1
            },
            {
                "name": "edit",
                "label": "Edit",
                "scope": "object",
                "function": "edit",
            },
            {
                "name": "view",
                "label": "View",
                "scope": "dynamic",
                "function": "view"
            }
        ],
        "stages": {
            1: {
                "name": "Stage 1",
                "dependent_field": None,
                "fields": [
                    {
                        "name": "name",
                        "label": "Category Name",
                        "type": "text",
                        "required": True,
                        "protected": False,
                        "overview": True
                    },
                    {
                        "name": "description",
                        "label": "Category Description",
                        "type": "textarea",
                        "required": False,
                        "protected": False,
                        "overview": False
                    }
                ]
            },
        }
    },
}