"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import include, path, re_path
from django.views.static import serve as serve_media

urlpatterns = [
    path("setup/", include("apps.setup.web.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
    path("account/", include("apps.account.urls")),
    path("organizations/", include("apps.organizations.web.urls")),
    path("settings/", include("apps.settings.web.urls")),
    path("inventory/", include("apps.inventory.web.urls")),
    path("audit/", include("apps.audit.web.urls")),
    path("", include("apps.common.web.urls")),
    path("", include("apps.pages.web.urls")),
    # Sem Nginx/volume compartilhado na frente (mesma lógica do whitenoise pros
    # estáticos): uploads (avatars, logos, fotos de item) também precisam ser
    # servidos direto pelo processo Django/gunicorn, senão retornam 404.
    re_path(r"^media/(?P<path>.*)$", serve_media, {"document_root": settings.MEDIA_ROOT}),
]
