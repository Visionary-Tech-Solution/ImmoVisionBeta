"""meet_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from authentication.views.base_auth import auto_login

schema_view = get_schema_view(
   openapi.Info(
      title="Real Vision Media Ltd",
      default_version='v2',
      description="Real Vision Media is a AI Based Property Video Generated Website .",
      terms_of_service="https://realvisionmedia.com/",
      contact=openapi.Contact(email="info-visionarytechsolution.com"),
      license=openapi.License(name="US License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/profile/', include('account.urls')),
    path('api/order/', include('order.urls')),
    path('api/order_delivery/', include('upload_video.urls')),
    path('autologin/<str:email>', auto_login, name="auto-login"),
    #recovery account
    path('api/recovery-account/', include('recovery_account.urls')),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    #notification
    path('api/notification/', include('notifications.urls')),
    path('api/get/', include('api_app.urls')),
]


urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
