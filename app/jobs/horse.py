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
import boto3
import unicodedata
import timeout_decorator

from app import db,\
    app

from app.config import raw_data_path
from app.models import Article as Article_Entry
from botocore.exceptions import ClientError

from datetime import date,\
    datetime,\
    timedelta

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
# celery = Celery(__name__, broker='redis://localhost:6379/0')
celery = Celery(__name__, broker=app.config.get('REDIS_URL'))
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

        self.dest_file = ""
        self.dest_path = raw_data_path

    # retrieve pdf & store to file
    @timeout_decorator.timeout(10)
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

    # Returns true if the article already exists in the dbase, take no further action;
    #   Else returns false, flag for extraction
    def db_check_exist_and_push(self):
        is_exist = db.session.query(Article_Entry).filter_by(headline=self.headline).first()

        # Add entry to database, retrieve ID, then use ID to name pdf
        if not is_exist:
            a = Article_Entry(
                    headline = self.headline,
                    publish_date = self.pub_date.date()
                )
            try:
                db.session.add(a)

                # once the entry is flushed to database, the ID should be available
                db.session.flush()

                target_name = "{}.pdf".format(a.id)

                self.dest_file = os.path.join(self.dest_path, target_name)
                a.raw_url = self.dest_file
                a.target_name = target_name

                db.session.commit()
            except IntegrityError:
                db.session.rollback()
            finally:
                return False

        return True

    def __repr__(self):
        return "* %s, %s" % (self.headline, self.pub_date.date())

# Exposed function allow articles to be extracted from site
#   and pushes article metadata into the database.
@celery.task(name='horse.retrieve')
def retrieve(first_call=False):
    source = lxml.html.parse(base_url)

    # docinfo = source.docinfo
    # assert(docinfo.encoding == 'UTF-8')

    all_articles = source.xpath(
        "//div[@class='article-content']/h2[@class='title']/a"
    )

    for raw_article_xml in all_articles:
        # pass the LXML.HTML element object
        try:
            a = Article(raw_article_xml)
            if not a.db_check_exist_and_push():
                a.extract()
        except TimeoutError:
            continue
        except AttributeError:
            continue

    if first_call == True:
        upload_all()

# Walk through the __database__ and store all non-stored files to AWS
@celery.task(name='horse.upload_all')
def upload_all():

    last_seven_days = datetime.utcnow() - timedelta(days=7)

    # Retrieve non-uploaded files from the dbase, om nom nom.
    upload_queue = Article_Entry.query.filter(
        (Article_Entry.uploaded == False),
        (Article_Entry.publish_date > last_seven_days)
    )

    # Open a cxn.
    s3 = boto3.client(
        "s3",
        aws_access_key_id=app.config.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=app.config.get('AWS_SECRET_KEY')
    )

    bucket = app.config.get('S3_BUCKET')

    if not bucket:
        raise ValueError("Bucket name cannot be `None`")

    try:
        s3.head_bucket(Bucket=bucket)
    except ClientError as e:
        if int(e.response['Error']['Code']) == 404:
            s3.create_bucket(Bucket=bucket)
        else:
            raise

    for article in upload_queue:
        headline_ascii = article.headline.encode('ascii', 'ignore').decode()

        target_metadata = {
            'Headline': headline_ascii,
            'PublishDate': article.publish_date.strftime("%Y-%m-%d"),
        }
        try:
            s3.put_object(
                ACL='public-read',
                Body=article.raw_url,
                Bucket=bucket,
                Key=article.target_name,
                Metadata=target_metadata
            )
        except Exception as e:
            print(e)

        try:
            article.uploaded = True

            aws_base_url = 'https://s3.amazonaws.com/breitbot-asset'
            article.aws_url = "{}/{}".format(aws_base_url, article.target_name)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

if __name__ == "__main__":
    retrieve()
