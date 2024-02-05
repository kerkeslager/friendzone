from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

import markdown_it

register = template.Library()

@register.filter(name='markdown')
@stringfilter
def render_markdown(source):
    renderer = markdown_it.MarkdownIt('js-default')
    result = renderer.render(source)
    result = "<section class='markdown'>{}</section>".format(result)
    result = mark_safe(result)
    return result
