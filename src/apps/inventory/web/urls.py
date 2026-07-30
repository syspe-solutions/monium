from django.urls import path

from .views import (
    BrandSimilarityCheckView,
    HomeView,
    ImovelCreateView,
    ImovelDetailView,
    ImovelListView,
    ImovelUpdateView,
    ItemImportTemplateView,
    ItemImportView,
    MovelCreateView,
    MovelDeleteView,
    MovelDetailView,
    MovelExportView,
    MovelListView,
    MovelUpdateView,
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
    path("items/<uuid:pk>/edit/", MovelUpdateView.as_view(), name="item_update"),
    path("items/<uuid:pk>/delete/", MovelDeleteView.as_view(), name="item_delete"),
    path("imoveis/", ImovelListView.as_view(), name="imovel_list"),
    path("imoveis/add/", ImovelCreateView.as_view(), name="imovel_create"),
    path("imoveis/<uuid:pk>/", ImovelDetailView.as_view(), name="imovel_detail"),
    path("imoveis/<uuid:pk>/edit/", ImovelUpdateView.as_view(), name="imovel_update"),
    path("brands/check/", BrandSimilarityCheckView.as_view(), name="brand_check"),
]
