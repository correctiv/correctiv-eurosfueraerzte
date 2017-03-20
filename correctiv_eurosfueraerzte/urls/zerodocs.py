from django.conf.urls import url, include
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView

from ..views.zerodocs import (ZeroDocsIndexView, login, ZeroDocsEntryView,
                              get_zerodocs_pdf)


zerodocs_patterns = [
    url(r'^$', ZeroDocsIndexView.as_view(), name='eurosfueraerzte-zerodocs_index'),
    url(r'^login/$', login, name='eurosfueraerzte-zerodocs_login'),
    # Translators: url slug
    url(r'^login/%s/$' % _('email-sent'), TemplateView.as_view(
        template_name='correctiv_eurosfueraerzte/zerodocs/email_sent.html'),
        name='eurosfueraerzte-zerodocs_email_sent'),
    # Translators: url slug
    url(r'^%s/(?P<slug>\w+)/$' % _('entry'), ZeroDocsEntryView.as_view(),
        name='eurosfueraerzte-zerodocs_entry'),
    url(r'^%s/(?P<slug>\w+)/pdf/$' % _('entry'), get_zerodocs_pdf,
        name='eurosfueraerzte-zerodocs_pdf'),
]

urlpatterns = [
    # Translators: url slug
    url(r'^%s/' % _('zero-euro'), include(zerodocs_patterns))
]
