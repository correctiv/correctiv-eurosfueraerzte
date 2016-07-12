from django import template
from django.template.defaultfilters import floatformat
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()


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

register.filter('intcomma_floatformat', intcomma_floatformat)
