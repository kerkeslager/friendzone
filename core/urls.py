from django.urls import include, path

from . import views

circle_urlpatterns = [
    path('new', views.circle_create, name='circle_create'),
    path('<uuid:pk>/delete', views.circle_delete, name='circle_delete'),
    path('<uuid:pk>/edit', views.circle_edit, name='circle_edit'),
    path('<uuid:pk>', views.circle_detail, name='circle_detail'),
]

invite_urlpatterns = [
    path('new', views.invite_create, name='invite_create'),
    path('<uuid:pk>/accept', views.invite_accept, name='invite_accept'),
    path('<uuid:pk>/delete', views.invite_delete, name='invite_delete'),
    path('<uuid:pk>/edit', views.invite_edit, name='invite_edit'),
    path('<uuid:pk>', views.invite_detail, name='invite_detail'),
]

post_urlpatterns = [
    path('new', views.post_create, name='post_create'),
    path('<uuid:pk>/delete', views.post_delete, name='post_delete'),
    path('<uuid:pk>/edit', views.post_edit, name='post_edit'),
    path('<uuid:pk>', views.post_detail, name='post_detail'),
]

urlpatterns = [
    path('circles', views.circle_list, name='circle_list'),
    path('circles/', include(circle_urlpatterns)),

    path('connections', views.connection_list, name='connection_list'),

    path('posts/', include(post_urlpatterns)),

    path('invites', views.invite_list, name='invite_list'),
    path('invites/', include(invite_urlpatterns)),

    path('settings', views.settings, name='settings'),
    path('style', views.style, name='style'),

    path('users/<uuid:pk>', views.user_detail, name='user_detail'),

    path('welcome', views.welcome, name='welcome'),
    path('why', views.why, name='why'),
    path('', views.index, name='index'),
]
