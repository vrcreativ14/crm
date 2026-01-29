from django.urls import path
from . import views


urlpatterns = [
    path('<str:secretKey>/', views.index),
    path('<str:secretKey>/<str:id>/', views.index),
    path('<str:secretKey>/<str:id>/<str:str>/', views.index),
    path('<str:secretKey>/<str:id>/<str:str>/<str:str1>/', views.index),
    path('<str:secretKey>/<str:id>/<str:str>/<str:str1>/<str:str2>/', views.index),
    path('<str:secretKey>/<str:id>/<str:str>/<str:str1>/<str:str2>/<str:str3>', views.index),
    path('maf/<str:id>', views.QuestionsForm),
    path('maf/api/<str:id>', views.MafApi)
]
