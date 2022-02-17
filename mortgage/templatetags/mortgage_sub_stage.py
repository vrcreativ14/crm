from django import template
register = template.Library()

@register.simple_tag
def setsubstages(val=None):
  return val

def setcurrentstages(val=None):
  return val