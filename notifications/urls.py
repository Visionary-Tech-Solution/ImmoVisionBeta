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

from django.urls import include, path
from notifications import views

urlpatterns = [
    path("all_notification/", views.NotificationView.as_view()),
    path('action_ready_video/', views.action_ready_video, name='action_ready_video'),
    path('action_send_offer/', views.action_send_offer, name='action_send_offer'),
    path('action_blog_post/', views.action_blog_post, name='action_blog_post'),
    path('ai_docs_ready/', views.action_ai_docs_ready, name='action_ai_docs_ready'),
    path('all_alert/', views.all_alert, name='all_alert'),
    path('help_mail/', views.help_me_mail, name='help_mail'),
]