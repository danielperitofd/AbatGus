from django import template
from django.utils import translation

from core.formatting import (
    format_currency,
    format_measure,
    format_number,
    month_label,
    unit_label,
    week_label,
)
from core.runtime import get_current_organization


register = template.Library()


def _context_settings():
    organization = get_current_organization()
    language_code = translation.get_language() or "pt-br"
    currency_code = getattr(organization, "default_currency", "BRL")
    return currency_code, language_code


@register.filter
def brl(value):
    currency_code, language_code = _context_settings()
    return format_currency(value, currency_code=currency_code, language_code=language_code)


@register.filter
def number_br(value):
    _, language_code = _context_settings()
    return format_number(value, language_code=language_code)


@register.filter
def kg(value):
    _, language_code = _context_settings()
    return format_measure(value, "kg", language_code)


@register.filter
def grams(value):
    _, language_code = _context_settings()
    return format_measure(value, "g", language_code)


@register.filter
def liters(value):
    _, language_code = _context_settings()
    return format_measure(value, "l", language_code)


@register.filter
def month_name(value):
    return month_label(value)


@register.filter
def week_name(value):
    return week_label(value)


@register.filter
def unit_display(value):
    return unit_label(value)
