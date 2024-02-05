from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='markdown')
@stringfilter
def render_markdown(source):
    return mark_safe(f"<section class='markdown'>{ source }</section>")
