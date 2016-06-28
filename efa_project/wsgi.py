"""
WSGI config for correctiv_community project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/
"""

import sys
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "efa_project.settings")

project = os.path.dirname(__file__)
workspace = os.path.join(project, '..')
sys.path.append(project)
sys.path.append(workspace)

from django.conf import settings
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

try:
    from whitenoise.django import DjangoWhiteNoise
    application = DjangoWhiteNoise(application)

    if settings.MEDIA_ROOT and settings.MEDIA_URL:
        application.add_files(settings.MEDIA_ROOT, prefix=settings.MEDIA_URL)
except ImportError:
    pass
