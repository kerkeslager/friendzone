from django.urls import include, path

from . import views

about_urlpatterns = [
    path('moderation', views.about_moderation, name='about_moderation'),
    path('philosophy', views.about_philosophy, name='about_philosophy'),
    path('privacy', views.about_privacy, name='about_privacy'),
]

circle_urlpatterns = [
    path('new', views.circle_create, name='circle_create'),
    path('<uuid:pk>/delete', views.circle_delete, name='circle_delete'),
    path('<uuid:pk>/edit', views.circle_edit, name='circle_edit'),
    path('<uuid:pk>', views.circle_detail, name='circle_detail'),
]

connection_urlpatterns = [
    path('<uuid:pk>/delete', views.conn_delete, name='connection_delete'),
    path('bulk-edit', views.conn_bulk_edit, name='connection_bulk_edit'),
]

convo_urlpatterns = [
    path('<uuid:pk>', views.convo_detail, name='convo_detail'),
    path('convo_redirect/', views.convo_redirect, name='convo_redirect'),
]

intro_urlpatterns = [
    path('new', views.intro_create, name='intro_create'),
    path('<uuid:pk>/accept', views.intro_accept, name='intro_accept'),
    path('<uuid:pk>', views.intro_detail, name='intro_detail'),
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
    path('about', views.about_main, name='about_main'),
    path('about/', include(about_urlpatterns)),

    path('circles', views.circle_list, name='circle_list'),
    path('circles/', include(circle_urlpatterns)),

    path('connections', views.connection_list, name='connection_list'),
    path('connections/', include(connection_urlpatterns)),

    path('convos', views.convo_list, name='convo_list'),
    path('convos/', include(convo_urlpatterns)),

    path('style.css', views.css_style, name='css_style'),

    path('posts/', include(post_urlpatterns)),

    path('intros', views.intro_list, name='intro_list'),
    path('intros/', include(intro_urlpatterns)),

    path('invites', views.invite_list, name='invite_list'),
    path('invites/', include(invite_urlpatterns)),

    path('settings', views.settings, name='settings'),
    path('style', views.style, name='style'),

    path('users/me/edit', views.profile_edit, name='profile_edit'),
    path('users/me', views.user_detail, name='profile_detail'),
    path('users/<uuid:pk>', views.user_detail, name='user_detail'),
    path(
        'users/<uuid:pk>/circles/edit',
        views.edit_connection_circles,
        name='edit_connection_circles',
    ),

    path('welcome', views.welcome, name='welcome'),
    path('why', views.why, name='why'),
    path('', views.index, name='index'),
]
