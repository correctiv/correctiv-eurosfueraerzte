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

    def search(self, queryset):
        if not self.is_valid():
            return queryset

        query = self.cleaned_data['q'].strip().split()
        query = [q.encode('utf-8') for q in query]
        return Drug.objects.search(queryset, query)
