from django.urls import path
from upload_video import views

urlpatterns = [
    #Admin
    # path('create_amount/', views.create_amount, name='amount-create'),    
    #Broker
    # path('order_create/', views.create_order, name='order-create'),
    #Freelancer
    path('order_delivery/<str:order_id>/', views.freelancer_order_delivery, name='order_delivery'),
]