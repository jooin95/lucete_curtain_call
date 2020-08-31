from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name="index"),
    path('start_server/', views.start_server, name="start_server"),
    path('stop_server/', views.stop_server, name="stop_server"),
    path('weather_upload/', views.weather_upload, name="weather_upload"),
]
