from django.urls import path

from . views import *


urlpatterns = [
    path('signup/',UserView.as_view(),name = "signup"),
    path('login/',CustomTokenObtainPairView.as_view(),name="token_obtain_pair"),
    path('refresh/',CustomTokenRefreshView.as_view(),name="token_refresh"),
    path('google/login/', GoogleLogin.as_view(), name='google_login'),
    path('google/callback/', GoogleCallback.as_view(), name='google_callback'),
    path('verify/<uid>/<token>',verify_email_view,)
]
