from __future__ import unicode_literals

from django import template
from django.template.defaultfilters import floatformat
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.safestring import mark_safe
from django.utils import six

from babel.numbers import format_currency, get_currency_symbol

register = template.Library()


def join_list(values):
    if len(values) > 1:
        return _('{} and {}').format(', '.join(str(s) for s in values[:-1]), values[-1])
    return '{}'.format(values[0])


def intcomma_floatformat(value, arg=2):
    if value is None:
        return None

    DECIMAL_SEPARATOR = floatformat(0.0, 2)[1]

    value = round(value, arg)

    val = intcomma(value)
    if DECIMAL_SEPARATOR not in val:
        if arg > 0:
            val += '%s%s' % (DECIMAL_SEPARATOR, '0' * arg)
    else:
        before_ds, after_ds = val.rsplit(DECIMAL_SEPARATOR, 1)
        if len(after_ds) > arg:
            after_ds = after_ds[:arg]
        elif len(after_ds) < arg:
            after_ds += '0' * (arg - len(after_ds))
        if arg > 0:
            val = '%s%s%s' % (before_ds, DECIMAL_SEPARATOR, after_ds)
        else:
            val = before_ds
    return val


@register.simple_tag(takes_context=True)
def currency_format(context, value, currency='EUR', decimal=2):
    if value is None:
        value = 0.0

    lang = translation.get_language()
    locale = context.get('locale', lang)

    if isinstance(value, six.string_types):
        symbol = get_currency_symbol(currency, locale=locale)
        if not symbol:
            symbol = currency
        return mark_safe('%s&nbsp;%s' % (value, symbol))

    value = round(value, decimal)
    formatted = format_currency(value, currency, locale=locale)
    symbol = get_currency_symbol(currency, locale=locale)
    if not context.get('filter_country') and len(symbol) == 1:
        # When we have possibly mixed currencies, show three letter symbol
        # This improves alignment
        formatted = formatted.replace(symbol, currency)
    if decimal == 0:
        zero_amount = format_currency(0, currency, locale=locale)
        zero_decimals = zero_amount.replace(symbol, '').strip()[1:]
        formatted = formatted.replace(zero_decimals, '')
    return mark_safe(formatted.replace(' ', '&nbsp;'))


register.filter('intcomma_floatformat', intcomma_floatformat)
register.filter('currency_format', currency_format)
register.filter('join_list', join_list)
