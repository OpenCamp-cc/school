from django import template

register = template.Library()


@register.filter(name='splitnewline')
def split_newline(value):
    """
    Returns the value turned into a list.
    """
    return [v.strip() for v in value.split('\n')]
