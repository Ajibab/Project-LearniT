##-import libraries-##
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import Token

##--imports from the model class-##
from .models import User,UserProfile,PendingUser,Token

##--create the user serializer--##
class ObtainTokenSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        access_token = refresh.access_token
        self.user.save_last_login()
        data["refresh"] = str(refresh)
        data["access"] = str(access_token)
        return data
    
    @classmethod
    def get_token(cls, user: User) -> Token:
        if user.is_flagged:
            raise exceptions.AuthenticationFailed(_("Contact Admin"),code="authentication"
                                                  )
        token = super().get_token(user)
        token.id = user.id
        token["first_name"] = user.first_name
        token["email"] = user.email
        return token

class ChangePasswordSerializer(serializers.ModelSerializer):
    new_password_1 = serializers.CharField(max_length=120,write_only=True,required=True,min_length=6)
    new_password_2 = serializers.CharField(max_length=120,write_only=True,required=True,min_length=6)
    old_password = serializers.CharField(max_length=120, write_only=True,required=True,min_length=6)

    class Meta:
        model = User
        fields = ('new_password_1','new_password_2','old_pasword')

    def validate_password(self, attrs):
        if attrs['new_password_1'] != attrs['new_password_2']:
            raise serializers.ValidationError({"password":"enter correct password"})
        
        return attrs
    
    def validate_old_password(self,value):
        user_request = self.context['request'].user
        if not user_request.check_password(value):
            raise serializers.ValidationError({"old_password": "Old password is not correct"})
        return value
    
    def save(self):
        user: User = self.context["request"].user
        new_password_1 = self.validated_data["new_password"]
        user.set_password(new_password_1)
        user.save(update_fields=["password"])
