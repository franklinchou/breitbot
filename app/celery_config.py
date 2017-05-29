# schedules tasks

__author__ = 'Franklin Chou'

from celery import chord
from celery.schedules import crontab

timezone = 'UTC'

beat_schedule = {
    'run-every-hour': {
        # 'task': chord('horse.retrieve', 'horse.upload_all'),
        'task': 'horse.retrieve',
        'schedule': crontab(hour='*/1', minute=0)
    },
}

task_soft_time_limit = 60
