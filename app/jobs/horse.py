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

from app.celery_config import celery

from .retry import retry

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

base_url = 'http://www.breitbart.com'
aws_base_url = 'https://s3.amazonaws.com/breitbot-asset'

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
        self.pdf_output = None

    def push_to_breitbot(self):
        is_exist = db.session.query(Article_Entry).filter(
            (Article_Entry.headline==self.headline),
            (Article_Entry.upload==True)).first()
        if not is_exist:
            session_object = Article_Entry(
                    headline = self.headline,
                    publish_date = self.pub_date.date()
                )
            try:
                db.session.add(session_object)
                db.session.flush()

                self.target_name = "{}.pdf".format(session_object.id)
                session_object.target_name = self.target_name

                self._extract()
                self._upload()
                self._update(session_object)

                db.session.commit()
            except IntegrityError:
                db.session.rollback()
            except ClientError:
                db.session.rollback()
                raise ClientError
        else:
            raise FileExistsError

    # retrieve pdf & store to VARIABLE
    @timeout_decorator.timeout(10)
    def _extract(self):
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
            # Set output to false, allows pdf output to be stored as variable
            self.pdf_output = pdfkit.from_url(
                base_url + self.article_url,
                False,
                doc_options
            )
        except IOError as e:
            print(e)
        except Exception as e:
            print(e)

    @retry(ClientError, tries=3, delay=3, backoff=2)
    def _upload(self):
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

        target_metadata = {
            'Headline': self.headline.encode('ascii', 'ignore').decode(),
            'PublishDate': self.pub_date.strftime("%Y-%m-%d")
        }
        if not self.pdf_output:
            raise ValueError("Cannot upload file to bucket if binary string is empty.")
        try:
            s3.put_object(
                    ACL = 'public-read',
                    Body = self.pdf_output,
                    Bucket = bucket,
                    Key = self.target_name,
                    Metadata = target_metadata
                )
        except ClientError as e:
            raise

    def _update(self, session_object):
        try:
            session_object.uploaded = True
            session_object.aws_url = "{}/{}".format(aws_base_url, self.target_name)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

    def __repr__(self):
        return "* %s, %s" % (self.headline, self.pub_date.date())

# Exposed function allow articles to be extracted from site
#   and pushes article metadata into the database.
@celery.task(name='horse.retrieve')
def retrieve():
    try:
        source = lxml.html.parse(base_url)
    except OSError:
        # @TODO: If there's a failure to get the website, requeue the task
        pass

    # docinfo = source.docinfo
    # assert(docinfo.encoding == 'UTF-8')

    all_articles = source.xpath(
        "//div[@class='article-content']/h2[@class='title']/a"
    )

    for raw_article_xml in all_articles:
        # pass the LXML.HTML element object
        try:
            new_article = Article(raw_article_xml)
            new_article.push_to_breitbot()
        except TimeoutError:
            continue
        except AttributeError:
            continue
        except ClientError:
            continue
        except FileExistsError:
            continue

def upload_check():

    last_seven_days = datetime.utcnow() - timedelta(days=7)

    # Retrieve non-uploaded files from the dbase
    upload_queue = Article_Entry.query.filter(
        (Article_Entry.uploaded == False),
        (Article_Entry.publish_date > last_seven_days)
    )
