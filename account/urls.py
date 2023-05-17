from account import views
from django.urls import path

urlpatterns = [
    # Base
    path('my_profile/', views.get_profile, name="my_profile"),
    # Admin
    path('freelancer/all/', views.get_all_freelancer_profile, name="all_freelancer_profile"),
    path('broker/all/', views.get_all_broker_profile, name="all_broker_profile"),
    #Broker
    path('broker/update_profile/', views.broker_update_profile, name="broker_profile_update"),
    #Freelancer
    path('freelancer/update_profile/', views.freelancer_update_profile, name="freelancer_profile_update"),
]