from . import app, models, fields, forms
from flask import request

@app.route("/test")
def test():
    field = fields.Field("Epic")
    form = forms.Form()
    form.addField(field)
    return form.render("/test/submit")

@app.route("/test/submit", methods=["GET", "POST"])
def submit():
    return request.form.to_dict()
