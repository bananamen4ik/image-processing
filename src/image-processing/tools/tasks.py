"""Celery tasks."""

import io
from pathlib import Path

from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.files.base import ContentFile
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from PIL import Image

from tools.models import Operation

logger = get_task_logger(__name__)


@shared_task(ignore_result=True)
def image_resize_processing(operation_id: int) -> None:
    """Resizes the image."""
    logger.info(
        _('Starting image resizing: %(operation_id)s')
        % {
            'operation_id': operation_id,
        },
    )

    operation = Operation.objects.get(pk=operation_id)

    if operation.status != Operation.Status.CREATED:
        raise ValueError(_('Operation status is not CREATED'))

    if operation.type != Operation.Type.RESIZE:
        raise ValueError(_('Operation type is not RESIZE'))

    operation.status = Operation.Status.PROCESSING
    operation.save(update_fields=['status'])

    uploaded_image = operation.uploaded_image

    try:
        with uploaded_image.open(), Image.open(uploaded_image) as image:
            new_image_format = image.format
            new_image = image.resize(
                (operation.parameters['width'], operation.parameters['height']),
                resample=Image.Resampling.LANCZOS,
            )
            buffer = io.BytesIO()
            new_image.save(buffer, new_image_format)

        operation.processed_image.save(
            str(uploaded_image.name),
            ContentFile(buffer.getvalue()),
        )
    except Exception:
        operation.status = Operation.Status.FAILED
        operation.processed_at = timezone.now()
        operation.save(update_fields=['status', 'processed_at'])
        raise

    operation.status = Operation.Status.COMPLETED
    operation.processed_at = timezone.now()
    operation.save(update_fields=['status', 'processed_at'])


@shared_task(ignore_result=True)
def image_convert_processing(operation_id: int) -> None:
    """Converts the image."""
    logger.info(
        _('Starting image converting: %(operation_id)s')
        % {
            'operation_id': operation_id,
        },
    )

    operation = Operation.objects.get(pk=operation_id)

    if operation.status != Operation.Status.CREATED:
        raise ValueError(_('Operation status is not CREATED'))

    if operation.type != Operation.Type.CONVERT:
        raise ValueError(_('Operation type is not CONVERT'))

    operation.status = Operation.Status.PROCESSING
    operation.save(update_fields=['status'])

    uploaded_image = operation.uploaded_image

    try:
        with uploaded_image.open(), Image.open(uploaded_image) as image:
            new_image_format = operation.parameters['format']
            buffer = io.BytesIO()
            image.save(buffer, new_image_format)

        name = str(
            Path(
                str(uploaded_image.name),
            ).with_suffix(
                operation.parameters['extension'],
            ),
        )

        operation.processed_image.save(
            name,
            ContentFile(buffer.getvalue()),
        )
    except Exception:
        operation.status = Operation.Status.FAILED
        operation.processed_at = timezone.now()
        operation.save(update_fields=['status', 'processed_at'])
        raise

    operation.status = Operation.Status.COMPLETED
    operation.processed_at = timezone.now()
    operation.save(update_fields=['status', 'processed_at'])
