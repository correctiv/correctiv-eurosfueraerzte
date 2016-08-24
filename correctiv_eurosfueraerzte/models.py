from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Distance
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import HStoreField
from django.contrib.gis.measure import D

from djorm_pgfulltext.models import SearchManager
from djorm_pgfulltext.fields import VectorField, FullTextLookup, startswith
import pandas as pd


class FullTextLookupCustom(FullTextLookup):
    lookup_name = 'ft_search'

    def as_sql(self, qn, connection):
        lhs, lhs_params = qn.compile(self.lhs)
        rhs, rhs_params = self.process_rhs(qn, connection)

        catalog, rhs_params = rhs_params

        cmd = "%s @@ plainto_tsquery('%s', %%s)" % (lhs, catalog)
        rest = (" & ".join(self.transform.__call__(rhs_params)),)

        return cmd, rest


class FullTextLookupCustomStartsWith(FullTextLookupCustom):
    lookup_name = 'ft_search_startswith'

    def transform(self, *args):
        return startswith(*args)

VectorField.register_lookup(FullTextLookupCustom)
VectorField.register_lookup(FullTextLookupCustomStartsWith)


class PharmaCompanyManager(SearchManager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)

    def _get_type_aggregation(self, obj, df, kind, max_amount):
        type_df = df[df['recipient_kind'] == kind]

        label_amounts = type_df.groupby(['individual_recipient', 'label'])['amount'].sum().unstack().iteritems()

        labels = [
            {
                'total': val_row.sum(),
                'top5': (
                    PaymentRecipient.objects.filter(
                        kind=kind, hidden_payments=False
                    ).extra(select={
                        "total_amount": """
                        SELECT COALESCE(SUM(correctiv_eurosfueraerzte_pharmapayment.amount), 0.0) FROM
                        correctiv_eurosfueraerzte_pharmapayment
                        WHERE
                        correctiv_eurosfueraerzte_paymentrecipient.id = correctiv_eurosfueraerzte_pharmapayment.recipient_id AND
                        correctiv_eurosfueraerzte_pharmapayment.pharma_company_id = %s AND
                        correctiv_eurosfueraerzte_pharmapayment.label = %s AND
                        correctiv_eurosfueraerzte_pharmapayment.recipient_kind = %s
                        """},
                        select_params=(obj.id, label, kind),
                        order_by=['-total_amount'])[:5]
                ),
                'label_slug': label,
                'order': PharmaPayment.PAYMENT_LABELS_ORDER.index(label),
                'label': PharmaPayment.PAYMENT_LABELS_DICT[label],
                'individual_percent': round((val_row.get(True, 0) or 0) / val_row.sum() * 100),
                'aggregated_percent': round((val_row.get(False, 0) or 0) / val_row.sum() * 100),
                'vis_individual_percent': round((val_row.get(True, 0) or 0) / max_amount * 100),
                'vis_aggregated_percent': round((val_row.get(False, 0) or 0) / max_amount * 100),
            }
            for label, val_row in label_amounts
            if val_row.sum()
        ]
        labels = sorted(labels, key=lambda x: x['order'])
        totals_ind_agg = type_df.groupby('individual_recipient')['amount'].sum()
        return {
            'total': type_df['amount'].sum(),
            'total_individual_percent': totals_ind_agg.get(True, 0) / max_amount * 100,
            'total_aggregated_percent': totals_ind_agg.get(False, 0) / max_amount * 100,
            'total_individual': totals_ind_agg.get(True, 0),
            'total_aggregated': totals_ind_agg.get(False, 0),
            'labels': labels
        }

    def get_by_payment_sum(self, country=None):
        qs = PharmaCompany.objects.all()

        if country is not None:
            qs = qs.filter(country=country)

        if country is not None:
            qs = qs.annotate(
                amount=models.Sum('pharmapayment__amount'),
                amount_currency=models.Value(
                    PharmaPayment.ORIGIN_CURRENCY[country],
                    output_field=models.CharField())
            )
        else:
            qs = qs.annotate(
                amount=models.Sum('pharmapayment__amount_euro'),
                amount_currency=models.Value(
                    'EUR',
                    output_field=models.CharField())
            )
        qs = qs.filter(amount__isnull=False)
        qs = qs.order_by('-amount')
        return qs

    def get_aggregated_payments(self, obj):
        p = obj.pharmapayment_set.all()

        result = (p.annotate(individual_recipient=models.Case(
                models.When(recipient__isnull=False, then=True), default=False, output_field=models.BooleanField())
            ).values('recipient_kind', 'label', 'individual_recipient')
            .annotate(amount=models.Sum('amount'))
        )

        df = pd.DataFrame(list(result))
        if len(df) == 0:
            return None
        rnd_amount = df[df['label'] == 'research_development']['amount'].sum()

        max_amount = max(rnd_amount, df.groupby('recipient_kind')['amount'].sum().max())
        totals_ind_agg = df.groupby('individual_recipient')['amount'].sum()
        total = df['amount'].sum()
        return {
            'total': total,
            'currency': PharmaPayment.ORIGIN_CURRENCY[obj.country],
            'rnd': rnd_amount,
            'rnd_percent': rnd_amount / max_amount * 100,
            'total_individual_percent': totals_ind_agg.get(True, 0) / total * 100,
            'total_aggregated_percent': totals_ind_agg.get(False, 0) / total * 100,
            'hcp': self._get_type_aggregation(obj, df, 0, max_amount),
            'hco': self._get_type_aggregation(obj, df, 1, max_amount),
        }


@python_2_unicode_compatible
class PharmaCompany(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)

    sub_names = models.TextField(blank=True)

    web = models.CharField(max_length=1024, blank=True)
    payments_url = models.CharField(max_length=1024, blank=True)

    country = models.CharField(max_length=2, default='DE')

    search_index = VectorField()

    objects = PharmaCompanyManager(
        fields=[
            ('name', 'A'),
            ('sub_names', 'B')
        ],
        config='pg_catalog.german',
        search_field='search_index',
        auto_update_search_field=True
    )

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

    def get_sub_names(self):
        return [x for x in self.sub_names.splitlines() if x]


class DrugManager(SearchManager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)

    def search(self, qs, query):
        if query:
            qs = qs.filter(
                models.Q(search_index__ft_search=(self.config, query)) |
                models.Q(pharma_company__search_index__ft_search=(
                    self.config, query
                ))
            )
        qs = self.add_annotations(qs)
        return qs

    def autocomplete(self, qs, query):
        if query:
            query = startswith(query)
            qs = qs.search(' & '.join(query), raw=True)
        return qs

    def get_for_company(self, company):
        qs = self.get_queryset().filter(pharma_company=company)
        qs = self.add_annotations(qs)
        return qs

    def add_annotations(self, queryset):
        return queryset.annotate(
            study_count=models.Count('observationalstudy'))

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
                                       on_delete=models.SET_NULL,
                                       blank=True,
                                       null=True)

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
        return ('eurosfueraerzte:eurosfueraerzte-drugdetail', (),
                {'slug': self.slug})

    def get_aggregates(self):
        aggs = Drug.objects.filter(pk=self.pk).aggregate(
            sum_patients=models.Sum(
                'observationalstudy__patient_count'),
            sum_doctors=models.Sum(
                'observationalstudy__doc_count'),
            total_fee=models.Sum(
                models.F('observationalstudy__patient_count') *
                models.F('observationalstudy__fee_per_patient'),
                output_field=models.DecimalField(decimal_places=2,
                                                 max_digits=19)
            )
        )
        return aggs


class ObservationalStudyManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)

    def get_by_fee_per_patient(self):
        return self.get_queryset().filter(fee_per_patient__isnull=False
                                          ).order_by('-fee_per_patient')


@python_2_unicode_compatible
class ObservationalStudy(models.Model):
    drugs = models.ManyToManyField(Drug, blank=True, verbose_name=_('drugs'))

    slug = models.SlugField(max_length=512, blank=True)
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
        return (self.slug,)
    natural_key.dependencies = [
            'correctiv_eurosfueraerzte.Drug']

    @models.permalink
    def get_absolute_url(self):
        return ('eurosfueraerzte:eurosfueraerzte-studydetail', (), {
            'slug': self.slug
        })

    @property
    def is_running(self):
        if self.end_date is None:
            return True
        now = timezone.now().date()
        if self.end_date > now:
            return True
        return False


class PaymentRecipientManager(SearchManager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)

    def kind_filter(self, qs):
        if self.model.KIND_FILTER is not None:
            qs = qs.filter(kind=self.model.KIND_FILTER)
        return qs

    def get_queryset(self):
        qs = super(PaymentRecipientManager, self).get_queryset()
        return self.kind_filter(qs)

    def search(self, qs, query):
        qs = self.kind_filter(qs)
        if query:
            qs = qs.filter(search_index__ft_search=(self.config, query))
        qs = self.add_annotations(qs)
        return qs

    def autocomplete(self, qs, query):
        if query:
            query = startswith(query)
            qs = qs.search(' & '.join(query), raw=True)
        return qs

    def add_annotations(self, queryset):
        return queryset.annotate(
            payments_total=models.F('total'),
            payments_total_currency=models.F('total_currency')
            # payments_fees=models.Sum(
            #     models.Case(
            #         models.When(
            #             pharmapayment__label='fees', then=models.F('pharmapayment__amount')
            #         ),
            #         default=0, output_field=models.DecimalField(
            #             decimal_places=2, max_digits=19
            #         )
            #     )
            # )
        )

    def get_top_doctors(self, origin=None):
        qs = super(PaymentRecipientManager, self).get_queryset()
        qs = qs.filter(kind=0)
        if origin is None:
            qs = qs.annotate(
                total_amount=models.F('total_euro'),
                total_amount_currency='EUR'
            )
        else:
            qs = qs.filter(origin=origin)
            qs = qs.annotate(
                total_amount=models.F('total'),
                total_amount_currency=models.F('total_currency')
            )
        return qs.order_by('-total_amount')

    def get_by_distance_to_point(self, point, distance=None, include_same=True, only_same=False):
        qs = self.get_queryset()
        if distance is not None:
            qs = qs.filter(geo__distance_lte=(point, D(m=distance)))
        qs = qs.annotate(distance=Distance('geo', point))
        if not include_same:
            qs = qs.filter(distance__gt=0.0)
        if only_same:
            qs = qs.filter(distance=0.0)
        qs = self.add_annotations(qs)
        return qs


MANAGER_KWARGS = dict(
    fields=[
        ('first_name', 'A'),
        ('name', 'A'),
        ('name_detail', 'B'),
        ('related_names', 'B'),
        ('location', 'B'),
        ('postcode', 'B'),
        ('address', 'C'),
        ('orientations', 'C'),
    ],
    config='pg_catalog.german',
    search_field='search_index',
    auto_update_search_field=True
)


@python_2_unicode_compatible
class PaymentRecipient(models.Model):
    KIND_FILTER = None
    KIND_MAPPING = {
        'hcp': 0,
        'hco': 1
    }

    name = models.CharField(max_length=512)
    slug = models.SlugField(max_length=512)
    origin = models.CharField(max_length=2, default='DE', db_index=True)

    kind = models.SmallIntegerField(choices=(
        (0, _('Doctors (HCP)')),
        (1, _('Organisation (HCO)')),
    ))

    name_detail = models.CharField(max_length=255, blank=True)
    related_names = models.TextField(blank=True)

    address = models.CharField(max_length=512, blank=True)
    postcode = models.CharField(max_length=10, blank=True)
    location = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)

    geo = models.PointField(_('Geographic location'), geography=True,
                            blank=True, null=True)

    first_name = models.CharField(max_length=512, blank=True)
    title = models.CharField(max_length=255, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    unique_country_identifier = models.CharField(max_length=255, blank=True)
    orientations = models.CharField(max_length=512, blank=True)

    data = HStoreField(blank=True)

    note = models.TextField(blank=True)
    hidden_payments = models.BooleanField(default=False)

    # aggregates
    total = models.DecimalField(decimal_places=2, max_digits=19, blank=True, null=True)
    total_currency = models.CharField(max_length=3, blank=True)
    total_euro = models.DecimalField(decimal_places=2, max_digits=19, blank=True, null=True)
    company_count = models.SmallIntegerField(blank=True, null=True)

    search_index = VectorField()

    objects = PaymentRecipientManager(**MANAGER_KWARGS)

    class Meta:
        verbose_name = _('payment recipient')
        verbose_name_plural = _('payment recipients')
        ordering = ('name',)

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.slug,)
    natural_key.dependencies = []

    @models.permalink
    def get_absolute_url(self):
        return ('eurosfueraerzte:eurosfueraerzte-recipientdetail', (), {
            'slug': self.slug
        })

    def distance_is_zero(self):
        if not hasattr(self, 'distance'):
            return False
        return self.distance.m == 0

    def get_full_name(self):
        if self.kind == 0:
            gen = (getattr(self, x) for x in ('first_name', 'name'))
            gen = (x for x in gen if x)
            return ' '.join(gen)
        else:
            return self.name
    get_full_name.short_description = _('Name')

    def get_nearby(self, **kwargs):
        if self.geo is None:
            return PaymentRecipient.objects.none()
        return PaymentRecipient.objects.get_by_distance_to_point(
                self.geo, **kwargs)

    def get_aggregates(self, origin=None):
        return {
            'payments_total': self.total,
            'payments_total_currency': self.total_currency
        }


@python_2_unicode_compatible
class Doctor(PaymentRecipient):
    KIND_FILTER = 0

    class Meta:
        proxy = True
        verbose_name = _('medical doctor')
        verbose_name_plural = _('medical doctors')
        ordering = ('name',)

    def __str__(self):
        return self.get_full_name()

    @property
    def last_name(self):
        return self.name


@python_2_unicode_compatible
class HealthCareOrganisation(PaymentRecipient):
    KIND_FILTER = 1

    class Meta:
        proxy = True
        verbose_name = _('healthcare organisation')
        verbose_name_plural = _('healthcare organisations')
        ordering = ('name',)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class PharmaPayment(models.Model):
    ORIGIN_CURRENCY = {
        'DE': 'EUR',
        'AT': 'EUR',
        'CH': 'CHF'
    }
    PAYMENT_LABELS = (
        ('fees', _('fees')),
        ('related_expenses', _('related expenses')),

        ('registration_fees', _('registration fees')),
        ('travel_accommodation', _('travel & accommodation')),

        ('donations_grants', _('donations and grants')),
        ('sponsorship', _('sponsorship')),

        ('research_development', _('Research & development'))
    )
    PAYMENT_LABELS_DICT = dict(PAYMENT_LABELS)
    PAYMENT_LABELS_ORDER = [x[0] for x in PAYMENT_LABELS]

    pharma_company = models.ForeignKey(PharmaCompany, null=True, blank=True)
    recipient = models.ForeignKey(PaymentRecipient, null=True, blank=True)
    date = models.DateField()
    origin = models.CharField(max_length=2, default='DE', db_index=True)

    amount = models.DecimalField(decimal_places=2, max_digits=19)
    currency = models.CharField(max_length=3, default='EUR')

    amount_euro = models.DecimalField(decimal_places=2, max_digits=19, null=True)

    label = models.CharField(max_length=512, blank=True,
                             choices=PAYMENT_LABELS)

    # Only valid for aggregates
    recipient_kind = models.SmallIntegerField(choices=(
            (0, _('Doctors (HCP)')),
            (1, _('Organisation (HCO)')),
            ), null=True, blank=True)
    recipient_detail = models.CharField(max_length=512, blank=True)
    recipient_count = models.IntegerField(null=True, blank=True)

    note = models.TextField(blank=True)

    class Meta:
        verbose_name = _('pharma payment')
        verbose_name_plural = _('pharma payments')
        ordering = ('-amount',)

    def __str__(self):
        return u'%s -> %s: %s (%s)' % (self.pharma_company, self.recipient,
                                       self.amount, self.label)
