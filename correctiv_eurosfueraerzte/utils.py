import decimal

CURRENCY_CONVERSION_EURO = {
    2015: {
        'CHF': decimal.Decimal(0.9205150814)
    }
}


def convert_currency_to_euro(val, currency, year):
    val = decimal.Decimal(val)  # ensure decimal
    if currency == 'EUR':
        return val
    return CURRENCY_CONVERSION_EURO[year][currency] * val
