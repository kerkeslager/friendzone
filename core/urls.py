from django.urls import path

from . import views

urlpatterns = [
    path('circles', views.circle_list, name='circle_list'),
    path('settings', views.settings, name='settings'),
    path('welcome', views.welcome, name='welcome'),
    path('', views.index, name='index'),
]
