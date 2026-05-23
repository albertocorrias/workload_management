from django import template
register = template.Library()

@register.filter(name="list_index")
def list_index(indexable, i):
    return indexable[i]