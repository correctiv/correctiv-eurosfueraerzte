from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .models import Drug


@plugin_pool.register_plugin
class EurosForDoctorsSearchTilePlugin(CMSPluginBase):
    module = _("Euros for Doctors")
    name = _('Search Tile')
    render_template = "correctiv_eurosfueraerzte/plugins/search_tile.html"

    def render(self, context, instance, placeholder):
        """
        Update the context with plugin's data
        """
        context['top_drugs'] = Drug.objects.get_by_patient_sum()[:3]
        return context
