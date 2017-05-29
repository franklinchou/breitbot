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

def __init__():

    # make necessary directories
    if not os.path.exists(config.raw_data_path):
        os.makedirs(config.raw_data_path, exist_ok=True)

    # create initial articles listing
    retrieve(first_call=True)

    print(" * Initial retrieval complete, ready to serve requests")
