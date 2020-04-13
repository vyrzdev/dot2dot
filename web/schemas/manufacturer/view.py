Schema = {
    "resourceDetails": {
        "name": "manufacturer",
        "title": "Manufacturer",
        "endpoint": "/manufacturer"
    },
    "resourceActions": [
        {
            "name": "create",
            "title": "Create New",
            "endpoint": "/create"
        },
        {
            "name": "drop",
            "title": "Delete All",
            "endpoint": "/drop"
        }
    ],
    "resultActions": [
        {
            "name": "edit",
            "title": "Edit",
            "endpoint": "/edit/{{ objID }}"
        },
        {
            "name": "view",
            "title": "View",
            "endpoint": "/view/{{ objID }}"
        }
    ]
}