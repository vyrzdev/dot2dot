from ..database import models
from flask import Flask

app = Flask(__name__)

from . import routes
