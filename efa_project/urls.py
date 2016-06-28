from django.conf.urls import include, url

urlpatterns = [
    url(r'^recherchen/euros-fuer-aerzte/datenbank/', include('correctiv_eurosfueraerzte.urls', namespace='eurosfueraerzte')),

    url(r'^eurosfueraerzte/api/', include('correctiv_eurosfueraerzte.api_urls', namespace='eurosfueraerzte')),
]
