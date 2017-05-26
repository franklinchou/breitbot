#------------------------------------------------------------------------------
#
# app/jobs/horse.py
#
# This is where all the magic happens.
#
# 14 May 2017
# Remove reliance on a text doc as temporary storage.
# Write all article extractions, including initiation, to database.
#
#------------------------------------------------------------------------------

__author__ = 'Franklin Chou'

import os
import re

if __name__ != "__main__":
    from app import db
    from app.config import raw_data_path
    from app.models import Article as Article_Entry
else:
    raw_data_path = os.path.join(os.path.dirname(__file__), 'test')

from datetime import date,\
    datetime

from sqlalchemy.exc import IntegrityError

#------------------------------------------------------------------------------
# html/xml parsing
#------------------------------------------------------------------------------
import lxml.html
from lxml import etree

#------------------------------------------------------------------------------
# pdf generation imports
#------------------------------------------------------------------------------
import pdfkit

#------------------------------------------------------------------------------
# celery
#------------------------------------------------------------------------------
from celery import Celery
celery = Celery(__name__, broker='redis://localhost:6379/0')
celery.config_from_object('app.celery_config')
#------------------------------------------------------------------------------

base_url = 'http://www.breitbart.com'

class Article:
    def __init__(self, raw_article_xml):

        # Extract the publish date from the article url

        # 14 May 2017
        # If there isn't a published date?
        # Current fix: Simple exclusion; do not track article.
        self.article_url = raw_article_xml.get("href")
        __raw_pub_date = re.search(r'(?<=/)(\d{4}/\d{2}/\d{2})', self.article_url)

        if __raw_pub_date is not None:

            # print(__raw_pub_date.group(1))

            year = re.search(r'^(\d{4})', __raw_pub_date.group(1)).group(1)
            month = re.search(r'(?<=/)(\d{2})(?=/)', __raw_pub_date.group(1)).group(1)
            day = re.search(r'(\d{2})$', __raw_pub_date.group(1)).group(1)

            self.pub_date = datetime.strptime(__raw_pub_date.group(1), "%Y/%m/%d")
        else:
            raise AttributeError("No publish date found, object not created.")


        if raw_article_xml.text is not None:
            self.headline = raw_article_xml.text
        else:
            raise AttributeError("No publication headline found, object not created.")

        self.dest_path = os.path.join(
            raw_data_path,
            self.pub_date.strftime("%Y"),
            self.pub_date.strftime("%m"),
            self.pub_date.strftime("%d")
        )

        self.dest_file = os.path.join(self.dest_path, self.headline + ".pdf")

    # retrieve pdf & store to file
    def extract(self):
        doc_options = {
            'page-size': 'Letter',
            'margin-top': '0.5in',
            'margin-bottom': '0.5in',
            'margin-left': '0in',
            'margin-right': '0in',
            'disable-javascript': '',

            # shut the hell up
            'quiet': '',
            # 'lowquality': '',
        }

        try:

            # generate path
            if not os.path.exists(self.dest_path):
                os.makedirs(self.dest_path, exist_ok=True)

            # does file already exist?
            if os.path.isfile(self.dest_file):
                raise FileExistsError

            # here is where UTF-8 compatibility __should__ be checked

            pdfkit.from_url(
                base_url + self.article_url,
                self.dest_file,
                doc_options
            )
        except IOError as e:
            print(e)
        except Exception as e:
            print(e)
        except FileExistsError as e:
            # The obvious error here is if the article is changed, the program
            #   won't catch that. The solution is to use some sort of file hash.
            #   Which is beyond the scope here.
            print("File already exists; exiting with record unchanged.")
            return

    # push to database (duh)
    def db_push(self):

        article = db.session.query(Article_Entry).filter_by(title=self.headline).first()

        if not article:
            article_metadata = Article_Entry(
                raw_url = self.dest_file,
                title = self.headline,
                publish_date = self.pub_date.date()
            )
            try:
                db.session.add(article_metadata)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __repr__(self):
        return "* %s, %s" % (self.headline, self.pub_date.date())

# Exposed function allow articles to be extracted from site
#   and pushes article metadata into the database.
@celery.task(name='horse.retrieve')
def retrieve():
    source = lxml.html.parse(base_url)

    docinfo = source.docinfo
    # assert(docinfo.encoding == 'UTF-8')

    all_articles = source.xpath(
        "//div[@class='article-content']/h2[@class='title']/a"
    )

    for raw_article_xml in all_articles:
        # pass the LXML.HTML element object
        try:
            a = Article(raw_article_xml)
            if __name__ == "__main__":
                print(a)
                continue
            a.extract()
            a.db_push()
        except AttributeError:
            continue

if __name__ == "__main__":
    retrieve()
    # extract_all()
