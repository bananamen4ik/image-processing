"""Shared form mixins for the project."""

from collections.abc import (
    Iterable,
    Sequence,
)
from typing import Any

from django.forms import BoundField
from django.forms.renderers import BaseRenderer
from django.forms.utils import ErrorList
from django.forms.widgets import Widget
from django.utils.safestring import SafeString


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
            else 'invalid-feedback'
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
        return 'common/forms/field.html'

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
