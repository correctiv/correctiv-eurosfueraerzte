from rest_framework import serializers, viewsets

from .models import PaymentRecipient
from .forms import PaymentRecipientSearchForm


class PaymentRecipientSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)

    def to_representation(self, obj):
        result = super(PaymentRecipientSerializer, self).to_representation(obj)
        result['full_name'] = obj.get_full_name()
        return result

    class Meta:
        model = PaymentRecipient
        fields = ('name', 'first_name',
                  'url',
                  'address', 'location', 'postcode',
                  'total', 'company_count'
                  )
        read_only_fields = fields


class PaymentRecipientViewSet(viewsets.ReadOnlyModelViewSet):
    """This viewset automatically provides `list` and `detail` actions."""

    permission_classes = ()
    authentication_classes = ()

    serializer_class = PaymentRecipientSerializer

    def get_queryset(self):
        qs = PaymentRecipient.objects.all()
        form = PaymentRecipientSearchForm(self.request.query_params)
        qs = form.search(qs)
        return qs
