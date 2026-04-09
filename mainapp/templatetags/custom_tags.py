from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.simple_tag
def get_item_tuple(dictionary, emp_id, day):
    return dictionary.get((emp_id, day))

