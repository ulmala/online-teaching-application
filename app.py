from os import getenv
from flask import Flask

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.config["MAX_CONTENT_LENGTH"] = int(getenv("MAX_CONTENT_LENGTH"))

import routes