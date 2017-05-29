import os

# FLASK
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app import config

app = Flask(__name__)

app.config.from_object(config)

db = SQLAlchemy(app)
db.init_app(app)

#------------------------------------------------------------------------------
# Avoid circular imports
#------------------------------------------------------------------------------

from app.models import Article

from app.jobs.horse import retrieve

from app import views

#------------------------------------------------------------------------------

retrieve(first_call=True)

print(" * Initial retrieval complete, ready to serve requests")
