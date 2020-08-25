from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name="index"),
    path('index', views.index, name="index"),
    path('index2', views.index2, name="index2"),
    path('index3', views.index3, name="index3"),
    path('index4', views.index4, name="index4"),
    path('data_insert', views.data_insert, name="data_insert")
]
