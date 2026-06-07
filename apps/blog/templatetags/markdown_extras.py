import markdown as md
import bleach
from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import get_language

register = template.Library()

ALLOWED_TAGS = [
    "h1", "h2", "h3", "h4", "h5", "h6",
    "p", "br", "hr",
    "ul", "ol", "li",
    "blockquote", "pre", "code",
    "strong", "em", "a", "img",
    "table", "thead", "tbody", "tr", "th", "td",
    "dl", "dt", "dd",
    "abbr", "acronym",
    "sub", "sup",
    "span", "div",
    "del", "ins",
]

ALLOWED_ATTRS = {
    "a": ["href", "title", "rel", "target"],
    "img": ["src", "alt", "title", "width", "height"],
    "code": ["class"],
    "pre": ["class"],
    "th": ["align"],
    "td": ["align"],
    "span": ["class"],
    "div": ["class"],
}


@register.filter
def render_markdown(text):
    if not text:
        return ""
    extensions = [
        "extra",
        "codehilite",
        "fenced_code",
        "tables",
        "sane_lists",
    ]
    html = md.markdown(text, extensions=extensions)
    clean = bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS)
    return mark_safe(clean)


@register.filter
def translated_field(obj, field_name):
    lang = get_language()
    if lang and lang.startswith("fr"):
        fr_val = getattr(obj, f"{field_name}_fr", None)
        if fr_val:
            return fr_val
    return getattr(obj, field_name)


@register.filter
def split(value, separator=","):
    if not value:
        return []
    return [item.strip() for item in value.split(separator)]


@register.filter
def trim(value):
    return value.strip() if value else ""
