from django.contrib.sitemaps import Sitemap

from .models import Drug, ObservationalStudy, PharmaCompany


def update_sitemap(sitemap_dict):
    sitemap_dict.update({
        'eurosfueraerzte-drugs': DrugSitemap,
        'eurosfueraerzte-observationalstudy': ObservationalStudySitemap,
        'eurosfueraerzte-pharmacompany': PharmaCompanySitemap
    })
    return sitemap_dict


class PharmaCompanySitemap(Sitemap):
    priority = 0.25
    changefreq = 'yearly'

    def items(self):
        """
        Return published entries.
        """
        return PharmaCompany.objects.all()


class DrugSitemap(Sitemap):
    priority = 0.25
    changefreq = 'yearly'

    def items(self):
        """
        Return published entries.
        """
        return Drug.objects.all()


class ObservationalStudySitemap(Sitemap):
    priority = 0.25
    changefreq = 'yearly'

    def items(self):
        """
        Return published entries.
        """
        return ObservationalStudy.objects.all()
