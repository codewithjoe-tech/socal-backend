from django.shortcuts import redirect
from rest_framework.views import APIView
from . serializers import *
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
import secrets      
import urllib.parse
import requests
from dotenv import load_dotenv
import os
from . utils import verify_email
from .tasks import send_mails_to_users


load_dotenv()

frontend = "https://friendbook.codewithjoe.in"
User = get_user_model()

class PublicApi(APIView):
    permission_classes = ()
    authentication_classes = ()


class UserView(PublicApi):
   
    def post(self, request):
        if request.data :
            serializer = UserModelSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                user = serializer.instance
                send_mails_to_users.delay(user.id)
                return Response({"message":"User created successfully"}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer


class GoogleLogin(PublicApi):
    def get(self,request):
        google_client_id = settings.GOOGLE_CLIENT_ID
        redirect_uri = f"{frontend}/auth/google/callback/"
        scope = "https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile"
        state = secrets.token_urlsafe(16)
        params = {
            'client_id': google_client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            "scope": scope,
            'state': state,
            'access_type':'offline',
            "prompt":"select_account"
        }
        print(redirect_uri)
       
        url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
        return redirect(url)


class GoogleCallback(PublicApi):
    def post(self,request, *args,**kwargs):
        code = request.data.get('code')
        state = request.data.get('state')
        error = request.data.get('error')
        request.session.pop('oauth_token',None)
        print(code , state)
        print(error)
        if error or not state :
            return Response({'error': 'Authentication failed!'}, status=status.HTTP_400_BAD_REQUEST)
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "code":code,
            "client_id":settings.GOOGLE_CLIENT_ID,
            "client_secret":settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri":f"{frontend}/auth/google/callback/",
            "grant_type":"authorization_code"
        }
        token_response = requests.post(token_url,data=token_data)
        print(token_response.json())
        token_json = token_response.json()
        access_token = token_json.get('access_token')

      
       

        user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        user_info_params ={"access_token":access_token}
        user_info_response = requests.get(user_info_url,params=user_info_params)
        user_info = user_info_response.json()
        print(user_info)


        email = str(user_info.get('email'))
        full_name = user_info.get('name')
        print(email)
        
        username = email.split('@')[0]


        user, created = User.objects.get_or_create(email=email, defaults={
            'username': username,
            'full_name': full_name,
            "email_verified": True
        })
        user.email_verified = True

        if created:
            user.set_unusable_password()
            profile = Profile.objects.create(user=user)
            profile.save()
        if user.banned:
            return Response({"message":"Account is banned"},status=status.HTTP_403_FORBIDDEN)
        user.save()

        refresh = RefreshToken.for_user(user)

        print(str(refresh.access_token))

        return Response({
            'refresh':str(refresh),
            'access':str(refresh.access_token)
        })
    



@api_view(['GET'])
@permission_classes([AllowAny])
def verify_email_view(request,uid,token):
    response =  verify_email(request,uid,token)
    if response==None:
        return Response(data={"message":f"Email already verified"},status=status.HTTP_400_BAD_REQUEST)
    if response:
        return Response(data={"message":f"Email verification successfully"},status=status.HTTP_200_OK)
    return Response(data={"message":f"Token Expired "},status=status.HTTP_406_NOT_ACCEPTABLE)


