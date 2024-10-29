from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer,TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import send_verification_email
from . models import *
from Profiles.models import Profile


User = get_user_model()


class UserModelSerializer(serializers.ModelSerializer):
    password= serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name', 'password']

    def create(self, validated_data):
        if validated_data:
            user = User.objects.create(username=validated_data['username'],email=validated_data['email'],full_name=validated_data['full_name'])
         
            user.set_password(validated_data['password'])
            user.save()
            profile = Profile.objects.create(user=user)
            profile.save()
            return user
        

            
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, data):
        data  = super().validate(data)
        user = self.user
        if not user.email_verified:
            send_verification_email(user)
            raise serializers.ValidationError("Email is not verified.")
        if user.banned:
            raise serializers.ValidationError("User is banned.")
        user_status = "admin"if user.is_superuser else "staff" if user.is_staff else "normal"
        data.update({
        'user': {
            'id': user.id,
            'username':user.username,
            'full_name': user.full_name,
            'email': user.email,
            'user_status': user_status,      
        }
    })
        return data

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):

        if 'refresh' not in attrs:
            raise serializers.ValidationError("Refresh token is required.")
        
       
        data = super().validate(attrs)
        
      
        refresh_token = RefreshToken(attrs['refresh'])
        
   
        user_id = refresh_token['user_id']
        user = User.objects.get(id=user_id)
        if user.banned:
            raise serializers.ValidationError("User is banned.")
        
        
        user_status = "admin" if user.is_superuser else "staff" if user.is_staff else "normal"
        data.update({
            'user': {
            'id': user.id,
            'username':user.username,
            'full_name': user.full_name,
            'email': user.email,
            'user_status': user_status,      
        }
        })
        return data
    
