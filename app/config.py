# /breitbot/app/config.py

import os

if os.environ['ENV'].strip('\'') == 'dev':
    DEBUG = True
    basepath = os.path.dirname(os.path.dirname(__file__))

if os.environ['ENV'].strip('\'') == 'prod':
    from os.path import expanduser
    basepath = expanduser("~")

raw_data_path = os.path.join(basepath, 'raw')

if not os.path.exists(raw_data_path):
    os.makedirs(raw_data_path, exist_ok=True)

SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL'].strip('\'')

SQLALCHEMY_TRACK_MODIFICATIONS = False

#------------------------------------------------------------------------------
# AWS Keys (for serving static files)
#------------------------------------------------------------------------------
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID'].strip('\'')
AWS_SECRET_KEY = os.environ['AWS_SECRET_KEY'].strip('\'')
S3_BUCKET = os.environ['S3_BUCKET'].strip('\'')
