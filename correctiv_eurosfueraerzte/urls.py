from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from .views import (IndexView, SearchView, DrugDetailView,
                    ObservationalStudyDetailView, CompanyDetailView)


urlpatterns = [
    url(r'^$', IndexView.as_view(), name='eurosfueraerzte-index'),
    url(_(r'^search/$'), SearchView.as_view(), name='eurosfueraerzte-search'),
    url(_(r'^drug/(?P<slug>[\w-]+)/$'), DrugDetailView.as_view(),
        name='eurosfueraerzte-drugdetail'),
    url(_(r'^study/(?P<year>\d{4,})/(?P<pk>\d+)/(?P<slug>[\w-]+)/$'),
        ObservationalStudyDetailView.as_view(),
        name='eurosfueraerzte-studydetail'),
    url(_(r'^company/(?P<slug>[\w-]+)/$'),
        CompanyDetailView.as_view(),
        name='eurosfueraerzte-companydetail'),

]
