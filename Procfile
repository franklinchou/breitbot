web: gunicorn manage:app --log-file=-

celery_beat: celery -A app.jobs.horse worker --beat --loglevel=info
