from django.urls import path

from account import views

urlpatterns = [
    # Base
    path('my_profile/', views.get_profile, name="my_profile"),
    # Admin
    path('freelancer/all/', views.get_all_freelancer_profile, name="all_freelancer_profile"),
    path('broker/all/', views.get_all_broker_profile, name="all_broker_profile"),
    path('admin/status_change/<str:username>/', views.admin_status_change, name="admin_status_change"),
    #Broker
    path('broker/update_profile/', views.broker_update_profile, name="broker_profile_update"),
    #Freelancer
    path('freelancer/update_profile/', views.freelancer_update_profile, name="freelancer_profile_update"),
    path('freelancer/status_change/', views.update_freelancer_status, name="freelancer_status_change"),

]