from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _


class EurosFuerAerzteApp(CMSApp):
    name = _('Euros for Doctors')
    app_name = 'eurosfueraerzte'
    urls = ['correctiv_eurosfueraerzte.urls']


apphook_pool.register(EurosFuerAerzteApp)
