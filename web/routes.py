from . import app, models, fields, form
from flask import request, jsonify, redirect, abort

##################
# Testing Routes #
##################

# Test form generation...
@app.route("/test", methods=["GET", "POST"])
def test():
    form1 = form.Form("/test", "post", fields=[
        fields.Field("Epic"),
        fields.SelectField("test", ["op1", "op2", "op3"], label="Test SelectField", required=True)
    ])
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
    # Create a new manufacturer object, this is to show the prefix ahead of time?
    # Potentially unecessary.
    # No actually, definitely unecessary...
    # Do I change it?
    # Nah.
    newManufacturer = models.manufacturer()
    # Define the form.
    createManufacturerForm = form.Form("/manufacturer/create", "post", fields=[
        fields.Field("name", label="Manufacturer Name", required=True),
    ])
    if request.method == "POST":
        # Get the form data
        response = request.form
        # Pass into the forms bespoke parser.
        jsonResponse = createManufacturerForm.parseResponse(response)
        # Get a JSON response. As defined in form.py.
        if jsonResponse["valid"]:
            newManufacturer.name = jsonResponse["values"]["name"]
            newManufacturer.save()
            # Send them to the new manufacturer page, iterID is the promary key, and is assigned by sequenceField.
            return redirect(f"/manufacturer/view/{newManufacturer.iterID}")
        else:
            # Fuck off. How tf did you break this shit?
            return "Invalid JSON"
    # Send the forms HTML.
    elif request.method == "GET":
        return createManufacturerForm.render()
    # They using PUT or some shit?!
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
        return requestedManufacturer.to_json()


################
# Error Routes #
################

# 404 Error
@app.errorhandler(404)
def Four_0_Four(error):
    return "Error! 404 Page not found... Ths page/feature either doesn't exist yet or at all."
