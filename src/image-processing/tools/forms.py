"""Application forms."""

from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
)

from django import forms
from django.core.files.uploadedfile import UploadedFile
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from PIL import Image

from common.forms import CustomTemplateFormMixin
from tools.models import Operation

if TYPE_CHECKING:
    from django.utils.functional import _StrPromise


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
            'To upload the file, change its extension to: ".%(real_format)s".',
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
        FORMAT_ALIASES = {
            'jpeg': 'jpg',
            'tiff': 'tif',
        }
        uploaded_image: UploadedFile = self.cleaned_data['uploaded_image']
        uploaded_image_extension = (
            uploaded_image.name.split('.')[-1].lower()
            if uploaded_image.name is not None
            else ''
        )

        with Image.open(uploaded_image) as image:
            image_format = image.format
        uploaded_image.seek(0)

        if image_format is None:  # pragma: no cover
            raise forms.ValidationError(
                self.error_messages['invalid_image_format_none'],
                code='invalid_image_format_none',
            )

        image_format = image_format.lower()
        image_format = FORMAT_ALIASES.get(image_format, image_format)
        uploaded_image_extension = FORMAT_ALIASES.get(
            uploaded_image_extension,
            uploaded_image_extension,
        )

        if image_format != uploaded_image_extension:
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
    )

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

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes new errors."""
        self.error_messages['invalid_max_pixels'] = gettext(
            'The maximum number of pixels has been exceeded: '
            '%(current_pixels)s (max: %(max_pixels)s)',
        )
        super().__init__(*args, **kwargs)

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
