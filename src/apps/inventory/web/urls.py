from django.urls import path

from .views import (
    AssetListView,
    AssetSearchView,
    BrandSimilarityCheckView,
    CategoryUsefulLifeUpdateView,
    HomeView,
    ItemImportTemplateView,
    ItemImportView,
    MovableAssetCreateView,
    MovableAssetDeleteView,
    MovableAssetDetailView,
    MovableAssetExportView,
    MovableAssetListView,
    MovableAssetUpdateView,
    MovableAssetsByCategoryView,
    RealEstateCreateView,
    RealEstateDetailView,
    RealEstateListView,
    RealEstateMapView,
    RealEstateUpdateView,
)

app_name = "inventory"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("patrimonios/", AssetListView.as_view(), name="asset_list"),
    path("patrimonios/search/", AssetSearchView.as_view(), name="asset_search"),
    path("categories/", MovableAssetsByCategoryView.as_view(), name="dashboard"),
    path("categories/<uuid:pk>/useful-life/", CategoryUsefulLifeUpdateView.as_view(), name="category_useful_life_update"),
    path("items/", MovableAssetListView.as_view(), name="item_list"),
    path("items/add/", MovableAssetCreateView.as_view(), name="item_create"),
    path("items/export/", MovableAssetExportView.as_view(), name="item_export"),
    path("items/import/", ItemImportView.as_view(), name="item_import"),
    path("items/import/template/", ItemImportTemplateView.as_view(), name="item_import_template"),
    path("items/<uuid:pk>/", MovableAssetDetailView.as_view(), name="item_detail"),
    path("items/<uuid:pk>/edit/", MovableAssetUpdateView.as_view(), name="item_update"),
    path("items/<uuid:pk>/delete/", MovableAssetDeleteView.as_view(), name="item_delete"),
    path("imoveis/", RealEstateListView.as_view(), name="real_estate_list"),
    path("imoveis/mapa/", RealEstateMapView.as_view(), name="real_estate_map"),
    path("imoveis/add/", RealEstateCreateView.as_view(), name="real_estate_create"),
    path("imoveis/<uuid:pk>/", RealEstateDetailView.as_view(), name="real_estate_detail"),
    path("imoveis/<uuid:pk>/edit/", RealEstateUpdateView.as_view(), name="real_estate_update"),
    path("brands/check/", BrandSimilarityCheckView.as_view(), name="brand_check"),
]
