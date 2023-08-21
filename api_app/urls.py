
from django.urls import path
from .views import *
urlpatterns = [

    path('get_list_property/', get_list_property, name="list all property"),   
    path('get_image_list/<str:zpid>/<str:origin>', get_image_list, name="list image"),
  
]