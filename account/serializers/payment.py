from account.models import (FreelancerPaymentMethod, FreelancerProfile,
                            FreelancerWithdraw, PaymentMethod)
from rest_framework import serializers


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['stripe_customer_id', 'last4', 'exp_month', 'exp_year']

class FreelancerPaymentMethodSerializer(serializers.ModelSerializer):
    # freelancer = ProfileSerializer()
    class Meta:
        model = FreelancerPaymentMethod
        fields = '__all__'

    def get_freelancer(self, obj):
        freelancer = obj.freelancer
        username = freelancer.profile.username
        return username


class FreelancerWithdrawSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField(read_only=True)
    withdrawal_type = serializers.SerializerMethodField(read_only=True)
    withdrawal_details = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = FreelancerWithdraw
        fields = ['id', 'username', 'withdrawal_type', 'withdrawal_details', 'withdraw_amount', 'withdraw_status']

    def get_username(self, obj):
        freelancer = obj.withdraw_method.freelancer
        username = freelancer.profile.username
        return username
    def get_withdrawal_type(self, obj):
        withdrawal_type = obj.withdraw_method.withdrawal_type
        return str(withdrawal_type)
    def get_withdrawal_details(self, obj):
        withdraw_method = obj.withdraw_method
        withdrawal_type = withdraw_method.withdrawal_type
        withdrawal_details = None
        if withdrawal_type == "paypal":
            withdrawal_details = withdraw_method.paypal_email
        elif withdrawal_type == "crypto":
            withdrawal_details = withdraw_method.crypto_address
        else:
            withdrawal_details = None
        return str(withdrawal_details)