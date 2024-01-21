from django.urls import path

from . import views

urlpatterns = [
    path('circles', views.circle_list, name='circle_list'),
    path('circles/new', views.circle_create, name='circle_create'),
    path('circles/<uuid:pk>/delete', views.circle_delete, name='circle_delete'),
    path('circles/<uuid:pk>', views.circle_detail, name='circle_detail'),
    path('settings', views.settings, name='settings'),
    path('welcome', views.welcome, name='welcome'),
    path('', views.index, name='index'),
]
