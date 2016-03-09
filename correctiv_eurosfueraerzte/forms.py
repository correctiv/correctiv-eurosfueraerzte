from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Drug


class SearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label=_('Search'),
        widget=forms.TextInput(
            attrs={
                'type': 'search',
                'class': 'form-control',
                'placeholder': _('e.g. Avastin')
            }))

    def search(self, queryset, autocomplete=False):
        if not self.is_valid():
            return queryset

        query = self.cleaned_data['q'].strip().split()
        query = [q.encode('utf-8') for q in query]
        if autocomplete:
            return Drug.objects.autocomplete(queryset, query)
        return Drug.objects.search(queryset, query)

    def autocomplete(self, queryset):
        return self.search(queryset, autocomplete=True)
