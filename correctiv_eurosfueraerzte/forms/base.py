import re

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D

from ..models import Drug, PharmaCompany, PaymentRecipient, PharmaPayment
from ..apps import EFA_COUNTRIES_CHOICE

LATLNG_RE = re.compile('(\d+\.?\d+),(\d+\.?\d+)')


class PharmaCompanyModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class UpperCaseChoiceField(forms.ChoiceField):
    def to_python(self, value):
        return super(UpperCaseChoiceField, self).to_python(value).upper()


class SearchForm(forms.Form):
    model = Drug

    q = forms.CharField(
        required=False,
        label=_('Search'),
        widget=forms.TextInput(
            attrs={
                'type': 'search',
                'class': 'form-control',
                'placeholder': _('Name of drug')
            }))

    def update_queryset(self, qs):
        return qs

    def finalise_queryset(self, qs):
        return qs

    def search(self, queryset, autocomplete=False):
        if not self.is_valid():
            return queryset

        queryset = self.update_queryset(queryset)

        query = self.cleaned_data['q'].strip()
        if autocomplete:
            qs = self.model.objects.autocomplete(queryset, query)
        else:
            qs = self.model.objects.search(queryset, query)
        qs = self.finalise_queryset(qs)
        return qs

    def autocomplete(self, queryset):
        return self.search(queryset, autocomplete=True)


class PaymentRecipientSearchForm(SearchForm):
    model = PaymentRecipient

    q = forms.CharField(
        required=False,
        label=_('Search'),
        widget=forms.TextInput(
            attrs={
                'type': 'search',
                'class': 'form-control',
                'placeholder': _('Name, city or postcode'),
                'id': 'id_q_doctors'
            }))

    recipient_kind = forms.ChoiceField(choices=(
        ('', _('People and organisations')),
        ('hcp', _('Only people')),
        ('hco', _('Only organisations')),
    ), required=False)

    label = forms.ChoiceField(choices=PharmaPayment.PAYMENT_LABELS,
                              required=False)

    latlng = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    country = UpperCaseChoiceField(
        choices=[
            ('', _('all available countries')),
        ] + EFA_COUNTRIES_CHOICE,
        required=False
    )

    company = PharmaCompanyModelChoiceField(
        required=False,
        queryset=PharmaCompany.objects.all(),
        widget=forms.HiddenInput()
    )

    def clean_latlng(self):
        latlng = self.cleaned_data['latlng']
        if latlng:
            match = LATLNG_RE.match(latlng)
            if match is not None:
                return GEOSGeometry('POINT(%s %s)' % (match.group(2), match.group(1)), srid=4326)
            raise forms.ValidationError("Bad latlng")
        return ''

    def update_queryset(self, qs):
        company = self.cleaned_data['company']
        if company:
            self.company_obj = company
            qs = qs.filter(pharmapayment__pharma_company=company)

        recipient_kind = self.cleaned_data['recipient_kind']
        if recipient_kind:
            qs = qs.filter(kind=PaymentRecipient.KIND_MAPPING[recipient_kind])

        label = self.cleaned_data['label']
        if label:
            self.label_description = PharmaPayment.PAYMENT_LABELS_DICT[label]
            qs = qs.filter(pharmapayment__label=label)
        return qs

    def finalise_queryset(self, qs):
        order_field = '-total_euro'

        country = self.cleaned_data['country']
        if country:
            qs = qs.filter(origin=country)

        qs = qs.order_by(order_field)
        latlng = self.cleaned_data['latlng']
        if latlng:
            qs = qs.annotate(distance=Distance('geo', latlng))
            qs = qs.filter(geo__distance_lte=(latlng, D(km=50)))
            qs = qs.order_by('distance', order_field)
        qs = qs.distinct()
        return qs