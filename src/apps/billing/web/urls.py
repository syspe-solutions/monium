from django.urls import path

from .views import PlansView

app_name = "billing"

urlpatterns = [
    path("plans/", PlansView.as_view(), name="plans"),
]
