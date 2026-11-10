"""Shared form mixins for the project."""

from collections.abc import (
    Iterable,
    Sequence,
)
from typing import Any

import httpx
from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms import (
    BoundField,
    CharField,
)
from django.forms.renderers import BaseRenderer
from django.forms.utils import ErrorList
from django.forms.widgets import Widget
from django.utils.safestring import SafeString
from django.utils.translation import gettext as _


class CustomErrorList(ErrorList):
    """Renders form errors with Bootstrap validation classes."""

    def __init__(
        self,
        initlist: ErrorList | Sequence[str | Exception] | None = None,
        error_class: str | None = None,
        renderer: BaseRenderer | None = None,
        field_id: str | None = None,
    ) -> None:
        """Initializes the error list with Bootstrap validation classes."""
        error_class = (
            error_class + ' invalid-feedback d-block'
            if error_class
            else 'invalid-feedback d-block'
        )
        super().__init__(
            initlist=initlist,
            error_class=error_class,
            renderer=renderer,
            field_id=field_id,
        )


class CustomBoundField(BoundField):
    """Renders form fields using Bootstrap styling."""

    @property
    def template_name(self) -> str:
        """Returns the template used to render the form field."""
        return self.field.template_name or 'common/forms/field.html'

    def label_tag(
        self,
        contents: str | None = None,
        attrs: dict[str, str | bool] | None = None,
        label_suffix: str | None = None,
        tag: str | None = None,
    ) -> SafeString:
        """Adds Bootstrap styling to the field label."""
        attrs = attrs or {}
        class_attr = attrs.get('class')

        if not isinstance(class_attr, str):  # pragma: no cover
            class_attr = ''

        attrs['class'] = (class_attr + ' form-label').strip()

        return super().label_tag(
            contents=contents,
            attrs=attrs,
            label_suffix=label_suffix,
            tag=tag,
        )

    def css_classes(self, extra_classes: str | Iterable[str] | None = None) -> str:
        """Adds bottom spacing to the field wrapper."""
        classes = super().css_classes(extra_classes)
        return ('mb-3 ' + classes).strip()

    def as_widget(
        self,
        widget: Widget | None = None,
        attrs: dict[str, str | bool] | None = None,
        only_initial: bool = False,
    ) -> SafeString:
        """Adds Bootstrap styling and indicates invalid fields."""
        attrs = attrs or {}
        class_attr = attrs.get('class')

        if not isinstance(class_attr, str):  # pragma: no cover
            class_attr = ''

        attrs['class'] = (class_attr + ' form-control').strip()

        if self.errors:
            attrs['class'] += ' is-invalid'

        return super().as_widget(widget=widget, attrs=attrs, only_initial=only_initial)


class CustomTemplateFormMixin:
    """Configures forms to use Bootstrap styling."""

    bound_field_class = CustomBoundField

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Configures the form to use Bootstrap error styling."""
        kwargs['error_class'] = CustomErrorList
        super().__init__(*args, **kwargs)


class CFTurnstileBoundField(CustomBoundField):
    """Configures context data."""

    def get_context(self) -> dict[str, Any]:
        """Adds the site key to the template."""
        context = super().get_context()
        context['site_key'] = settings.CF_TURNSTILE_SITE_KEY
        return context


class CFTurnstileField(CharField):
    """Field for the turnstile CAPTCHA."""

    def __init__(self) -> None:
        """Configures the field."""
        super().__init__(
            max_length=2048,
            required=False,
            # ty: ignore[unknown-argument]
            template_name='common/forms/cf_turnstile_field.html',
            # ty: ignore[unknown-argument]
            bound_field_class=CFTurnstileBoundField,
            error_messages={
                'cf_turnstile_invalid': _('Verification failed. Please try again.'),
            },
        )

    def clean(self, value: Any) -> Any:  # pragma: no cover
        """Validates the token."""
        if settings.DEBUG or settings.TESTING:
            return value

        url = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'
        data = {
            'secret': settings.CF_TURNSTILE_SECRET_KEY,
            'response': value,
        }
        error = False

        try:
            response = httpx.post(url, data=data, timeout=10)
            response.raise_for_status()

            validation = response.json()
            if not validation['success']:
                error = True
        except httpx.HTTPStatusError:
            error = True

        if error:
            raise ValidationError(
                self.error_messages['cf_turnstile_invalid'],
                code='cf_turnstile_invalid',
            )

        return value
