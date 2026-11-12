"""Application forms."""

from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
)

from django import forms
from django.core.files.uploadedfile import UploadedFile
from django.utils.translation import gettext_lazy as _
from PIL import Image

from common.forms import (
    CFTurnstileField,
    CustomTemplateFormMixin,
)
from tools.models import Operation

OPTIMIZE_IMAGE_FORMATS = ('JPEG', 'PNG')

if TYPE_CHECKING:
    from django.utils.functional import _StrPromise


def registered_extensions() -> list[tuple[str, str]]:
    """Returns a collections of all supported image extensions."""
    return [
        (extension, f'{pil_format} ({extension})')
        for extension, pil_format in Image.registered_extensions().items()
    ]


class BaseOperationForm(CustomTemplateFormMixin, forms.ModelForm):
    """A base class that describes form operation.

    Not intended for direct use!
    """

    error_messages: ClassVar[dict[str, '_StrPromise | str']] = {
        'invalid_image_format_none': _(
            'The file extension does not match the image format.',
        ),
        'invalid_image_format': _(
            'The file extension does not match the image format. '
            'Real image format: ".%(real_format)s".',
        ),
    }

    class Meta:
        """Configures the model and fields used by the form."""

        model = Operation
        fields = ('uploaded_image',)
        labels: ClassVar[dict[str, '_StrPromise']] = {
            'uploaded_image': _('Image'),
        }

    def clean_uploaded_image(self) -> UploadedFile:
        """Checks whether the image file extension matches the real format."""
        uploaded_image: UploadedFile = self.cleaned_data['uploaded_image']
        uploaded_image_extension = (
            str(Path(uploaded_image.name).suffix).lower()
            if uploaded_image.name is not None
            else ''
        )
        uploaded_image_format = Image.registered_extensions().get(
            uploaded_image_extension,
        )

        with Image.open(uploaded_image) as image:
            image_format = image.format
        uploaded_image.seek(0)

        if image_format is None:  # pragma: no cover
            raise forms.ValidationError(
                self.error_messages['invalid_image_format_none'],
                code='invalid_image_format_none',
            )

        if image_format != uploaded_image_format:
            raise forms.ValidationError(
                self.error_messages['invalid_image_format'],
                code='invalid_image_format',
                params={
                    'real_format': image_format,
                },
            )

        return uploaded_image


class ResizeForm(BaseOperationForm):
    """Form for the resize operation."""

    MAX_PIXELS = 40_000_000
    field_order = (
        'uploaded_image',
        'width',
        'height',
        'cf_turnstile_response',
    )

    error_messages: ClassVar[dict[str, '_StrPromise | str']] = {
        **BaseOperationForm.error_messages,
        'invalid_max_pixels': _(
            'The maximum number of pixels has been exceeded: '
            '%(current_pixels)s (max: %(max_pixels)s)',
        ),
    }

    width = forms.IntegerField(
        label=_('Width'),
        help_text=_('The final width of the image in pixels.'),
        min_value=1,
        max_value=10_000,
    )

    height = forms.IntegerField(
        label=_('Height'),
        help_text=_('The final height of the image in pixels.'),
        min_value=1,
        max_value=10_000,
    )

    cf_turnstile_response = CFTurnstileField()

    def clean(self) -> dict[str, Any] | None:
        """Checks for the pixel count limit."""
        cleaned_data = super().clean()

        if cleaned_data is None or self.errors:
            return cleaned_data

        width: int | None = cleaned_data.get('width')
        height: int | None = cleaned_data.get('height')

        if width is None or height is None:  # pragma: no cover
            return cleaned_data

        total_pixels = width * height

        if total_pixels > self.MAX_PIXELS:
            raise forms.ValidationError(
                self.error_messages['invalid_max_pixels'],
                code='invalid_max_pixels',
                params={
                    'current_pixels': total_pixels,
                    'max_pixels': self.MAX_PIXELS,
                },
            )

        return cleaned_data


class ConvertForm(BaseOperationForm):
    """Form for the convert operation."""

    field_order = (
        'uploaded_image',
        'extension',
        'cf_turnstile_response',
    )

    extension = forms.ChoiceField(
        label=_('Format'),
        help_text=_('Format for the final image.'),
        choices=registered_extensions,
    )

    cf_turnstile_response = CFTurnstileField()


class OptimizeForm(BaseOperationForm):
    """Form for the optimize operation."""

    error_messages: ClassVar[dict[str, '_StrPromise | str']] = {
        **BaseOperationForm.error_messages,
        'invalid_accepted_image_format': _('Invalid image format.'),
    }

    cf_turnstile_response = CFTurnstileField()

    class Meta(BaseOperationForm.Meta):  # ty: ignore[invalid-attribute-override]
        """Adds a notification about supported image formats."""

        help_texts: ClassVar[dict[str, str]] = {
            'uploaded_image': _('Available formats: %(formats)s.')
            % {
                'formats': ', '.join(OPTIMIZE_IMAGE_FORMATS),
            },
        }

    def clean_uploaded_image(self) -> UploadedFile:
        """Checks whether the image format is valid."""
        uploaded_image: UploadedFile = super().clean_uploaded_image()

        with Image.open(uploaded_image) as image:
            image_format = image.format
        uploaded_image.seek(0)

        if image_format not in OPTIMIZE_IMAGE_FORMATS:
            raise forms.ValidationError(
                self.error_messages['invalid_accepted_image_format'],
                code='invalid_accepted_image_format',
            )

        return uploaded_image
