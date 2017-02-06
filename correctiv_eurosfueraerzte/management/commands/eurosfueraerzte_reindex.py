from django.core.management.base import BaseCommand
from django.utils import translation
from django.conf import settings

from ...models import Drug, PharmaCompany, PaymentRecipient


class Command(BaseCommand):
    help = "Reindex search vectors"

    def handle(self, *args, **options):
        translation.activate(settings.LANGUAGE_CODE)

        Drug.objects.update_search_index()
        PharmaCompany.objects.update_search_index()
        PaymentRecipient.objects.update_search_index()
