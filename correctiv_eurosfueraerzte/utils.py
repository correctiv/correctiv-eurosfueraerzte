import decimal
import itertools

from django.core.paginator import Paginator

from .apps import EFA_YEARS


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


def get_year_columns(qs):
    def key_func(x):
        return (x.pharma_company.get_absolute_url(),
                x.pharma_company.name,
                x.get_label_display(),
                x.recipient_detail,
                x.currency)

    def get_years(payments):
        payments = {p.date.year: p for p in payments}
        for year in EFA_YEARS:
            if year in payments:
                yield {
                    'year': year,
                    'amount': payments[year].amount,
                    'currency': payments[year].currency
                }
            else:
                yield {
                    'year': year,
                    'amount': None,
                    'currency': None
                }

    qs = sorted(qs, key=key_func)
    qs = [{
        'pharma_company_url': k[0],
        'pharma_company_name': k[1],
        'label': k[2],
        'recipient_detail': k[3],
        'years': [x for x in get_years(g)]
        } for k, g in itertools.groupby(qs, key=key_func)]
    qs = sorted(qs, key=lambda x: x['years'][-1]['amount'], reverse=True)
    return qs
