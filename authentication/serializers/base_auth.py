from account.models import IpAddress
from authentication.models import User
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken


class UserCreationSerializer(serializers.ModelSerializer):
    isAdmin = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username','first_name', 'last_name', 'email', 'type' ,'isAdmin']
    
    def get_isAdmin(self, obj):
        return obj.is_staff

class UserSerializerWithToken(UserCreationSerializer):
    token = serializers.SerializerMethodField(read_only=True)
    username = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username','email', 'isAdmin', 'type', 'token']
    
    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)
    def get_username(self, obj):
        return obj.username
    

class IpAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = IpAddress
        fields = '__all__'
