from django.views.generic import TemplateView, ListView
from django.views.generic.detail import DetailView
from django.http import QueryDict
from django.shortcuts import redirect

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
        context['top_drugs'] = Drug.objects.get_by_patient_sum()[:10]
        context['highest_paid_studies'] = ObservationalStudy.objects.get_by_fee_per_patient()[:10]
        return context


class SearchView(ListView):
    model = Drug
    paginate_by = 20

    def get_queryset(self):
        qs = super(SearchView, self).get_queryset()
        self.form = SearchForm(self.request.GET)
        result = self.form.search(qs)
        return result

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        context['form'] = self.form
        no_page_query = QueryDict(self.request.GET.urlencode().encode('utf-8'), mutable=True)
        no_page_query.pop('page', None)
        context['getvars'] = no_page_query.urlencode()

        return context


class DrugDetailView(SearchMixin, DetailView):
    model = Drug

    def get_context_data(self, **kwargs):
        context = super(DrugDetailView, self).get_context_data(**kwargs)
        context['aggs'] = self.object.get_aggregates()
        return context


class ObservationalStudyDetailView(SearchMixin, DetailView):
    model = ObservationalStudy

    def get(self, request, *args, **kwargs):
        response = super(ObservationalStudyDetailView, self).get(request, *args, **kwargs)
        object_url = self.object.get_absolute_url()
        if object_url != self.request.get_full_path():
            return redirect(object_url)
        return response


class CompanyDetailView(SearchMixin, DetailView):
    model = PharmaCompany
