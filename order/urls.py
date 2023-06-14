from django.urls import path
from order import views

urlpatterns = [
    #Admin
    path('create_amount/', views.create_amount, name='amount-create'),   
    path('create_max_order/', views.create_max_order, name='max-order-create'),   
    path('create_commision/', views.create_commition, name='create-commision'),   
    path('all/', views.all_orders, name='all-order'),
    path('create_discount_coupon/', views.create_discount_coupon, name='create-discount-coupon'),
    path('update_discount_coupon/<str:discount_code_id>/', views.update_discount_coupon, name='update-discount-coupon'),
    path('delete_discount_coupon/<str:discount_code_id>/', views.delete_discount_coupon, name='delete-discount-coupon'),
    path('all_discount_coupon/', views.all_discount_coupon, name='all-discount-coupon'),
    #Broker
    path('order_create/', views.create_order, name='order-create'),
    path('broker_orders/', views.broker_orders, name='broker-orders'),
    # path('delivery_accept/<str:order_id>/', views.delivery_accept, name='delivery_accept'),
    path('revision_delivery/<str:order_id>/', views.delivery_revisoin, name='delivery_revision'),

    #Freelancer
    path('order_accept/<str:order_id>/', views.accept_order, name='order_accept'),
    path('order_cancel/<str:order_id>/', views.cancel_order, name='order_cancel'),
    path('freelancer_orders/', views.freelancer_orders, name='freelancer-orders'),
]