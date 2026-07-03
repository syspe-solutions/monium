from django.urls import path

from .views import MercadoPagoWebhookView, PlansView, SubscribeView

app_name = "billing"

urlpatterns = [
    path("plans/", PlansView.as_view(), name="plans"),
    path("subscribe/<str:plan_id>/", SubscribeView.as_view(), name="subscribe"),
    path("webhook/mercadopago/", MercadoPagoWebhookView.as_view(), name="mercadopago_webhook"),
]
