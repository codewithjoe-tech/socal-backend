
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/',include('UserManagement.urls')),
    path("api/profile/",include('Profiles.urls')),
    path('api/report/',include('ReportApp.urls')),
    path("api/admin/",include('AdminPanel.urls')),
    path('api/chat/',include('Chat.urls')),
] + static(settings.MEDIA_URL,document_root =settings.MEDIA_ROOT)




