from django.conf.urls import url, include
from django.utils.translation import ugettext_lazy as _

try:
    # Optional caching decorator
    from correctiv_community.helpers.cache_utils import cache_page_anonymous as c
except ImportError:
    c = lambda x: x

from .views import (IndexView, SearchView, RecipientSearchView, DrugDetailView,
                    RecipientDetailView, ObservationalStudyDetailView, CompanyDetailView)
from . import api_urls


urlpatterns = [
    url(r'^$', c(IndexView.as_view()), name='eurosfueraerzte-index'),
    url(_(r'^search/$'), SearchView.as_view(), name='eurosfueraerzte-search'),
    url(_(r'^search/json/$'), SearchView.as_view(),
        {'json': True}, name='eurosfueraerzte-search_json'),
    url(_(r'^recipient-search/$'), RecipientSearchView.as_view(),
        name='eurosfueraerzte-recipientsearch'),

    url(_(r'^recipient/(?P<slug>[\w-]+)/$'), RecipientDetailView.as_view(),
        name='eurosfueraerzte-recipientdetail'),

    url(_(r'^drug/(?P<slug>[\w-]+)/$'), DrugDetailView.as_view(),
        name='eurosfueraerzte-drugdetail'),
    url(_(r'^study/(?P<year>\d{4,})/(?P<pk>\d+)/(?P<slug>[\w-]+)/$'),
        ObservationalStudyDetailView.as_view(),
        name='eurosfueraerzte-studydetail'),
    url(_(r'^company/(?P<slug>[\w-]+)/$'),
        c(CompanyDetailView.as_view()),
        name='eurosfueraerzte-companydetail'),
    # url(r'^api/', include(api_urls)),
]
