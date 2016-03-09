import json

from django.views.generic import TemplateView, ListView
from django.views.generic.detail import DetailView
from django.http import HttpResponse, QueryDict
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _

from .models import Drug, ObservationalStudy, PharmaCompany
from .forms import SearchForm


class SearchMixin(object):
    def get_context_data(self, **kwargs):
        context = super(SearchMixin, self).get_context_data(**kwargs)
        context['form'] = SearchForm()
        return context


class IndexView(SearchMixin, TemplateView):
    template_name = 'correctiv_eurosfueraerzte/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['is_index'] = True
        context['top_drugs'] = Drug.objects.get_by_patient_sum()[:10]
        context['highest_paid_studies'] = ObservationalStudy.objects.get_by_fee_per_patient()[:10]
        return context


class SearchView(ListView):
    model = Drug
    paginate_by = 20

    def get_queryset(self):
        qs = super(SearchView, self).get_queryset()
        self.form = SearchForm(self.request.GET)
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
            autocomplete_list = [{'name': o.name, 'url': o.get_absolute_url()}
                                          for o in context['object_list'][:20]]
            return HttpResponse(json.dumps(autocomplete_list),
                                content_type='application/json')
        return super(SearchView, self).render_to_response(context,
                                                          **response_kwargs)


class DrugDetailView(SearchMixin, DetailView):
    model = Drug

    def get_context_data(self, **kwargs):
        context = super(DrugDetailView, self).get_context_data(**kwargs)
        context['aggs'] = self.object.get_aggregates()
        context['title'] = _('Drug %(name)s') % {'name': self.object.name}
        context['description'] = _('Details on how much money doctors got to prescribe %(name)s.') % {'name': self.object.name}
        return context


class ObservationalStudyDetailView(SearchMixin, DetailView):
    model = ObservationalStudy

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


class CompanyDetailView(SearchMixin, DetailView):
    model = PharmaCompany

    def get_context_data(self, **kwargs):
        context = super(CompanyDetailView, self).get_context_data(**kwargs)
        context['drug_list'] = Drug.objects.get_for_company(self.object)
        context['title'] = _('Pharma company  %(name)s') % {
            'name': self.object.name
        }
        context['description'] = _('Details on which drugs where pushed by %(name)s through observational studies.') % {
            'name': self.object.name}
        return context
