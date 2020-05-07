from . import app, models, form, schemas
from flask import request, jsonify, redirect, abort, render_template

from flask.json import JSONEncoder
from bson import json_util
from mongoengine.base import BaseDocument
from mongoengine.queryset.base import BaseQuerySet

# APISchemas = schemas.apis.Schemas


class MongoEngineJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, BaseDocument):
            return json_util._json_convert(obj.to_mongo())
        elif isinstance(obj, BaseQuerySet):
            return json_util._json_convert(obj.as_pymongo())
        return JSONEncoder.default(self, obj)


def paginate(resource, items_per_page=10, page_number=1):
    offset = (page_number - 1) * items_per_page

    paginatedResults = resource.objects.skip(offset).limit(items_per_page)
    return paginatedResults


def getFieldValue(fieldObject, fieldName):
    objectDict = fieldObject.to_mongo().to_dict()
    if "__" in fieldName:
        path = fieldName.split("__")
        current = objectDict
        for pathElement in path:
            current = current.get(pathElement)
        return current
    else:
        return objectDict.get(fieldName)


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


# View all manufacturers (Paginated)
@app.route("/manufacturer/view")
def viewManufacturers():
    currentPage = request.args.get("page")
    if currentPage is None: currentPage = 1
    try:
        currentPage = int(currentPage)
    except ValueError:
        return "Invalid Page Number!"
    pageResults = paginate(models.manufacturer, page_number=currentPage)
    return render_template("view", currentPage=currentPage, resource="manufacturer", action="view", results=pageResults)


# Create A Manufacturer
@app.route("/manufacturer/create", methods=["GET", "POST"])
def createManufacturer():
    createManufacturerForm = form.Form("/manufacturer/create", "post")
    createManufacturerForm.buildFromSchema(schemas.manufacturer.create.Schema)

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
    editManufacturerForm.buildFromSchema(schemas.manufacturer.edit.Schema)
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
@app.route("/category")
def categoryRedirect():
    return redirect("/category/view")


@app.route("/category/<action>", methods=["GET", "POST"])
def categoryRoute(action):
    resourceSchema = schemas.resourceSchemas.Schema.get("category")
    if resourceSchema is None:
        return "Oops! This resources schema appears not to exist!"
    for actionJSON in resourceSchema.get("actions"):
        if action == actionJSON.get("name"):
            if actionJSON.get("function") == "create":
                # Get the current stage from GET parameters.
                stage = request.args.get("stage")
                # If the parameter is not specified, stage must be 1.
                if stage is None: stage = 1
                # Try and convert stage to an integer...
                # It must be possible otherwise it is invalid
                try:
                    stage = int(stage)
                except ValueError:
                    return "Invalid Stage Number!"
                if stage > actionJSON.get("stages"):
                    return "Invalid Stage Number!"
                if request.method == "GET":
                    if stage == 1:
                        createForm = form.Form("/category/create?stage=1", "post")
                        Schema = resourceSchema.get("stages").get(1).get("fields")
                        createForm.buildFromSchema(Schema)
                        return createForm.render()
                    else:
                        targetObjectID = request.args.get("target")
                        if targetObjectID is None: abort(404)
                        targetObject = resourceSchema.get("meta").get("dbModel").objects(id=targetObjectID).first()
                        if targetObject is None: abort(404)

                        createForm = form.Form(f"/category/create?stage={stage}&target={targetObjectID}", "post")
                        dependentFieldName = resourceSchema.get("stages").get(stage).get("dependent_field")
                        if dependentFieldName is None:
                            Schema = resourceSchema.get("stages").get(stage).get("fields")
                        else:
                            Schema = list()
                        dependentValue = getFieldValue(targetObject, dependentFieldName)
                        for field in resourceSchema.get("stages").get(stage).get("fields"):
                            if field.get("dependent") == dependentValue:
                                Schema.append(field)
                            else:
                                pass
                        createForm.buildFromSchema(Schema)
                        return createForm.render()

                else:
                    if stage == 1:
                        createForm = form.Form("/category/create?stage=1", "post")
                        Schema = resourceSchema.get("stages").get(1).get("fields")
                        createForm.buildFromSchema(Schema)
                        jsonResponse = createForm.parseResponse(request.form)
                        targetObject = resourceSchema.get("meta").get("dbModel")()
                    else:
                        targetObjectID = request.args.get("target")
                        if targetObjectID is None: abort(404)
                        targetObject = resourceSchema.get("meta").get("dbModel").objects(id=targetObjectID).first()
                        if targetObject is None: abort(404)

                        createForm = form.Form(f"/category/create?stage={stage}&target={targetObjectID}", "post")
                        dependentFieldName = resourceSchema.get("stages").get(stage).get("dependent_field")
                        if dependentFieldName is None:
                            Schema = resourceSchema.get("stages").get(stage).get("fields")
                        else:
                            Schema = list()
                            dependentValue = getFieldValue(targetObject, dependentFieldName)
                            for field in resourceSchema.get("stages").get(stage).get("fields"):
                                if field.get("dependent") == dependentValue:
                                    Schema.append(field)
                                else:
                                    pass
                        createForm.buildFromSchema(Schema)
                        jsonResponse = createForm.parseResponse(request.form)

                    if jsonResponse.get("valid"):
                        targetObject.save()

                        if stage == actionJSON.get("stages"):
                            jsonResponse["values"] = {**jsonResponse.get("values"), "metaData__finalized": True}
                            redirectURL = f"/category/view?target={targetObject.id}"
                        else:
                            jsonResponse["values"] = {**jsonResponse.get("values"), "metaData__finalized": False}
                            redirectURL = f"/category/create?stage={stage + 1}&target={targetObject.id}"

                        targetObject.update(**jsonResponse.get("values"))
                        return redirect(redirectURL)
                    else:
                        createForm.addErrorMessages(jsonResponse.get("errors"))
                        return createForm.render()

            elif actionJSON.get("function") == "edit":
                targetObjectID = request.args.get("target")
                if targetObjectID is None: abort(404)
                targetObject = resourceSchema.get("meta").get("dbModel").objects(id=targetObjectID).first()
                if targetObject is None: abort(404)

                editForm = form.Form(f"/category/edit?target={targetObjectID}", "post")
                Schema = list()
                for stage in resourceSchema.get("stages").values():
                    for field in stage.get("fields"):
                        if field.get("protected"):
                            pass
                        else:
                            Schema.append(field)
                editForm.buildFromSchema(Schema)
                editForm.addDefaultValues(targetObject)

                if request.method == "GET":
                    return editForm.render()
                else:
                    jsonResponse = editForm.parseResponse(request.form)

                    if jsonResponse.get("valid"):
                        targetObject.update(**jsonResponse.get("values"))
                        return redirect(f"/category/view?{targetObjectID}")
                    else:
                        editForm.addErrorMessages(jsonResponse.get("errors"))
                        return editForm.render()

            elif actionJSON.get("function") == "view":
                # Get the target object ID, if it doesnt exist, obviously view all items.
                targetObjectID = request.args.get("target")
                if targetObjectID is None:
                    currentPage = request.args.get("page")
                    if currentPage is None: currentPage = 1
                    try:
                        currentPage = int(currentPage)
                    except ValueError:
                        return "Invalid Page Number!"
                    pageResults = paginate(resourceSchema.get("meta").get("dbModel"), page_number=currentPage)
                    return render_template("view", schema=resourceSchema, results=pageResults, currentPage=currentPage, action="view")
                else:
                    # Query target
                    targetObject = resourceSchema.get("meta").get("dbModel").objects(id=targetObjectID).first()
                    if targetObject is None:
                        abort(404)
                    else:
                        return MongoEngineJSONEncoder().encode(targetObject)
        else:
            pass

    return "Oops! Invalid Action!"


#########################
# Category Field Routes #
#########################

@app.route("/category/fields/<objID>/create", methods=["POST", "GET"])
def createCategoryField(objID):
    requestedCategory = models.category.objects(id=objID).first()
    if requestedCategory is None:
        abort(404)

    createCategoryFieldForm = form.Form(f"/category/fields/{objID}/create", "post")
    createCategoryFieldForm.buildFromSchema(schemas.category.fields.create.Schema)
    if request.method == "POST":
        jsonResponse = createCategoryFieldForm.parseResponse(request.form)
        if jsonResponse.get("valid"):
            newField = models.fieldStore(category=requestedCategory)
            newField.save()
            newField.update(**jsonResponse.get("values"))
            return redirect(f"/category/fields/{objID}/finalize/{newField.id}")
        else:
            createCategoryFieldForm.addErrorMessages(jsonResponse.get("errors"))
            return createCategoryFieldForm.render()
    else:
        return createCategoryFieldForm.render()


@app.route("/category/fields/<catID>/finalize/<fieldID>", methods=["GET", "POST"])
def finalizeCategoryField(catID, fieldID):
    requestedField = models.fieldStore.objects(id=fieldID).first()
    if requestedField is None:
        abort(404)
    elif requestedField.metaData.get("finalized"):
        return "Product already finalized!"
    Schema = schemas.category.fields.create.FinalizeSchemas.get(requestedField.fieldType)
    finalizeCategoryFieldForm = form.Form(f"/category/fields/{catID}/finalize/{fieldID}", "post")
    finalizeCategoryFieldForm.buildFromSchema(Schema)

    if request.method == "POST":
        jsonResponse = finalizeCategoryFieldForm.parseResponse(request.form)
        if jsonResponse.get("valid"):
            requestedField.update(**jsonResponse.get("values"))
            requestedField.update(**{"metaData__finalized": True})
            return redirect(f"/category/fields/{catID}/view")
        else:
            finalizeCategoryFieldForm.addErrorMessages(jsonResponse.get("errors"))
            return finalizeCategoryFieldForm.render()
    else:
        return finalizeCategoryFieldForm.render()


@app.route("/category/fields/<catID>/edit/<fieldID>", methods=["GET", "POST"])
def editCategoryField(catID, fieldID):
    requestedField = models.fieldStore.objects(id=fieldID).first()
    if requestedField is None:
        abort(404)

    Schema = {**schemas.category.fields.edit.Schema, **schemas.category.fields.edit.typeSpecific.get(requestedField.fieldType)}
    editCategoryFieldForm = form.Form(f"/category/fields/{catID}/edit/{fieldID}", "post")
    editCategoryFieldForm.buildFromSchema(Schema)
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
    return f"Error! 404 Page not found... Ths page/feature either doesn't exist yet or at all.\n {error}"
