"""
URL configuration for fz project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from core import views as core_views

auth_urlpatterns = [
    path('delete', core_views.delete, name='delete'),
    path('delete-done', core_views.delete_done, name='delete_done'),
    path('login', auth_views.LoginView.as_view(), name='login'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    path('password-change', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password-change-done', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('signup', core_views.signup, name='signup'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include(auth_urlpatterns)),
    path('', include('core.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
