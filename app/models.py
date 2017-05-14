from app import db

class Article(db.Model):

    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    raw_url = db.Column(db.String(), unique=True)
    title = db.Column(db.String())

    # publication date
    publish_date = db.Column(db.Date())

    def __repr__(self):
        return '<id {}> {}'.format(id, title)
