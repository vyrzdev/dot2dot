from .. import models
Schema = {
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
                "stages": 2
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
                "endpoint": "/category/view",
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
            2: {
                "name": "Stage 2",
                "dependent_field": "name",
                "fields": [
                    {
                        "name": "metaData__epic",
                        "label": "Epic",
                        "type": "text",
                        "required": True,
                        "dependent": "Epic",
                        "protected": False,
                        "overview": False
                    }
                ]
            }
        }
    },
}