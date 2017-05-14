__author__ = 'Franklin Chou'

#------------------------------------------------------------------------------
#
# app/horse.py
#
# This is where all the magic happens.
#
# 14 May 2017
# Remove reliance on a text doc as temporary storage.
# Write all article extractions, including initiation, to database.
#
#------------------------------------------------------------------------------


import os
# from app.config import raw_data_path
# from app.config import article_listing

# from datetime import datetime
from datetime import date

import re

# from app.models import Article

#------------------------------------------------------------------------------
# html/xml parsing
#------------------------------------------------------------------------------
import lxml.html
from lxml import etree

#------------------------------------------------------------------------------
# pdf generation imports
#------------------------------------------------------------------------------
import pdfkit

'''
    1. initialize & get page articles
    2. on interval: compare new page articles to existing page articles (collected from initialize)
    3. find difference; convert to pdf
'''

base_url = 'http://www.breitbart.com'

class PublishDate:
    def __init__(self, raw_date):
        self.year = re.search(r'^(\d{4})', raw_date).group(1)
        self.month = re.search(r'(?<=/)(\d{2})(?=/)', raw_date).group(1)
        self.day = re.search(r'(\d{2})$', raw_date).group(1)

        self.date = "{}{}{}".format(self.year, self.month, self.day)

    def file_date(self):
        return "{}-{}-{}".format(self.year, self.month, self.day)

class Article:
    def __init__(self, raw_article_xml):

        # Extract the publish date from the article url

        # 14 May 2017
        # If there isn't a published date?
        # Current fix: Simple exclusion; do not track article.
        __article_url = raw_article_xml.get("href")
        __raw_pub_date = re.search(r'(?<=/)(\d{4}/\d{2}/\d{2})', __article_url)

        if __raw_pub_date is not None:
            self.pub_date = PublishDate(__raw_pub_date.group(1))
        else:
            raise AttributeError("No publish date found, object not created.")

        self.headline = raw_article_xml.text

    def __repr__(self):
        return "Article(title = %s, date = %s)" % (self.headline, self.pub_date)

def retrieve():
    source = lxml.html.parse(base_url)

    docinfo = source.docinfo
    # assert(docinfo.encoding == 'UTF-8')

    all_articles = source.xpath(
        "//div[@class='article-content']/h2[@class='title']/a"
    )

    for a_raw in all_articles:
        # pass the LXML.HTML element object
        try:
            a = Article(a_raw)
        except AttributeError:
            continue

def extract_all():
    # expects list of anchor tags; each on own line
    try:
        with open(article_listing, 'r') as f:
            for article_html in f:
                extract_as_pdf(article_html)
    except IOError as e:
        print(e)

# This could be hella modular, but I'm lazy
def generate_path(parent, child):
    full_dir = os.path.join(raw_data_path, parent)
    if not os.path.exists(full_dir):
        os.makedirs(full_dir, exist_ok=True)

    return os.path.join(raw_data_path, parent, child)

def extract_as_pdf(article_from_static_file):
    doc_options = {
        'page-size': 'Letter',
        'margin-top': '0.5in',
        'margin-bottom': '0.5in',
        'margin-left': '0in',
        'margin-right': '0in',

        'disable-javascript': ''
    }

    try:

        raw = lxml.html.fromstring(article_from_static_file)
        headline = lxml.html.fromstring(article_from_static_file).text_content()
        child_url = raw.xpath('//a/@href')[0]

    except Exception as e:
        print("Unexpected error")
        print(e)

    url = "{}{}".format(
        base_url,
        child_url
    )

    destination = re.search(r'^.*(?<=/)(.*?)(?=/)', child_url).group(1)

    # /year/month/day
    raw_publish_date = re.search(r'(?<=/)(\d{4}/\d{2}/\d{2})', child_url).group(1)
    publish_date = PublisDate(raw_publish_date)

    # Truncate file name length to fit date (just in case)
    # Date needs 8 characters
    if len(destination) > 255:
        destination = destination[:-8]

    destination = generate_path(
        publish_date.file_date(),
        "{}{}.pdf".format(destination, publish_date.date)
    )

    # visit & extract as pdf
    try:
        pdfkit.from_url(url, destination, doc_options)
    except IOError as e:
        print(e)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    retrieve()
    # extract_all()
