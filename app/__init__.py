import os

from app import config

# FLASK
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_object(config)

db = SQLAlchemy(app)
db.init_app(app)

def __init__():
    if app.config['ENV'] == 'stage':
        # Clear any existing articles, reset dbase sequence counter to 1
        try:
            Article.query().delete()
            if Article.query.count() == 0:
                db.session.execute('ALTER SEQUENCE articles_id_seq RESTART WITH 1;')
            db.session.commit()
        except:
            db.session.rollback()

    try:
        retrieve()
    except:
        raise
    print(" * Initial retrieval complete, ready to serve requests")

#------------------------------------------------------------------------------
# Avoid circular imports
#------------------------------------------------------------------------------
from app.models import Article

from app.jobs.horse import retrieve

from app import views
#------------------------------------------------------------------------------
