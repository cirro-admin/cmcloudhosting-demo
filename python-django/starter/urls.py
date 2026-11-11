from django.contrib import admin
from django.urls import path

from entries import views

urlpatterns = [
    # The runtime's blue/green health check polls this path. Keep it cheap.
    path("_runtime/health", views.health),
    path("api/info", views.api_info),
    path("admin/", admin.site.urls),
    path("", views.home),
]
