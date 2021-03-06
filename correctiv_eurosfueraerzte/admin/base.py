from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.contrib.admin import helpers

from leaflet.admin import LeafletGeoAdmin

from ..models import Drug, PharmaPayment, ObservationalStudy, PaymentRecipient


class ReplacementMixin(object):
    def replace_objects(self, request, queryset):
        opts = self.model._meta
        # Check that the user has change permission for the actual model
        if not self.has_change_permission(request):
            raise PermissionDenied

        # User has already chosen
        if request.POST.get('object_id'):
            real_obj = self.model.objects.get(pk=request.POST.get('object_id'))
            self.handle_replacement(real_obj, queryset)
            queryset.delete()
            self.message_user(request, _("Successfully replaced objects."))
            return None

        context = {
            'opts': opts,
            'queryset': queryset,
            'media': self.media,
            'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
            'applabel': opts.app_label
        }

        # Display the confirmation page
        return TemplateResponse(request,
            'correctiv_eurosfueraerzte/admin/replace_objects.html', context)
    replace_objects.short_description = _('Replace selected with...')


class PharmaCompanyAdmin(ReplacementMixin, admin.ModelAdmin):
    list_filter = ('country',)
    search_fields = ('name', 'payments_url')

    actions = ['replace_objects']

    def handle_replacement(self, real_object, queryset):
        Drug.objects.filter(pharma_company__in=queryset).update(
                            pharma_company=real_object)
        PharmaPayment.objects.filter(pharma_company__in=queryset).update(
                            pharma_company=real_object)


class DrugAdmin(ReplacementMixin, admin.ModelAdmin):
    search_fields = ('name', 'active_ingredient',)
    raw_id_fields = ('pharma_company',)
    list_display = ('name', 'active_ingredient', 'pharma_company')

    actions = ['replace_objects']

    def handle_replacement(self, real_object, queryset):
        for study in ObservationalStudy.objects.filter(drugs__in=queryset):
            study.drugs.add(real_object)


class ObservationalStudyAdmin(admin.ModelAdmin):
    search_fields = ('drug_title', 'company', 'sponsor')
    raw_id_fields = ('drugs',)
    date_hierarchy = 'start_date'
    list_display = (
        'drug_title', 'patient_count', 'doc_count', 'fee_per_patient',
        'registration_date', 'start_date', 'company', 'sponsor'
    )


class PharmaPaymentInlineAdmin(admin.TabularInline):
    model = PharmaPayment


class PaymentRecipientAdmin(ReplacementMixin, LeafletGeoAdmin):
    inlines = [
        PharmaPaymentInlineAdmin
    ]
    # Display raw input for geo fields
    display_raw = True
    list_display = ('get_full_name', 'address', 'postcode', 'location')
    list_filter = ('kind', 'origin', 'is_zerodoc')
    search_fields = ('first_name', 'name', 'address', 'postcode', 'location')
    save_on_top = True

    actions = ['replace_objects', 'compute_total', 'update_search_vector']

    def handle_replacement(self, real_object, queryset):
        PharmaPayment.objects.filter(recipient__in=queryset).update(
                            recipient=real_object)

    def compute_total(self, request, queryset):
        for obj in queryset:
            try:
                obj.compute_total()
            except ValueError as e:
                self.message_user(request, e)
                break
            obj.save()
        self.message_user(request, _("Successfully computed totals."))

    def update_search_vector(self, request, queryset):
        queryset.update(
                search_vector=PaymentRecipient.objects.get_search_vector())


class PharmaPaymentAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_filter = ('origin', 'label', 'pharma_company',)
    list_display = ('pharma_company', 'recipient', 'date', 'label', 'amount',
                    'origin')
    search_fields = ('recipient__name', 'recipient_detail', 'recipient_kind')
    raw_id_fields = ('recipient',)
