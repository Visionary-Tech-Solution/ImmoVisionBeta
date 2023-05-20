from django.urls import path

from order import views

urlpatterns = [
    #Admin
    path('create_amount/', views.create_amount, name='amount-create'),    
    # Order from Broker
    path('order_create/', views.create_order, name='order-create'),
    # path('pending_orders/', views.pending_order_reassign, name='order-create'),
]