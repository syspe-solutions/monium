from django.urls import path

from .views import FAQView, HomeView, PrivacyView, ServiceDetailView, ServicesView, TermsView

app_name = "pages"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("services/", ServicesView.as_view(), name="services"),
    path("services/<slug:slug>/", ServiceDetailView.as_view(), name="service_detail"),
    path("faq/", FAQView.as_view(), name="faq"),
    path("privacy/", PrivacyView.as_view(), name="privacy"),
    path("terms/", TermsView.as_view(), name="terms"),
]
