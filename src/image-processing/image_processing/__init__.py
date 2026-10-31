"""Provides the project configuration and import celery."""

from image_processing.celery import app as celery_app

__all__ = ('celery_app',)
