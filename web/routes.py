from . import app, models, fields, form
from flask import request, jsonify, redirect


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


@app.route("/manufacturer/create", methods=["GET", "POST"])
def createManufacturer():
    newManufacturer = models.manufacturer()
    createManufacturerForm = form.Form("/manufacturer/create", "post", fields=[
        fields.Field("name", label="Manufacturer Name", required=True),
    ])
    if request.method == "POST":
        response = request.form
        jsonResponse = createManufacturerForm.parseResponse(response)
        if jsonResponse["valid"]:
            newManufacturer.name = jsonResponse["values"]["name"]
            newManufacturer.save()
            return redirect(f"/manufacturer/view/{newManufacturer.iterID}")
        else:
            return "Invalid JSON"
        return jsonify(jsonResponse)
    elif request.method == "GET":
        return createManufacturerForm.render()
    else:
        return "Invalid Method! This endpoint only supports GET & POST"


@app.route("/manufacturer/view/<objID>")
def viewManufacturer(objID):
    return models.manufacturer.objects(iterID=objID).first().to_json()
