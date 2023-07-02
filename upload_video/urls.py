from django.urls import path
from upload_video import views

urlpatterns = [
    #Admin
    path('all_videos/', views.all_videos, name='all_videos'),    
    path('delete_videos/<str:video_id>', views.delete_videos, name='delete_videos'),    
    #Broker
    path('broker_reports/', views.broker_reports, name='broker_reports'),
    #Freelancer
    path('order_delivery/<str:order_id>/', views.freelancer_order_delivery, name='order_delivery'),
    path('review_order_delivery/<str:order_id>/', views.review_order_delivery, name='review_order_delivery'),
    path('freelancer_reports/', views.freelancer_reports, name='freelancer_report'),

]