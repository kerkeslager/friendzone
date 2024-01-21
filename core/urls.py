from django.urls import path

from . import views

urlpatterns = [
    path('settings', views.settings, name='settings'),
    path('welcome', views.welcome, name='welcome'),
    path('', views.index, name='index'),
]
