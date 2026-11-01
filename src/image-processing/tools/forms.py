"""Application forms."""

from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
)

from django import forms
from django.utils.translation import gettext_lazy as _

from common.forms import CustomTemplateFormMixin
from tools.models import Operation

if TYPE_CHECKING:
    from django.utils.functional import _StrPromise


class ResizeForm(CustomTemplateFormMixin, forms.ModelForm):
    """Form for the resize operation."""

    MAX_PIXELS = 40_000_000
    field_order = (
        'uploaded_image',
        'width',
        'height',
    )
    error_messages: ClassVar[dict[str, '_StrPromise']] = {  # ruff: ignore[UP037]
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

    class Meta:
        """Configures the model and fields used by the form."""

        model = Operation
        fields = ('uploaded_image',)
        labels: ClassVar[dict[str, '_StrPromise']] = {  # ruff: ignore[UP037]
            'uploaded_image': _('Image'),
        }

    def clean(self) -> dict[str, Any] | None:
        """Checks for the pixel count limit."""
        cleaned_data = super().clean()

        if cleaned_data is None or self.errors:
            return cleaned_data

        width: int | None = cleaned_data.get('width')
        height: int | None = cleaned_data.get('height')

        if width is None or height is None:
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
