import os

# FLASK
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.horse import retrieve

import app.config

#------------------------------------------------------------------------------
# SET APPLICATION VARS
#------------------------------------------------------------------------------

app = Flask(__name__)
app.config.from_object(config)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from app.models import Article

#------------------------------------------------------------------------------

def __init__():

    # make necessary directories
    if not os.path.exists(config.raw_data_path):
        os.makedirs(config.raw_data_path, exist_ok=True)

    # create initial articles listing
    # retrieve()

