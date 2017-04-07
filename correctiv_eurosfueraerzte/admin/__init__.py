from django.contrib import admin

from ..models import (PharmaCompany, Drug, ObservationalStudy,
                     PaymentRecipient, PharmaPayment, ZeroDoctor,
                     ZeroDocSubmission)
from .base import (PharmaCompanyAdmin, DrugAdmin, ObservationalStudyAdmin,
                   PaymentRecipientAdmin, PharmaPaymentAdmin)
from .zerodocs import ZeroDoctorAdmin, ZeroDocSubmissionAdmin

admin.site.register(PharmaCompany, PharmaCompanyAdmin)
admin.site.register(Drug, DrugAdmin)
admin.site.register(ObservationalStudy, ObservationalStudyAdmin)
admin.site.register(PaymentRecipient, PaymentRecipientAdmin)
admin.site.register(PharmaPayment, PharmaPaymentAdmin)
admin.site.register(ZeroDoctor, ZeroDoctorAdmin)
admin.site.register(ZeroDocSubmission, ZeroDocSubmissionAdmin)
