from django.urls import path

from .views import OrganizationCreateView

app_name = "organizations"

urlpatterns = [
    path("create/", OrganizationCreateView.as_view(), name="create"),
]
