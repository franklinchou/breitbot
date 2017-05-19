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

__author__ = 'Franklin Chou'

import os

if __name__ != "__main__":
    from app.config import raw_data_path
    from app.models import Article
else:
    raw_data_path = os.path.join(os.path.dirname(__file__), 'test')

# from datetime import datetime
from datetime import date

import re


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

    def __repr__(self):
        return "{}-{}-{}".format(self.year, self.month, self.day)

class Article:
    def __init__(self, raw_article_xml):

        # Extract the publish date from the article url

        # 14 May 2017
        # If there isn't a published date?
        # Current fix: Simple exclusion; do not track article.
        self.article_url = raw_article_xml.get("href")
        __raw_pub_date = re.search(r'(?<=/)(\d{4}/\d{2}/\d{2})', self.article_url)

        if __raw_pub_date is not None:
            self.pub_date = PublishDate(__raw_pub_date.group(1))
        else:
            raise AttributeError("No publish date found, object not created.")


        if raw_article_xml.text is not None:
            self.headline = raw_article_xml.text
        else:
            raise AttributeError("No publication headline found, object not created.")

        self.dest_path = os.path.join(
            raw_data_path,
            self.pub_date.year,
            self.pub_date.month,
            self.pub_date.day
        )

        self.dest_file = os.path.join(self.dest_path, self.headline + ".pdf")

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
            'lowquality': '',
        }

        try:

            # generate path
            if not os.path.exists(self.dest_path):
                os.makedirs(self.dest_path, exist_ok=True)

            pdfkit.from_url(
                base_url + self.article_url,
                self.dest_file,
                doc_options
            )
        except IOError as e:
            print(e)
        except Exception as e:
            print(e)


    def __repr__(self):
        return "* %s, %s, %s" % (self.headline, self.pub_date, self.dest)

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
            a.extract()
            if __name__ == '__main__':
                print(a)
        except AttributeError:
            continue

if __name__ == "__main__":
    retrieve()
    # extract_all()
