from flask import Flask
from ohayodash.base import base

app = Flask(__name__)
app.register_blueprint(base)
