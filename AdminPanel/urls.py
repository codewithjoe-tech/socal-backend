from django.urls import path
from . views import *



urlpatterns = [
    path('get/all-users',UsersView.as_view()),
    path('delete/<id>',UsersView.as_view()),
    path('ban/<id>',UsersView.as_view()),
    path('report/reason/<id>/',ReportedReason.as_view()),
    path('reported/<type>',Reported.as_view()),
    path('report/remove/<id>/',Reported.as_view()),
    path('report/delete/<id>/',ReportedReason.as_view()),
]
 