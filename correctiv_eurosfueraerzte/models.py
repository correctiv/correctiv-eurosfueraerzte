from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from djorm_pgfulltext.models import SearchManager
from djorm_pgfulltext.fields import VectorField


@python_2_unicode_compatible
class PharmaCompany(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)

    web = models.CharField(max_length=1024, blank=True)

    class Meta:
        verbose_name = _('Pharma Company')
        verbose_name_plural = _('Pharma Companies')
        ordering = ('name',)

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.slug,)

    @models.permalink
    def get_absolute_url(self):
        return ('eurosfueraerzte:eurosfueraerzte-companydetail', (), {
            'slug': self.slug
        })


class DrugManager(SearchManager):
    def search(self, queryset, query):
        if query:
            queryset = queryset.filter(search_index__ft_startswith=query)
        queryset = queryset.annotate(study_count=models.Count('observationalstudy'))
        return queryset

    def get_by_patient_sum(self):
        return self.get_queryset().filter(
                observationalstudy__patient_count__isnull=False
                ).annotate(
                    sum_patients=models.Sum(
                        'observationalstudy__patient_count')
                ).order_by('-sum_patients')

    def get_by_doc_sum(self):
        return self.get_queryset().filter(
                    observationalstudy__doc_count__isnull=False
                ).annotate(
                    doc_sum=models.Sum(
                        'observationalstudy__doc_count')
                ).order_by('-doc_sum')


@python_2_unicode_compatible
class Drug(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)

    active_ingredient = models.CharField(_('active ingredient'),
                                         max_length=512, blank=True)
    medical_indication = models.CharField(_('medical indication'),
                                          max_length=512, blank=True)

    atc_code = models.CharField(max_length=15, blank=True)

    pharma_company = models.ForeignKey(PharmaCompany,
        verbose_name=_('pharma company'),
        on_delete=models.SET_NULL, blank=True, null=True)

    search_index = VectorField()

    objects = DrugManager(
        fields=[
            ('name', 'A'),
            ('active_ingredient', 'B'),
            ('medical_indication', 'C'),
        ],
        config='pg_catalog.german',
        search_field='search_index',
        auto_update_search_field=True
    )

    class Meta:
        verbose_name = _('Drugs')
        verbose_name_plural = _('Drugs')
        ordering = ('name',)

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.slug,)
    natural_key.dependencies = [
            'correctiv_eurosfueraerzte.PharmaCompany']

    @models.permalink
    def get_absolute_url(self):
        return ('eurosfueraerzte:eurosfueraerzte-drugdetail', (), {'slug': self.slug})

    def get_aggregates(self):
        return Drug.objects.filter(pk=self.pk).aggregate(
            sum_patients=models.Sum(
                'observationalstudy__patient_count'),
            sum_doctors=models.Sum(
                'observationalstudy__doc_count'),
            average_fee=models.Avg(
                'observationalstudy__fee_per_patient')
        )


class ObservationalStudyManager(models.Manager):
    def get_by_fee_per_patient(self):
        return self.get_queryset().filter(fee_per_patient__isnull=False
            ).order_by('-fee_per_patient')


@python_2_unicode_compatible
class ObservationalStudy(models.Model):
    drugs = models.ManyToManyField(Drug, verbose_name=_('drugs'))

    drug_title = models.CharField(max_length=1024, blank=True)
    drug_slug = models.SlugField(max_length=1024, blank=True)
    description = models.TextField(blank=True)

    registration_date = models.DateField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    company = models.CharField(_('executing company'),
                               max_length=1024, blank=True)
    sponsor = models.CharField(_('sponsor'),
                               max_length=1024, blank=True)

    patient_count = models.IntegerField(null=True, blank=True)
    doc_count = models.IntegerField(null=True, blank=True)
    fee_per_patient = models.DecimalField(null=True, blank=True,
                                          decimal_places=2, max_digits=19)
    fee_description = models.TextField(blank=True)

    reference = models.CharField(max_length=1024, blank=True)

    objects = ObservationalStudyManager()

    class Meta:
        verbose_name = _('observational study')
        verbose_name_plural = _('observational studies')
        ordering = ('-start_date',)

    def __str__(self):
        return self.drug_title

    def natural_key(self):
        return (self.drug_slug, self.registration_date, self.start_date)
    natural_key.dependencies = [
            'correctiv_eurosfueraerzte.Drug']

    @models.permalink
    def get_absolute_url(self):
        return ('eurosfueraerzte:eurosfueraerzte-studydetail', (), {
            'pk': self.pk,
            'year': self.start_date.year,
            'slug': self.drug_slug
        })

    @property
    def is_running(self):
        if self.end_date is None:
            return True
        now = timezone.now().date()
        if self.end_date > now:
            return True
        return False
