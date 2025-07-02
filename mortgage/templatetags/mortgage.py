from django import template
from django.db.models.query import QuerySet

register = template.Library()

@register.filter()
def field_name_to_label(value):
    value = value.replace('_', ' ')
    return value.title()
