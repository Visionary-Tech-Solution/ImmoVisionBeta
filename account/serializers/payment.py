from account.models import PaymentMethod
from rest_framework import serializers


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['stripe_customer_id', 'last4', 'exp_month', 'exp_year']