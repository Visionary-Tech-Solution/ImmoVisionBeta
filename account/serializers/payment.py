from account.models import (FreelancerPaymentMethod, FreelancerWithdraw,
                            PaymentMethod, Profile)
from rest_framework import serializers


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['stripe_customer_id', 'last4', 'exp_month', 'exp_year']
    



class ProfileShortSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)
    user_type = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Profile
        fields = ['id', 'full_name', 'profile_pic', 'email', 'user_type' ]
    def get_full_name(self, obj):
        name = f"{obj.user.first_name} {obj.user.last_name}"
        return name
    def get_user_type(self, obj):
        user_type = obj.user.type
        return user_type

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
    profile = serializers.SerializerMethodField(read_only=True)
    withdrawal_type = serializers.SerializerMethodField(read_only=True)
    withdrawal_details = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = FreelancerWithdraw
        fields = ['id', 'profile', 'withdrawal_type', 'withdrawal_details', 'withdraw_amount', 'withdraw_status']

    def get_profile(self, obj):
        freelancer = obj.withdraw_method.freelancer
        profile = freelancer.profile
        serializer = ProfileShortSerializer(profile, many=False)
        return serializer.data
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