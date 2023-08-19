
from django.urls import path
from .views import *
urlpatterns = [

    path('get_list_property/<str:zuid>/', get_list_property, name="list all property"),   
]