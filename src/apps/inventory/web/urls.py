from django.urls import path

from .views import BrandSimilarityCheckView, HomeView, ItemCreateView, ItemsByCategoryView

app_name = "inventory"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("categories/", ItemsByCategoryView.as_view(), name="dashboard"),
    path("items/add/", ItemCreateView.as_view(), name="item_create"),
    path("brands/check/", BrandSimilarityCheckView.as_view(), name="brand_check"),
]
