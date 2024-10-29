from django.urls import path
from . views import *

urlpatterns = [
    path("",ReportPostView.as_view())
]
