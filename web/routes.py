from . import app, models, form, formschemas
from flask import request, jsonify, redirect, abort

##################
# Testing Routes #
##################

# Test form generation...
@app.route("/test", methods=["GET", "POST"])
def test():
    form1 = form.Form("/test", "post")
    print("TRACE!")
    form1.buildFromSchema()
    if request.method == "POST":
        jsonResponse = form1.parseResponse(request.form)
        return jsonify(jsonResponse)
    elif request.method == "GET":
        return form1.render()
    else:
        return "This Endpoint only supports GET and POST..."

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
            # Fuck off. How tf did you break this shit?
            return str(jsonResponse)
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


################
# Error Routes #
################

# 404 Error
@app.errorhandler(404)
def Four_0_Four(error):
    return "Error! 404 Page not found... Ths page/feature either doesn't exist yet or at all."
