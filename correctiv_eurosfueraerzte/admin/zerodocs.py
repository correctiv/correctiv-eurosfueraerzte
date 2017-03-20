from django.contrib import admin
from django.conf.urls import url
from django.shortcuts import redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import PermissionDenied
from django.utils.html import format_html
from django.contrib import messages

from leaflet.admin import LeafletGeoAdmin

from ..models import ZeroDoctor, ZeroDocSubmission


class ZeroDocSubmissionInlineAdmin(admin.TabularInline):
    model = ZeroDocSubmission
    raw_id_fields = ('payment',)


class ZeroDoctorAdmin(LeafletGeoAdmin):
    inlines = [
        # ZeroDocSubmissionInlineAdmin
    ]

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
        return format_html('{address}<br/>{postcode} {location} ({country})',
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

        years = [int(year) for year in request.POST.getlist('year')]
        if years:
            try:
                obj.confirm_submissions(years)
            except ValueError as e:
                messages.add_message(request, messages.ERROR, e)
            else:
                messages.add_message(request, messages.SUCCESS,
                    _('Successfully confirmed!'))
        return redirect('admin:correctiv_eurosfueraerzte_zerodoctor_changelist')
