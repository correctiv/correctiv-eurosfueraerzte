from rest_framework import serializers, viewsets

from .models import PaymentRecipient
from .forms import PaymentRecipientSearchForm


class PaymentRecipientSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    payments_total = serializers.DecimalField(decimal_places=2, max_digits=19)
    # payments_fees = serializers.DecimalField(decimal_places=2, max_digits=19)

    def to_representation(self, obj):
        result = super(PaymentRecipientSerializer, self).to_representation(obj)
        print('before access')
        result['payments'] = [r.amount for r in obj.pharmapayment_set.all()]
        return result

    class Meta:
        model = PaymentRecipient
        fields = ('first_name', 'last_name',
                  'url',
                  'location', 'postcode',
                  'payments_total',
                #   'payments_fees',
                  )
        #   'payments_registration_fees',
        #   'payments_travel_accommodation',
        #   'payments_total'
        read_only_fields = fields


class PaymentRecipientViewSet(viewsets.ReadOnlyModelViewSet):
    """This viewset automatically provides `list` and `detail` actions."""

    permission_classes = ()
    authentication_classes = ()

    serializer_class = PaymentRecipientSerializer

    def get_queryset(self):
        print('before qs')
        qs = PaymentRecipient.objects.all()
        qs = qs.prefetch_related('pharmapayment_set')
        form = PaymentRecipientSearchForm(self.request.query_params)
        qs = form.search(qs)
        return qs
