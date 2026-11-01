"""Celery tasks."""

from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(ignore_result=True)
def image_resize_processing(operation_id: int) -> None:
    """Resizes the image."""
    logger.info(f'Resizing image: {operation_id}')
