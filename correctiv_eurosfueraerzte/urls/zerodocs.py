from django.conf.urls import url, include
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.clickjacking import xframe_options_exempt

from ..views.zerodocs import (ZeroDocsIndexView, login, EmailSentView,
                              ZeroDocsEntryView, ZeroDocsMapView,
                              get_zerodocs_pdf)


zerodocs_patterns = [
    url(r'^$', ZeroDocsIndexView.as_view(),
        name='eurosfueraerzte-zerodocs_index'),
    url(_(r'^map/$'), xframe_options_exempt(ZeroDocsMapView.as_view()),
        name='eurosfueraerzte-zerodocs_map'),
    # Translators: url slug
    url(_(r'^login/$'), login, name='eurosfueraerzte-zerodocs_login'),
    # Translators: url slug
    url(_(r'^login/email-sent/$'), EmailSentView.as_view(),
        name='eurosfueraerzte-zerodocs_email_sent'),
    # Translators: url slug
    url(_(r'^entry/(?P<slug>\w+)/$'), ZeroDocsEntryView.as_view(),
        name='eurosfueraerzte-zerodocs_entry'),
    # Translators: url slug
    url(_(r'^entry/(?P<slug>\w+)/pdf/$'), get_zerodocs_pdf,
        name='eurosfueraerzte-zerodocs_pdf'),
]

urlpatterns = [
    # Translators: url slug
    url(_(r'^zero-euro/'), include(zerodocs_patterns))
]
