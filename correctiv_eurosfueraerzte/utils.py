import decimal

from django.core.paginator import Paginator


CURRENCY_CONVERSION_EURO = {
    2015: {
        'CHF': decimal.Decimal(0.9205150814)
    },
    2016: {
        'CHF': decimal.Decimal(0.9322542672)
    }
}


def convert_currency_to_euro(val, currency, year):
    val = decimal.Decimal(val)  # ensure decimal
    if currency == 'EUR':
        return val
    return CURRENCY_CONVERSION_EURO[year][currency] * val


class OptimizedPaginator(Paginator):
    '''
    Runs the count of the paginator without annotations/ordering
    which would otherwise result in counting a subquery which is
    around half as slow.
    '''
    def __init__(self, *args, **kwargs):
        annotated_qs = kwargs.pop('annotated_qs', None)
        super(OptimizedPaginator, self).__init__(*args, **kwargs)
        # Execute count without annotations and ordering
        self.count
        # Set annotated and ordered qs now
        if annotated_qs is not None:
            self.object_list = annotated_qs
