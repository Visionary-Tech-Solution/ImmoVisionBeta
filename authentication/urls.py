from authentication.views.base_auth import (MyTokenObtainPairView,
                                            change_password, resend_password)
from authentication.views.broker import BrokerView
from authentication.views.freelancer import create_freelancer
from django.urls import path

urlpatterns = [
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('password_change/', change_password, name="password_change"),
    path('resend_password/<int:user_id>', resend_password, name="password_resend"),
    # Broker
    path('create_broker/', BrokerView.as_view(), name="create_broker"),
    #Freelancer
    path('create_freelancer/', create_freelancer, name="create_freelancer"),    
]