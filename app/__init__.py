import os

from app.config import raw_data_path

# FLASK
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

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

_prepare()

def _prepare():

    # Create raw data path
    if not os.path.exists(raw_data_path):
        os.makedirs(raw_data_path, exist_ok=True)

    # retrieve()

    # print(" * Initial retrieval complete, ready to serve requests")
