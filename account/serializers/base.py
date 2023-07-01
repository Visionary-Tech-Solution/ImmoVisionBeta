from account.models import Profile
from account.serializers.payment import PaymentMethod, PaymentMethodSerializer
from rest_framework import serializers


class ProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)
    user_type = serializers.SerializerMethodField(read_only=True)
    is_admin = serializers.SerializerMethodField(read_only=True)
    payment_info = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Profile
        # fields = '__all__'
        fields = ['id', 'full_name', 'profile_pic', 'phone_number', 'username','email',  'address', 'user_type', 'payment_info', 'is_admin']
    
    def get_full_name(self, obj):
        name = f"{obj.user.first_name} {obj.user.last_name}"
        return name
    
    def get_user_type(self, obj):
        user_type = obj.user.type
        return user_type
    
    def get_is_admin(self, obj):
        is_admin = obj.user.is_staff
        return is_admin
    
    def get_payment_info(self, obj):
        profile = obj
        payment_method_qs = PaymentMethod.objects.filter(profile__username=profile.username)
        payment_method = payment_method_qs.first()
        customer_id = payment_method.stripe_customer_id
        payment_info = None
        if customer_id is not None and len(customer_id) > 0:
            serializer = PaymentMethodSerializer(payment_method, many=False)
            payment_info = serializer.data
        return payment_info