from __future__ import unicode_literals

from django.contrib import admin
from django.db import models
from django.conf.urls import url
from django.shortcuts import redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import PermissionDenied
from django.utils.html import format_html
from django.contrib import messages
from django.utils import timezone
from django.contrib.admin.filters import SimpleListFilter

from leaflet.admin import LeafletGeoAdmin

from ..models import ZeroDoctor


class NullFilterSpec(SimpleListFilter):
    def lookups(self, request, model_admin):
        return (
            ('1', _('Has value')),
            ('0', _('None')),
        )

    def queryset(self, request, queryset):
        kwargs = {
            '%s' % self.parameter_name: None,
        }
        if self.value() == '0':
            return queryset.filter(**kwargs)
        if self.value() == '1':
            return queryset.exclude(**kwargs)
        return queryset


class RecipientNullFilterSpec(NullFilterSpec):
    title = _('In Euros for Doctors database')
    parameter_name = 'recipient_id'


class LastLoginNullFilterSpec(NullFilterSpec):
    title = _('Logged in')
    parameter_name = 'last_login'


class HasSubmissionsListFilter(admin.SimpleListFilter):
    title = _('Has submissions')

    parameter_name = 'has_submissions'

    def lookups(self, request, model_admin):
        return (
            ('1', _('has submissions')),
            ('0', _('has no submissions')),
        )

    def queryset(self, request, qs):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        qs = qs.annotate(submission_count=models.Count('zerodocsubmission'))
        if self.value() == '0':
            return qs.filter(submission_count=0)
        elif self.value() == '1':
            return qs.filter(submission_count__gt=0)


class ZeroDocSubmissionAdmin(admin.ModelAdmin):
    raw_id_fields = ('payment',)
    date_hierarchy = 'submitted_on'
    list_display = ('zerodoc', 'kind', 'date_year', 'submitted_on', 'confirmed')
    list_filter = ('kind', 'confirmed', 'date')
    search_fields = ('zerodoc__first_name', 'zerodoc__last_name',
                     'zerodoc__email',)

    def date_year(self, obj):
        return obj.date.year
    date_year.short_description = _('Year')


class ZeroDoctorAdmin(LeafletGeoAdmin):
    display_raw = True  # raw geo field
    list_display = ('get_full_name', 'email', 'num_unconfirmed_submissions',
                    'all_submissions_confirmed', 'get_full_address',)
    list_filter = ('country', RecipientNullFilterSpec, HasSubmissionsListFilter,
                    LastLoginNullFilterSpec)
    search_fields = ('first_name', 'last_name', 'email', 'location', 'address',
                     'postcode')
    raw_id_fields = ('recipient',)
    save_on_top = True

    actions = ['export_csv', 'confirm_all']

    def get_urls(self):
        urls = super(ZeroDoctorAdmin, self).get_urls()
        my_urls = [
            url(r'^zerodoc-confirm/$',
                self.admin_site.admin_view(self.confirm_zerodoc_submission),
                name='eurosfueraerzte-zerodocs_confirm'),
        ]
        return my_urls + urls

    def get_full_address(self, obj):
        if not obj.address and not obj.location:
            return '---'
        return format_html('{address}, {postcode} {location} ({country})',
            address=obj.address,
            postcode=obj.postcode,
            location=obj.location,
            country=obj.country
        )
    get_full_address.short_description = _('Address')

    def num_unconfirmed_submissions(self, obj):
        return len(obj.all_submissions_unconfirmed())
    num_unconfirmed_submissions.short_description = _('new submissions')

    def confirm_zerodoc_submission(self, request):
        if not request.method == 'POST':
            raise PermissionDenied
        if not self.has_change_permission(request):
            raise PermissionDenied

        obj = get_object_or_404(ZeroDoctor, pk=request.POST['pk'])

        sub_ids = [int(sub_id) for sub_id in request.POST.getlist('sub_id')]

        try:
            obj.confirm_submissions(sub_ids)
        except ValueError as e:
            messages.add_message(request, messages.ERROR, e)
        else:
            messages.add_message(request, messages.SUCCESS,
                _('Successfully confirmed!'))
        return redirect('admin:correctiv_eurosfueraerzte_zerodoctor_changelist')

    def confirm_all(self, request, queryset):
        if not self.has_change_permission(request):
            raise PermissionDenied

        failed = []
        for obj in queryset:
            sub_ids = [x.pk for x in obj.get_all_submissions()]
            try:
                obj.confirm_submissions(sub_ids)
            except ValueError as e:
                failed.append(str(e))
        if failed:
            failed_message = u', '.join(failed)
            messages.add_message(request, messages.ERROR, _('Failed on these:') + failed_message)
        else:
            messages.add_message(request, messages.SUCCESS,
                _('All successfully confirmed!'))
    confirm_all.short_description = _("Confirm all submissions")

    def export_csv(self, request, queryset):
        from correctiv_community.helpers.csv_utils import export_csv_response

        fields = ('id', 'gender', 'title', 'first_name', 'last_name',
                'email', 'recipient_id',
                'address', 'postcode', 'location', 'country',
                'address_type', 'geo', 'specialisation', 'web',
                'confirmed_on', 'get_absolute_domain_url',
                'get_absolute_recipient_url'
        )
        filename = timezone.now().strftime('zerodocs_%Y%m%d-%H%M.csv')
        return export_csv_response(queryset, fields, name=filename)
    export_csv.short_description = _("Export to CSV")
