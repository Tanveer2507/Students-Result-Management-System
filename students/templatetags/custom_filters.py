"""
Custom template filters for SRMS
"""
from django import template

register = template.Library()

@register.filter(name='get')
def get_item(dictionary, key):
    """
    Get item from dictionary using key
    Usage: {{ mydict|get:key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.filter(name='get_attr')
def get_attribute(obj, attr):
    """
    Get attribute from object
    Usage: {{ myobj|get_attr:"attribute_name" }}
    """
    if obj is None:
        return None
    return getattr(obj, attr, None)
