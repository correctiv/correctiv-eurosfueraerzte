from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

EFA_COUNTRIES = [
            ('DE', _('Germany')),
            ('AT', _('Austria')),
            ('CH', _('Switzerland')),
]


class EurosfuerAerzteConfig(AppConfig):
    name = 'correctiv_eurosfueraerzte'
    verbose_name = _('Euros for Doctors')
