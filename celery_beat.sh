#! /bin/bash

celery -A app.jobs.horse beat --loglevel=info -s ./var/celery/celerybeat-schedule -l debug
