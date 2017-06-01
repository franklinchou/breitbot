# schedules tasks

__author__ = 'Franklin Chou'

import os

from celery import Celery

# from celery import chord
from celery.schedules import crontab

celery = Celery(__name__, broker = os.environ.get('REDIS_URL').strip('\''))
celery.config_from_object('app.celery_config')

timezone = 'UTC'

beat_schedule = {
    'run-every-hour': {
        'task': 'horse.retrieve',
        'schedule': crontab(hour='*/1', minute=0)
    },
}

task_soft_time_limit = 60
