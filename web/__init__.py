from ..database import models
from flask import Flask

app = Flask(__name__)

app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True

from . import routes
