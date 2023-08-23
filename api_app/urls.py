
from django.urls import path
from .views import *
urlpatterns = [

    path('get_list_property/', get_list_property, name="list all property"),   
    path('get_image_list/<str:zpid>/<str:origin>', get_image_list, name="list image"),
    path('get_list_property_info/<str:zpid>/<str:origin>', get_list_property_info, name="fetch data"),
  
]