from django.urls import path

from .views import (
    BrandSimilarityCheckView,
    HomeView,
    ImovelCreateView,
    ImovelDetailView,
    ImovelListView,
    ItemImportTemplateView,
    ItemImportView,
    MovelCreateView,
    MovelDetailView,
    MovelExportView,
    MovelListView,
    MovelsByCategoryView,
    PatrimonioChoiceView,
    PatrimonioListView,
)

app_name = "inventory"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("patrimonios/", PatrimonioListView.as_view(), name="patrimonio_list"),
    path("patrimonios/novo/", PatrimonioChoiceView.as_view(), name="patrimonio_choice"),
    path("categories/", MovelsByCategoryView.as_view(), name="dashboard"),
    path("items/", MovelListView.as_view(), name="item_list"),
    path("items/add/", MovelCreateView.as_view(), name="item_create"),
    path("items/export/", MovelExportView.as_view(), name="item_export"),
    path("items/import/", ItemImportView.as_view(), name="item_import"),
    path("items/import/template/", ItemImportTemplateView.as_view(), name="item_import_template"),
    path("items/<uuid:pk>/", MovelDetailView.as_view(), name="item_detail"),
    path("imoveis/", ImovelListView.as_view(), name="imovel_list"),
    path("imoveis/add/", ImovelCreateView.as_view(), name="imovel_create"),
    path("imoveis/<uuid:pk>/", ImovelDetailView.as_view(), name="imovel_detail"),
    path("brands/check/", BrandSimilarityCheckView.as_view(), name="brand_check"),
]
