from django.urls import path
from . import views


urlpatterns = [
    path('<str:str>/<str:str1>/<str:str2>/', views.index),
    path('<str:str>/<str:str1>/<str:str2>/<str:str3>/', views.index),
    path('<str:str>/<str:str1>/<str:str2>/<str:str3>/<str:str4>', views.index),
]