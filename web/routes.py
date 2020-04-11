from . import app, models, form, formschemas
from flask import request, jsonify, redirect, abort


from flask.json import JSONEncoder
from bson import json_util
from mongoengine.base import BaseDocument
from mongoengine.queryset.base import BaseQuerySet


class MongoEngineJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, BaseDocument):
            return json_util._json_convert(obj.to_mongo())
        elif isinstance(obj, BaseQuerySet):
            return json_util._json_convert(obj.as_pymongo())
        return JSONEncoder.default(self, obj)


##################
# Testing Routes #
##################


# Test form generation...
@app.route("/test-form-generation", methods=["GET", "POST"])
def test():
    form1 = form.Form("/test", "post")
    Schema = {
        "name": {
            "type": "text",
            "label": "Name",
            "required": True
        },
        "description": {
            "type": "textarea",
            "label": "Description",
            "required": True
        },
        "boolean_test": {
            "type": "boolean",
            "label": "Boolean Test",
        },
        "select_test": {
            "type": "select",
            "label": "Select Test",
            "required": True,
            "options": ["op1", "op2", "op3"],
            "allowMultiple": True
        }
    }
    form1.buildFromSchema(Schema)
    if request.method == "POST":
        jsonResponse = form1.parseResponse(request.form)
        return jsonify(jsonResponse)
    else:
        return form1.render()


@app.route("/test-schema-generation", methods=["GET", "POST"])
def testSchemaGeneration():
    fieldList = [models.fieldStore(name="Epic", type="text", details={"label": "Epic",
                                                                      "required": False}
                                   ),
                 models.fieldStore(name="Select Test", type="select", details={"label": "Select Test",
                                                                               "required": True,
                                                                               "options": ["op1", "op2", "op3", "op4"],
                                                                               "allowMultiple": False
                                                                               }
                                   )
                ]
    Schema = {}
    for fieldStore in fieldList:
        Schema = {**Schema, **fieldStore.Schema()}
    newForm = form.Form("/test-schema-generation", "post")
    newForm.buildFromSchema(Schema)
    if request.method == "POST":
        jsonResponse = newForm.parseResponse(request.form)
        return jsonify(jsonResponse)
    else:
        return newForm.render()


@app.route("/test-multistep-form-step1", methods=["GET", "POST"])
def testMultiStepFormStep1():
    Schema = {
        "selection": {
            "label": "Epic Select",
            "type": "select",
            "required": True,
            "options": ["foo", "foo2"],
        }
    }
    step1 = form.Form("/test-multistep-form-step1", "post")
    step1.buildFromSchema(Schema)
    if request.method == "POST":
        jsonResponse = step1.parseResponse(request.form)
        if jsonResponse.get("valid"):
            selection = jsonResponse.get("values").get("selection")
            return redirect(f"/test-multistep-form-step2/{selection}")
        else:
            step1.addErrorMessages(jsonResponse.get("errors"))
            return step1.render()
    else:
        return step1.render()


@app.route("/test-multistep-form-step2/<foo>")
def testMultiStepFormStep2(foo):
    schemaLookup = {
        "foo": {
            "thingy": {
                "label": "Thingy 1",
                "type": "text",
                "required": False
            }
        },
        "foo2": {
            "thingy2": {
                "label": "Thingy 2",
                "type": "text",
                "required": False
            }
        }
    }
    step2 = form.Form("/test-multistep-form-step2/<foo>", "post")
    step2.buildFromSchema(schemaLookup.get(foo))
    if request.method == "POST":
        return "Only a test buddy"
    else:
        return step2.render()

#######################
# Manufacturer Routes #
#######################


# Create A Manufacturer
@app.route("/manufacturer/create", methods=["GET", "POST"])
def createManufacturer():
    createManufacturerForm = form.Form("/manufacturer/create", "post")
    createManufacturerForm.buildFromSchema(formschemas.manufacturer.create.Schema)

    if request.method == "POST":
        # Get the form data
        response = request.form
        # Pass into the forms bespoke parser.
        jsonResponse = createManufacturerForm.parseResponse(response)
        # Get a JSON response. As defined in form.py.
        if jsonResponse["valid"]:
            newManufacturer = models.manufacturer()
            newManufacturer.save()
            newManufacturer.update(**jsonResponse["values"])
            # Send them to the new manufacturer page, iterID is the primary key, and is assigned by sequenceField.
            return redirect(f"/manufacturer/view/{newManufacturer.iterID}")
        else:
            createManufacturerForm.addErrorMessages(jsonResponse["errors"])
            return createManufacturerForm.render()
    # Send the forms HTML.
    elif request.method == "GET":
        return createManufacturerForm.render()
    # They using PUT or some shit?!
    else:
        return "Invalid Method! This endpoint only supports GET & POST"


@app.route("/manufacturer/edit/<objID>", methods=["GET", "POST"])
def editManufacturer(objID):
    # Fetch Manufacturer Object, See if it exists.
    requestedManufacturer = models.manufacturer.objects(iterID=objID).first()
    if requestedManufacturer is None:
        abort(404)

    editManufacturerForm = form.Form(f"/manufacturer/edit/{objID}", "post")
    editManufacturerForm.buildFromSchema(formschemas.manufacturer.edit.Schema)
    editManufacturerForm.addDefaultValues(requestedManufacturer)

    if request.method == "POST":
        jsonResponse = editManufacturerForm.parseResponse(request.form)
        if jsonResponse["valid"]:
            requestedManufacturer.update(**jsonResponse["values"])
            return redirect(f"/manufacturer/view/{requestedManufacturer.iterID}")
        else:
            return request.form.to_dict()
    elif request.method == "GET":
        return editManufacturerForm.render()
    else:
        return "Invalid Method! This endpoint only supports GET & POST"


# View A Specific Manufacturer
# Not worthy of comment.
@app.route("/manufacturer/view/<objID>")
def viewManufacturer(objID):
    requestedManufacturer = models.manufacturer.objects(iterID=objID).first()
    if requestedManufacturer is None:
        abort(404)
    else:
        return jsonify(requestedManufacturer.to_mongo().to_dict())


###################
# Category Routes #
###################

@app.route("/category/create", methods=["GET", "POST"])
def createCategory():
    createCategoryForm = form.Form("/category/create", "post")
    createCategoryForm.buildFromSchema(formschemas.category.create.Schema)
    if request.method == "POST":
        # Get the form data
        response = request.form
        jsonResponse = createCategoryForm.parseResponse(response)
        # Get a JSON response. As defined in form.py.
        if jsonResponse["valid"]:
            newCategory = models.category(**jsonResponse["values"])
            newCategory.save()
            # Send them to the new manufacturer page, iterID is the primary key, and is assigned by sequenceField.
            return redirect(f"/category/view/{newCategory.id}")
        else:
            createCategoryForm.addErrorMessages(jsonResponse["errors"])
            return createCategoryForm.render()
        # Send the forms HTML.
    else:
        return createCategoryForm.render()


@app.route("/category/edit/<objID>", methods=["GET", "POST"])
def editCategory(objID):
    # Fetch Manufacturer Object, See if it exists.
    requestedCategory = models.category.objects(id=objID).first()
    if requestedCategory is None:
        abort(404)

    editCategoryForm = form.Form(f"/manufacturer/edit/{objID}", "post")
    editCategoryForm.buildFromSchema(formschemas.category.edit.Schema)
    editCategoryForm.addDefaultValues(requestedCategory)

    if request.method == "POST":
        # Get the form data
        response = request.form
        jsonResponse = editCategoryForm.parseResponse(response)
        # Get a JSON response. As defined in form.py.
        if jsonResponse["valid"]:
            requestedCategory.update(**jsonResponse["values"])
            # Send them to the new manufacturer page, iterID is the primary key, and is assigned by sequenceField.
            return redirect(f"/category/view/{requestedCategory.id}")
        else:
            editCategoryForm.addErrorMessages(jsonResponse["errors"])
            return editCategoryForm.render()
        # Send the forms HTML.
    else:
        return editCategoryForm.render()


@app.route("/category/view/<objID>")
def viewCategory(objID):
    requestedCategory = models.category.objects(id=objID).first()
    print(requestedCategory)
    if requestedCategory is None:
        abort(404)
    else:
        return MongoEngineJSONEncoder().encode(requestedCategory)


#########################
# Category Field Routes #
#########################


@app.route("/category/fields/<objID>/create", methods=["POST", "GET"])
def createCategoryField(objID):
    requestedCategory = models.category.objects(id=objID).first()
    if requestedCategory is None:
        abort(404)

    createCategoryFieldForm = form.Form(f"/category/fields/{objID}/create", "post")
    createCategoryFieldForm.buildFromSchema(formschemas.category.fields.create.Schema)
    if request.method == "POST":
        jsonResponse = createCategoryFieldForm.parseResponse(request.form)
        if jsonResponse.get("valid"):
            newField = models.fieldStore(category=requestedCategory)
            newField.save()
            newField.update(**jsonResponse.get("values"))
            return redirect(f"/category/fields/{objID}/view")
        else:
            createCategoryFieldForm.addErrorMessages(jsonResponse.get("errors"))
            return createCategoryFieldForm.render()
    else:
        return createCategoryFieldForm.render()

@app.route("/category/fields/<catID>/finalize/<fieldID>", methods=["GET", "POST"])
def finalizeCategoryField(catID, fieldID):
    requestedCategory = None  # Potentially may be used at a later date.
    requestedField = models.fieldStore.objects(id=fieldID).first()
    if requestedField is None:
        abort(404)
    elif requestedField.metaData.get("finalized"):
        return "Product already finalized!"
    # TODO: Finish this method according two stage policy..


@app.route("/category/fields/<catID>/edit/<fieldID>", methods=["GET", "POST"])
def editCategoryField(catID, fieldID):
    requestedCategory = None  # Potentially may be used at a later date.
    requestedField = models.fieldStore.objects(id=fieldID).first()
    if requestedField is None:
        abort(404)

    editCategoryFieldForm = form.Form(f"/category/fields/{catID}/edit/{fieldID}")
    editCategoryFieldForm.buildFromSchema(formschemas.category.fields.edit.Schema)
    editCategoryFieldForm.addDefaultValues(requestedField)
    if request.method == "POST":
        jsonResponse = editCategoryFieldForm.parseResponse(request.form)
        if jsonResponse.get("valid"):
            requestedField.update(**jsonResponse.get("values"))
            return redirect(f"/category/fields/{catID}/view")
        else:
            editCategoryFieldForm.addErrorMessages(jsonResponse.get("errors"))
            return editCategoryFieldForm.render()
    else:
        return editCategoryFieldForm.render()


################
# Error Routes #
################

# 404 Error
@app.errorhandler(404)
def Four_0_Four(error):
    return "Error! 404 Page not found... Ths page/feature either doesn't exist yet or at all."
