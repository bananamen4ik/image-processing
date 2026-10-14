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
    def __init__(
        self,
        initlist: ErrorList | Sequence[str | Exception] | None = None,
        error_class: str | None = None,
        renderer: BaseRenderer | None = None,
        field_id: str | None = None,
    ) -> None:
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
    @property
    def template_name(self) -> str:
        return 'common/forms/field.html'

    def label_tag(
        self,
        contents: str | None = None,
        attrs: dict[str, str | bool] | None = None,
        label_suffix: str | None = None,
        tag: str | None = None,
    ) -> SafeString:
        attrs = attrs or {}
        class_attr = attrs.get('class')

        if not isinstance(class_attr, str):
            class_attr = ''

        attrs['class'] = (class_attr + ' form-label').strip()

        return super().label_tag(
            contents=contents,
            attrs=attrs,
            label_suffix=label_suffix,
            tag=tag,
        )

    def css_classes(self, extra_classes: str | Iterable[str] | None = None) -> str:
        classes = super().css_classes(extra_classes)
        return ('mb-3 ' + classes).strip()

    def as_widget(
        self,
        widget: Widget | None = None,
        attrs: dict[str, str | bool] | None = None,
        only_initial: bool = False,
    ) -> SafeString:
        attrs = attrs or {}
        class_attr = attrs.get('class')

        if not isinstance(class_attr, str):
            class_attr = ''

        attrs['class'] = (class_attr + ' form-control').strip()

        if self.errors:
            attrs['class'] += ' is-invalid'

        return super().as_widget(widget=widget, attrs=attrs, only_initial=only_initial)


class CustomTemplateFormMixin:
    bound_field_class = CustomBoundField

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs['error_class'] = CustomErrorList
        super().__init__(*args, **kwargs)
