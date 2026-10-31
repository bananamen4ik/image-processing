"""Defining a Celery instance."""

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'image_processing.settings')

app = Celery('image_processing')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
