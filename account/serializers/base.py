from rest_framework import serializers

from account.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)
    user_type = serializers.SerializerMethodField(read_only=True)
    is_admin = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Profile
        # fields = '__all__'
        fields = ['id', 'full_name', 'profile_pic', 'username','email',  'address', 'user_type', 'is_admin']
    
    def get_full_name(self, obj):
        name = f"{obj.user.first_name} {obj.user.last_name}"
        return name
    
    def get_user_type(self, obj):
        user_type = obj.user.type
        return user_type
    
    def get_is_admin(self, obj):
        is_admin = obj.user.is_staff
        return is_admin