from django.urls import path

from . import views

urlpatterns = [
    path('circles', views.circle_list, name='circle_list'),
    path('circles/new', views.circle_create, name='circle_create'),
    path('circles/<uuid:pk>/delete', views.circle_delete, name='circle_delete'),
    path('circles/<uuid:pk>/edit', views.circle_edit, name='circle_edit'),
    path('circles/<uuid:pk>', views.circle_detail, name='circle_detail'),

    path('invites', views.invite_list, name='invite_list'),
    path('invites/new', views.invite_create, name='invite_create'),
    path('invites/<uuid:pk>/accept', views.invite_accept, name='invite_accept'),
    path('invites/<uuid:pk>/delete', views.invite_delete, name='invite_delete'),
    path('invites/<uuid:pk>/edit', views.invite_edit, name='invite_edit'),
    path('invites/<uuid:pk>', views.invite_detail, name='invite_detail'),

    path('settings', views.settings, name='settings'),

    path('users/<uuid:pk>', views.user_detail, name='user_detail'),

    path('welcome', views.welcome, name='welcome'),
    path('', views.index, name='index'),
]
