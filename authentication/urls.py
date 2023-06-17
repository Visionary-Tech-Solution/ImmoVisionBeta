from django.urls import path

from authentication.views.base_auth import (MyTokenObtainPairView, admin_login,
                                            change_password, resend_password)
from authentication.views.broker import (GoogleLoginCallback, create_broker,
                                         upload_broker_csv)
from authentication.views.freelancer import create_freelancer

urlpatterns = [
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('password_change/', change_password, name="password_change"),
    path('resend_password/<int:user_id>', resend_password, name="password_resend"),


    # Admin
    path('admin_login/', admin_login, name="admin-login"),
    # Broker
    # path('create_broker/', BrokerView.as_view(), name="create_broker"),
    path('create_broker/', create_broker, name="create_broker"),
    path('csv_create_broker/', upload_broker_csv, name="create_broker_csv"),
    path('google_authentication/', GoogleLoginCallback.as_view(), name="google_authentication"),

    
    #Freelancer
    path('create_freelancer/', create_freelancer, name="create_freelancer"),    
]