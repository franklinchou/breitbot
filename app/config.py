# /breitbot/app/config.py

import os

ENV = os.environ['ENV'].strip('\'')

if ENV == 'dev':
    DEBUG = True
    basepath = os.path.dirname(os.path.dirname(__file__))

if ENV == 'prod':
    basepath = os.path.expanduser("~")

raw_data_path = os.path.join(basepath, 'raw')

SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL'].strip('\'')

SQLALCHEMY_TRACK_MODIFICATIONS = False

#------------------------------------------------------------------------------
# AWS Keys (for serving static files)
#------------------------------------------------------------------------------
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID'].strip('\'')
AWS_SECRET_KEY = os.environ['AWS_SECRET_KEY'].strip('\'')
S3_BUCKET = os.environ['S3_BUCKET'].strip('\'')
