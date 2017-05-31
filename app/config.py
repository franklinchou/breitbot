# /breitbot/app/config.py

import os

ENV = os.environ['ENV'].strip('\'')

if ENV == 'dev':
    DEBUG = True

if ENV == 'prod':
    base_path = os.path.expanduser("~")
    bin_path = os.path.join(base_path, 'bin')
    engine = os.path.join(binpath, 'wkhtmltopdf')
    if os.path.isfile(engine):
        print(" >>> WKHTMLTOPDF ENGINE DETECTED")
        PDF_ENGINE = engine

SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL'].strip('\'')

SQLALCHEMY_TRACK_MODIFICATIONS = False

#------------------------------------------------------------------------------
# AWS Keys (for serving static files)
#------------------------------------------------------------------------------
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID'].strip('\'')
AWS_SECRET_KEY = os.environ['AWS_SECRET_KEY'].strip('\'')
S3_BUCKET = os.environ['S3_BUCKET'].strip('\'')
