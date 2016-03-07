from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import PermissionDenied
from django.db import router
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from django.contrib.admin import helpers

from .models import PharmaCompany, Drug, ObservationalStudy


class PharmaCompanyAdmin(admin.ModelAdmin):
    search_fields = ('name',)


class DrugAdmin(admin.ModelAdmin):
    search_fields = ('name', 'active_ingredient',)
    raw_id_fields = ('pharma_company',)
    list_display = ('name', 'active_ingredient', 'pharma_company')

    actions = ['replace_drugs']

    def replace_drugs(self, request, queryset):
        opts = self.model._meta
        # Check that the user has change permission for the actual model
        if not self.has_change_permission(request):
            raise PermissionDenied

        # User has already chosen
        if request.POST.get('drug_id'):
            real_drug = Drug.objects.get(pk=request.POST.get('drug_id'))
            for study in ObservationalStudy.objects.filter(drugs__in=queryset):
                study.drugs.add(real_drug)
            queryset.delete()
            self.message_user(request, _("Successfully replaced drugs."))
            return None

        db = router.db_for_write(self.model)

        class FakeRel:
            to = Drug
            limit_choices_to = {}

            @classmethod
            def get_related_field(cls):
                class FakeField:
                    name = ''
                return FakeField

        context = {
            'opts': opts,
            'queryset': queryset,
            'media': self.media,
            'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
            'drug_widget': mark_safe(admin.widgets.ForeignKeyRawIdWidget(
                    FakeRel, self.admin_site, using=db).render(
                            'drug_id', None,
                            {'id': 'id_drug_id'})
                            .replace('../../..', '../..')),
            'applabel': opts.app_label
        }

        # Display the confirmation page
        return TemplateResponse(request, 'correctiv_eurosfueraerzte/admin/replace_drugs.html',
            context, current_app=self.admin_site.name)
    replace_drugs.short_description = _('Replace drugs with...')


class ObservationalStudyAdmin(admin.ModelAdmin):
    search_fields = ('drug_title', 'company', 'sponsor')
    raw_id_fields = ('drugs',)
    date_hierarchy = 'start_date'
    list_display = ('drug_title',
        'patient_count', 'doc_count', 'fee_per_patient',
        'registration_date', 'start_date',
        'company', 'sponsor'
    )


admin.site.register(PharmaCompany, PharmaCompanyAdmin)
admin.site.register(Drug, DrugAdmin)
admin.site.register(ObservationalStudy, ObservationalStudyAdmin)
