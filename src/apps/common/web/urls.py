from django.urls import path

from apps.common.web.views import HealthCheckView, NotFoundView, PublicFileProxyView

app_name = "common"

urlpatterns = [
    path("notfound/", NotFoundView.as_view(), name="notfound"),
    path("health/", HealthCheckView.as_view(), name="health"),
    path("content/<path:relative_path>", PublicFileProxyView.as_view(), name="media_proxy"),
]
