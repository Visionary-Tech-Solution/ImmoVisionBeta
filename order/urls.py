from django.urls import path

from order import views

urlpatterns = [
    #Admin
    path('create_amount/', views.create_amount, name='amount-create'),   
    path('get_amount/', views.get_amount, name='get-amount'),   
    path('create_max_order/', views.create_max_order, name='max-order-create'),   
    path('create_commision/', views.create_commition, name='create-commision'),
    path('reasssign_task/<str:order_id>', views.reasssign_task, name='reasssign_task'),
    path('admin_order_cancel/<str:order_id>', views.admin_order_cancel, name='admin-order-cancel'),   
    path('all/', views.all_orders, name='all-order'),
    path('create_discount_coupon/', views.create_discount_coupon, name='create-discount-coupon'),
    path('update_discount_coupon/<str:discount_code_id>/', views.update_discount_coupon, name='update-discount-coupon'),
    path('delete_discount_coupon/<str:discount_code_id>/', views.delete_discount_coupon, name='delete-discount-coupon'),
    path('all_discount_coupon/', views.all_discount_coupon, name='all-discount-coupon'),
    path('all_withdraw_request/', views.all_withdraw_request, name='all_withdraw_request'),
    path('withdraw_request_details/<int:id>', views.withdraw_request_details, name='withdraw_request_details'),
    path('withdraw_confirm/<int:id>', views.withdraw_confirm, name='withdraw_confirm'),
    path('withdraw_cancel/<int:id>', views.withdraw_cancel, name='withdraw_cancel'),
    path('change_broker/<str:order_id>/', views.change_broker, name='change_broker'),
    #Broker
    path('order_create/', views.create_order, name='order-create'),
    path('order_details/<str:order_id>', views.order_details, name='order-details'),
    path('revision_delivery/<str:order_id>/', views.delivery_revisoin, name='delivery_revision'),
    path('regenerate_social_text/<str:order_id>/', views.regenerate_social_text, name='regenerate_social_text'),
    path('rating_create/<str:order_id>/', views.create_order_rating, name='create_order_rating'),

    # Payment Work 
        # Broker --------------
    path('payment_create/', views.payment_create, name='make-payment'),
    path('save_payment/', views.save_payment, name='save-payment'),
    path('remove_payment/', views.remove_payment, name='remove-payment'),
    path('broker_orders/', views.broker_orders, name='broker-orders'),
    path('unpaid_orders/<str:order_id>/', views.unpaid_order_payment, name='unpaid_orders'),
    path('discount_code_verify/', views.discount_code_verify, name='discount_code_verify'),
        # Freelancer --------------
    path('freelancer_payment_save/', views.freelancer_payment_save, name='freelancer_payment_save'),
    path('freelancer_payment_remove/', views.freelancer_payment_remove, name='freelancer_payment_remove'),
    # path('delivery_accept/<str:order_id>/', views.delivery_accept, name='delivery_accept'),
    
    #Freelancer
    path('order_accept/<str:order_id>/', views.accept_order, name='order_accept'),
    path('order_cancel/<str:order_id>/', views.cancel_order, name='order_cancel'),
    path('freelancer_orders/', views.freelancer_orders, name='freelancer-orders'),
    path('withdraw_request/', views.withdraw_request, name='withdraw_request'),
    path('my_withdraw_request/', views.my_withdraw_request, name='my_withdraw_request'),

    # Admin Statistic
    path('admin_orders_info/', views.get_orders_info, name='get_orders_info'),
    path('today_new_clients_percent/', views.today_new_clients_percent, name='today_new_clients_percent'),
    path('avg_percentage/', views.get_avg_percentage, name='get_avg_percentage'),

    #Freelancer Statistic
    path('freelancer_task/', views.get_freelancer_task_info, name='get_freelancer_task_info'),
    # path('api/download/csv/', views.download_database_csv, name='download_database_csv'),
]