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
    path('payment_create/', views.make_payment, name='make-payment'),
    path('broker_orders/', views.broker_orders, name='broker-orders'),
    # path('delivery_accept/<str:order_id>/', views.delivery_accept, name='delivery_accept'),
    path('revision_delivery/<str:order_id>/', views.delivery_revisoin, name='delivery_revision'),
    path('rating_create/<str:order_id>/', views.create_order_rating, name='create_order_rating'),

    #Freelancer
    path('order_accept/<str:order_id>/', views.accept_order, name='order_accept'),
    path('order_cancel/<str:order_id>/', views.cancel_order, name='order_cancel'),
    path('freelancer_orders/', views.freelancer_orders, name='freelancer-orders'),

    # Admin Statistic
    path('admin_orders_info/', views.get_orders_info, name='get_orders_info'),
    path('today_new_clients_percent/', views.today_new_clients_percent, name='today_new_clients_percent'),
    path('avg_percentage/', views.get_avg_percentage, name='get_avg_percentage'),

    #Freelancer Statistic
    path('freelancer_task/', views.get_freelancer_task_info, name='get_freelancer_task_info'),
]