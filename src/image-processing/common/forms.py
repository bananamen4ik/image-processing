from django.forms import BoundField
from django.forms.utils import ErrorList


class CustomErrorList(ErrorList):
    def __init__(
            self,
            initlist=None,
            error_class=None,
            renderer=None,
            field_id=None,
    ):
        error_class = error_class + ' invalid-feedback d-block' if error_class else 'invalid-feedback'
        super().__init__(
            initlist=initlist,
            error_class=error_class,
            renderer=renderer,
            field_id=field_id,
        )


class CustomBoundField(BoundField):
    @property
    def template_name(self):
        return 'common/forms/field.html'

    def label_tag(self, contents=None, attrs=None, label_suffix=None, tag=None):
        attrs = attrs or {}
        attrs['class'] = (attrs.get('class', '') + ' form-label').strip()

        return super().label_tag(contents=contents, attrs=attrs, label_suffix=label_suffix, tag=tag)

    def css_classes(self, extra_classes=None):
        classes = super().css_classes(extra_classes)
        return ('mb-3 ' + classes).strip()

    def as_widget(self, widget=None, attrs=None, only_initial=False):
        attrs = attrs or {}
        attrs['class'] = (attrs.get('class', '') + ' form-control').strip()

        if self.errors:
            attrs['class'] += ' is-invalid'

        return super().as_widget(widget=widget, attrs=attrs, only_initial=only_initial)


class CustomTemplateFormMixin:
    bound_field_class = CustomBoundField

    def __init__(self, *args, **kwargs):
        kwargs['error_class'] = CustomErrorList
        super().__init__(*args, **kwargs)
