from django.contrib import admin
from django.conf.urls import url
from django.shortcuts import redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import PermissionDenied
from django.utils.html import format_html
from django.contrib import messages

from leaflet.admin import LeafletGeoAdmin

from ..models import ZeroDoctor


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
    list_display = ('get_full_name', 'email', 'get_full_address',)
    list_filter = ('country',)
    search_fields = ('first_name', 'last_name', 'email', 'location', 'address',
                     'postcode')
    raw_id_fields = ('recipient',)
    save_on_top = True

    def get_urls(self):
        urls = super(ZeroDoctorAdmin, self).get_urls()
        my_urls = [
            url(r'^zerodoc-confirm/$',
                self.admin_site.admin_view(self.confirm_zerodoc_submission),
                name='eurosfueraerzte-zerodocs_confirm'),
        ]
        return my_urls + urls

    def get_full_address(self, obj):
        return format_html('{address}, {postcode} {location} ({country})',
            address=obj.address,
            postcode=obj.postcode,
            location=obj.location,
            country=obj.country
        )
    get_full_address.short_description = _('Address')

    def confirm_zerodoc_submission(self, request):
        if not request.method == 'POST':
            raise PermissionDenied
        if not self.has_change_permission(request):
            raise PermissionDenied

        obj = get_object_or_404(ZeroDoctor, pk=request.POST['pk'])

        sub_ids = [int(sub_id) for sub_id in request.POST.getlist('sub_id')]
        if sub_ids:
            try:
                obj.confirm_submissions(sub_ids)
            except ValueError as e:
                messages.add_message(request, messages.ERROR, e)
            else:
                messages.add_message(request, messages.SUCCESS,
                    _('Successfully confirmed!'))
        return redirect('admin:correctiv_eurosfueraerzte_zerodoctor_changelist')
