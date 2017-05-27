from app import db

# Procedure for resetting alembic and creating new migrations
# 1. Delete migrations
# 2. At psql prompt issue: `DROP TABLE alembic_version;`
# 3. Re-initialize dbase

class Article(db.Model):

    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    raw_url = db.Column(db.String(), unique=True)
    headline = db.Column(db.String())

    # publication date
    publish_date = db.Column(db.Date())

    # 27 May 2017
    # `raw_url` won't be determined until the object is created
    def __init__(self, headline, publish_date):
        # self.raw_url = raw_url
        self.headline = headline
        self.publish_date = publish_date

    def __repr__(self):
        return '<id {}> {}'.format(self.id, self.headline)
