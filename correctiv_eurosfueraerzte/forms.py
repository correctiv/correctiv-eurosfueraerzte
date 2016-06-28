from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Drug, PharmaCompany, Doctor


class SearchForm(forms.Form):
    model = Drug

    q = forms.CharField(
        required=False,
        label=_('Search'),
        widget=forms.TextInput(
            attrs={
                'type': 'search',
                'class': 'form-control',
                'placeholder': _('e.g. Avastin')
            }))

    def update_queryset(self, qs):
        return qs

    def search(self, queryset, autocomplete=False):
        if not self.is_valid():
            return queryset

        queryset = self.update_queryset(queryset)

        query = self.cleaned_data['q'].strip().split()
        query = [q.encode('utf-8') for q in query]
        if autocomplete:
            return self.model.objects.autocomplete(queryset, query)
        return self.model.objects.search(queryset, query)

    def autocomplete(self, queryset):
        return self.search(queryset, autocomplete=True)


class DoctorSearchForm(SearchForm):
    model = Doctor

    q = forms.CharField(
        required=False,
        label=_('Search'),
        widget=forms.TextInput(
            attrs={
                'type': 'search',
                'class': 'form-control',
                'placeholder': _('Name or Postcode'),
                'id': 'id_q_doctors'
            }))

    company = forms.ModelChoiceField(
        required=False,
        queryset=PharmaCompany.objects.all(),
        widget=forms.HiddenInput()
    )

    def update_queryset(self, qs):
        company = self.cleaned_data['company']
        if company:
            qs = qs.filter(doctor__pharmapayment__pharma_company=company)
        return qs
