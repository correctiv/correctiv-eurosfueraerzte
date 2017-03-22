# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.views.generic import TemplateView, ListView
from django.views.generic.detail import DetailView
from django.http import HttpResponse, QueryDict
from django.shortcuts import redirect
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from ..models import Drug, ObservationalStudy, PharmaCompany, PaymentRecipient
from ..forms import SearchForm, PaymentRecipientSearchForm
from ..apps import EFA_COUNTRIES_DICT, EFA_COUNTRIES_CHOICE_DICT, EFA_COUNTRIES


def get_origin_include(origin, filename):
    return 'correctiv_eurosfueraerzte/%s/%s' % (origin, filename)


class LocaleIncludeDict(object):
    def __init__(self, origin):
        self.origin = origin

    def __getattr__(self, key):
        return get_origin_include(self.origin, '_%s.html' % key)


class LocaleMixin(object):
    DEFAULT_LOCALE = 'DE'
    HAS_AGGREGATES = {
        'DE': True,
        'CH': False,
        'AT': True
    }
    TITLES = {
        'de': _('Euros for Doctors'),
        'ch': _('Money for Doctors'),
        'at': _('Euros for Doctors'),
    }

    def get_context_data(self, **kwargs):
        context = super(LocaleMixin, self).get_context_data(**kwargs)
        country = self.get_country()
        fallback_country = country
        if not country:
            fallback_country = self.DEFAULT_LOCALE
        country_lower = fallback_country.lower()
        context['country'] = country
        context['countries'] = EFA_COUNTRIES
        context['country_label'] = EFA_COUNTRIES_DICT.get(country)
        context['country_label_choice'] = EFA_COUNTRIES_CHOICE_DICT.get(country)
        context['filter_country'] = self.get_country()
        current_lang = translation.get_language()
        context['locale'] = '%s_%s' % (current_lang, fallback_country)
        context['project_title'] = self.TITLES.get(country_lower)
        context['includes'] = LocaleIncludeDict(country_lower)
        context['has_aggregates'] = self.HAS_AGGREGATES.get(country)
        return context


class SearchMixin(object):

    def get_context_data(self, **kwargs):
        context = super(SearchMixin, self).get_context_data(**kwargs)
        context['form'] = SearchForm()
        context['recipient_form'] = PaymentRecipientSearchForm()
        return context


class IndexView(LocaleMixin, SearchMixin, TemplateView):
    template_name = 'correctiv_eurosfueraerzte/index.html'

    def get_country(self):
        return self.kwargs.get('country', 'de').upper()

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        country = self.get_country()
        context['recipient_form'] = PaymentRecipientSearchForm(initial={
            'country': self.get_country()
        })
        context['is_index'] = True
        context['top_drugs'] = Drug.objects.get_by_patient_sum()[:5]
        context['highest_paid_studies'] = ObservationalStudy.objects.get_by_fee_per_patient()[:5]
        context['top_companies'] = PharmaCompany.objects.get_by_payment_sum(country)[:5]
        context['top_doctors'] = PaymentRecipient.objects.get_top_doctors(country)[:5]
        return context


class SearchView(ListView):
    model = Drug
    search_form = SearchForm
    paginate_by = 20

    def get_search_form(self):
        return self.search_form(self.request.GET)

    def get_queryset(self):
        qs = super(SearchView, self).get_queryset()
        self.form = self.get_search_form()
        if not self.form.is_valid():
            return qs
        if self.kwargs.get('json'):
            result = self.form.autocomplete(qs)
        else:
            result = self.form.search(qs)
        return result

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        context['form'] = self.form
        context['query'] = self.request.GET.get('q', '')
        no_page_query = QueryDict(self.request.GET.urlencode().encode('utf-8'),
                                  mutable=True)
        no_page_query.pop('page', None)
        context['getvars'] = no_page_query.urlencode()
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.kwargs.get('json'):
            autocomplete_list = [
                {'name': o.name,
                 'url': o.get_absolute_url()}
                for o in context['object_list'][:20]]
            return HttpResponse(json.dumps(autocomplete_list),
                                content_type='application/json')
        return super(SearchView, self).render_to_response(context,
                                                          **response_kwargs)


class RecipientSearchView(LocaleMixin, SearchView):
    model = PaymentRecipient
    search_form = PaymentRecipientSearchForm
    ordering = '-total_euro'

    def get_country(self):
        form = self.form
        if form.cleaned_data:
            return form.cleaned_data['country']
        return ''

    def get_context_data(self, **kwargs):
        context = super(RecipientSearchView, self).get_context_data(**kwargs)
        context['recipient_form'] = context['form']
        return context


class RecipientDetailView(LocaleMixin, SearchMixin, DetailView):
    model = PaymentRecipient

    def get_country(self):
        return self.object.origin

    def get_template_names(self):
        if self.object.is_zerodoc:
            return ['correctiv_eurosfueraerzte/zerodocs/detail.html']
        return ['correctiv_eurosfueraerzte/paymentrecipient_detail.html']

    def get_meta_info(self, context):
        if self.object.is_zerodoc and not context['payments']:
            return {
                'title': _('%(name)s does not take money from the pharma industry') % {
                    'name': self.object.get_full_name()
                },
                'description': _("Details on why %(name)s doesn't take money from pharma companies.") % {
                    'name': self.object.get_full_name()
                },
                'project_title': _('Project “Zero Euro Doctors”')
            }
        return {
            'title': _('%(name)s and money from the pharma industry') % {
                'name': self.object.get_full_name()
            },
            'description': _('Details on how much money %(name)s got from pharma companies.') % {
                'name': self.object.get_full_name()
            }
        }

    def get_context_data(self, **kwargs):
        context = super(RecipientDetailView, self).get_context_data(**kwargs)
        context['aggs'] = self.object.get_aggregates()
        context['payments'] = self.object.pharmapayment_set.all()
        if self.object.geo:
            context['same_address_objects'] = (self.object
                    .get_nearby(only_same=True)
                    .exclude(pk=self.object.pk)
                    .order_by('-payments_total')[:5]
            )
            context['nearby_objects'] = (self.object
                    .get_nearby(include_same=False)
                    .order_by('distance')[:5]
            )

        context.update(self.get_meta_info(context))
        return context


class DrugDetailView(SearchMixin, DetailView):
    model = Drug

    def get_country(self):
        return self.kwargs.get('country', 'de').upper()

    def get_context_data(self, **kwargs):
        context = super(DrugDetailView, self).get_context_data(**kwargs)
        context['aggs'] = self.object.get_aggregates()
        context['title'] = _('Drug %(name)s') % {'name': self.object.name}
        context['description'] = _('Details on how much money doctors got to prescribe %(name)s.') % {'name': self.object.name}
        return context


class ObservationalStudyDetailView(SearchMixin, DetailView):
    model = ObservationalStudy

    def get_country(self):
        return self.kwargs.get('country', 'de').upper()

    def get(self, request, *args, **kwargs):
        response = super(ObservationalStudyDetailView, self).get(request, *args, **kwargs)
        object_url = self.object.get_absolute_url()
        if object_url != self.request.get_full_path():
            return redirect(object_url)
        return response

    def get_context_data(self, **kwargs):
        context = super(ObservationalStudyDetailView, self).get_context_data(**kwargs)
        context['title'] = _('Observational Study  %(title)s') % {
            'title': self.object.drug_title
        }
        context['description'] = _('Details on the observational study %(title)s.') % {
            'title': self.object.drug_title}
        return context


class CompanyDetailView(LocaleMixin, SearchMixin, DetailView):
    model = PharmaCompany

    def get_country(self):
        return self.object.country

    def get_context_data(self, **kwargs):
        context = super(CompanyDetailView, self).get_context_data(**kwargs)
        context['drug_list'] = Drug.objects.get_for_company(self.object)

        context['payments'] = PharmaCompany.objects.get_aggregated_payments(self.object)

        context['title'] = _('Pharma company  %(name)s') % {
            'name': self.object.name
        }
        context['description'] = _('Details on how money from %(name)s goes to doctors and observational studies.') % {
            'name': self.object.name}
        return context