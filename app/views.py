from app import app

from flask import render_template,\
    send_from_directory

from sqlalchemy import desc

from app.models import Article

from app.config import raw_data_path

@app.route('/')
def home():

    # Display only 50 articles from the query
    # @TODO use fixed page? to dynamically load all articles to page
    article_list = []
    try:
        selected_articles = Article.query.filter(Article.headline != None).order_by(desc(Article.publish_date)).limit(50)
        for article in selected_articles:
            article_dict = {
                'ID': article.id,
                'URL': article.raw_url,
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
