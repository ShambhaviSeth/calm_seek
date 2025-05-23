"""
URL configuration for calmseek project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import calmseek.views as views

urlpatterns = [
    path("", lambda request: redirect("login")),
    path("appointments/", include("appointments.urls")),
    path("admin/", admin.site.urls),
    path("login/", views.login_user, name="login"),
    path("logout/", views.log_out, name="logout"),
    path("signup/", include("signup.urls")),
    path("error/", views.error, name="error"),
    path("providers/", include("providers.urls")),
    path("client/", include("client.urls")),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("home/", views.home, name="home"),
    path(
        "messaging/", include("messaging.urls", namespace="messaging")
    ),  # Include messaging app URLs
    path("groups/", include("groups.urls", namespace="groups")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
