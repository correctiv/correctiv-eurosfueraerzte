import re

from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.db.models.functions import Distance

from .models import Drug, PharmaCompany, PaymentRecipient, PharmaPayment

LATLNG_RE = re.compile('(\d+\.?\d+),(\d+\.?\d+)')


class PharmaCompanyModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


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

        query = self.cleaned_data['q'].strip().split()
        query = [q.encode('utf-8') for q in query]
        if autocomplete:
            qs = self.model.objects.autocomplete(queryset, query)
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
        ('hcp', _('Healthcare Professionals')),
        ('hco', _('Healthcare Organisations')),
    ), required=False)

    label = forms.ChoiceField(choices=PharmaPayment.PAYMENT_LABELS,
                              required=False)

    latlng = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
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
            qs = qs.filter(pharmapayment__label=label)
        return qs

    def finalise_queryset(self, qs):
        order_field = '-total'
        # company = self.cleaned_data['company']
        # label = self.cleaned_data['label']
        # if company or label:
        #     qs = qs.annotate(computed_total=models.Sum('pharmapayment__amount'))
        #     order_field = '-computed_total'

        qs = qs.order_by(order_field)
        latlng = self.cleaned_data['latlng']
        if latlng:
            qs = qs.annotate(distance=Distance('geo', latlng))
            qs = qs.order_by('distance', order_field)
        return qs
