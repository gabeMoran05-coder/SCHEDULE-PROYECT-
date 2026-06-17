from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="escuela:dashboard", permanent=False)),
    path("admin/", admin.site.urls),
    path("usuarios/", include("apps.usuarios.urls")),
    path("escuela/", include("apps.escuela.urls")),
    path("horarios/", include("apps.horarios.urls")),
]
