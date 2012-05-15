from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def split_timeuntil(duration):
    return duration.split(",")[0]

@register.filter
@stringfilter
def removePrefixNumber(category):
    return category[2:]