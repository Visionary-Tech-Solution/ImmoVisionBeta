from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.models import User


class BrokerSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = User
        fields = ('username', 'email', 'type', 'password', 'token')

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name="New",
            last_name="User",
            type = 'BROKER'
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)
    


class UserSerializerWithToken(serializers.Serializer):
    access_token = serializers.CharField()
