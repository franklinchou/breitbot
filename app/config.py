# /breitbot/app/config.py

import os

basepath = os.path.relpath(os.path.dirname(os.path.dirname(__file__)))
raw_data_path = os.path.join(basepath, 'static', 'raw')

if os.environ['ENV'].strip('\'') == 'dev':
    DEBUG = True

SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL'].strip('\'')

SQLALCHEMY_TRACK_MODIFICATIONS = False
