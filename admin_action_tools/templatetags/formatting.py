from django import template
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def format_change_data_field_value(field_value):
    if isinstance(field_value, str):
        return field_value
    try:
        output = "<ul>"
        for value in iter(field_value):
            output += "<li>" + escape(value) + "</li>"
        output += "</ul>"
        return mark_safe(output)  # nosec
    except Exception:
        return field_value


@register.simple_tag
def verbose_name(obj, fieldname):
    name = obj._meta.get_field(fieldname).verbose_name
    return name.capitalize() if isinstance(name, str) else name


@register.simple_tag
def back_url(queryset, opts):
    if len(queryset) == 1:
        obj = queryset[0]
        return reverse("admin:%s_%s_change" % (opts.app_label, opts.model_name), args=[obj.pk])
    return reverse("admin:%s_%s_changelist" % (opts.app_label, opts.model_name))
