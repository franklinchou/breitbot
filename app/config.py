import os

basepath = os.path.dirname(__file__)
raw_data_path = os.path.join(basepath, 'raw')
article_listing = os.path.join(raw_data_path, 'articles.dir')

if os.environ['ENV'] == 'dev':
    DEBUG = True

SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL'].strip('\'')

