from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from . import api_views


# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'doctors', api_views.DoctorViewSet,
                base_name='eurosfueraerzte')

# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls))
]