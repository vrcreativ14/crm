import json

from django import template

from django.core.serializers import serialize
from django.db.models.query import QuerySet


register = template.Library()


@register.filter(name='replace_with_space')
def replace_with_space(value, arg):
    """Replace all occurences of arg from the given string"""
    return value.replace(arg, ' ')


@register.filter(name='jsonify')
def jsonify(obj):
    if isinstance(obj, QuerySet):
        return serialize('json', obj)

    return json.dumps(obj)
