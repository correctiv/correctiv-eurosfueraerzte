from django.apps import AppConfig
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy as _


EFA_COUNTRIES = [
            ('DE', pgettext_lazy('stand-alone', 'Germany')),
            ('AT', pgettext_lazy('stand-alone', 'Austria')),
            ('CH', pgettext_lazy('stand-alone', 'Switzerland')),
]
EFA_COUNTRIES_DICT = dict(EFA_COUNTRIES)

EFA_COUNTRIES_CHOICE = [
            ('DE', pgettext_lazy('in @country', 'Germany')),
            ('AT', pgettext_lazy('in @country', 'Austria')),
            ('CH', pgettext_lazy('in @country', 'Switzerland')),
]
EFA_COUNTRIES_CHOICE_DICT = dict(EFA_COUNTRIES_CHOICE)

EFA_YEARS = [2015, 2016]

CURRENT_YEAR = {
    'AT': 2016,
    'DE': 2016,
    'CH': 2016,
}
FILTER_YEAR = {
    'AT': None,
    'DE': None,
    'CH': None,
}


class EurosfuerAerzteConfig(AppConfig):
    name = 'correctiv_eurosfueraerzte'
    verbose_name = _('Euros for Doctors')
