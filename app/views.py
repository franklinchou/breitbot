from flask import render_template,\
    send_from_directory

from datetime import datetime,\
    timedelta

from app import app
from app.models import Article

from sqlalchemy import desc

@app.route('/')
def home():

    # Display the last week's worth of articles
    # @TODO use fixed page? to dynamically load all articles to page


    last_seven_days = datetime.utcnow() - timedelta(days=7)

    article_list = []
    try:
        selected_articles = Article.query.filter(
            (Article.publish_date > last_seven_days),
            (Article.uploaded == True)
            ).order_by(desc(Article.publish_date)
        )

        for article in selected_articles:
            article_dict = {
                'ID': article.id,
                'URL': article.aws_url,
                'Headline': article.headline,
                'PublishDate': article.publish_date
            }
            article_list.append(article_dict)
    except Exception as e:
        print(e)

    return render_template('home.html', articles=article_list)

@app.route('/raw/<filename>')
def serve_file(filename):
    return send_from_directory(raw_data_path, filename)

@app.route('/about')
def about():
    return render_template('about.html')
