from django import template

register = template.Library()

@register.filter
def get_range(value):
    """Returns a range of numbers from 1 to value."""
    return range(1, int(value) + 1)

@register.filter
def get_item(dictionary, key):
    """Returns the value for the given key from the dictionary."""
    return dictionary.get(str(key)) 