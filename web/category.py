from . import app, schemas
from flask import redirect


@app.route("/category")
def categoryRedirect():
    return redirect("/category/view")


@app.route("/category/create", methods=["GET", "POST"])
def categoryCreate():
    resourceSchema = schemas.resourceSchemas.Schema.get("category")
    if resourceSchema is None:
        return "UhOh! Your category schema is missing, we need this to understand what a category is!"