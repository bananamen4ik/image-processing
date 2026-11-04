"""Application models."""

import uuid
from functools import partial
from pathlib import Path

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from custom_auth.models import CustomUser


def get_upload_to(dir_name: str, instance: Operation, filename: str) -> str:
    """Returns the file name relative to MEDIA_ROOT."""
    now = timezone.now().strftime('%Y/%m/%d')
    suffix = Path(filename).suffix.lower()
    return f'tools/{dir_name}/{now}/{uuid.uuid4()}{suffix}'


class Operation(models.Model):
    """Defines the unit of an image operation."""

    class Status(models.IntegerChoices):
        """Defines the status of an image operation."""

        CREATED = 0, _('Created')
        PROCESSING = 1, _('Processing')
        COMPLETED = 2, _('Completed')
        FAILED = 3, _('Failed')

    class Type(models.IntegerChoices):
        """Defines the type of image operation."""

        RESIZE = 0, _('Resize')
        CONVERT = 1, _('Convert')
        OPTIMIZE = 2, _('Optimize')

    user = models.ForeignKey(
        verbose_name=_('user'),
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name='operations',
    )

    uploaded_image = models.ImageField(
        verbose_name=_('uploaded image'),
        upload_to=partial(get_upload_to, 'uploaded_images'),
    )

    parameters = models.JSONField(
        verbose_name=_('parameters'),
    )

    type = models.IntegerField(
        verbose_name=_('type'),
        choices=Type.choices,
    )

    processed_image = models.ImageField(
        verbose_name=_('processed image'),
        upload_to=partial(get_upload_to, 'processed_images'),
        blank=True,
    )

    status = models.IntegerField(
        verbose_name=_('status'),
        choices=Status.choices,
        default=Status.CREATED,
    )

    created_at = models.DateTimeField(
        verbose_name=_('created at'),
        auto_now_add=True,
    )

    processed_at = models.DateTimeField(
        verbose_name=_('processed at'),
        default=None,
        null=True,
        blank=True,
    )
