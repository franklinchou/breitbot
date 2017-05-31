#! /bin/bash

celery -A app.jobs.horse worker --loglevel=info
