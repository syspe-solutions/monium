from .brand_views import BrandSimilarityCheckView
from .category_useful_life_update_view import CategoryUsefulLifeUpdateView
from .dashboard import MovelsByCategoryView
from .home_view import HomeView
from .imovel_detail_view import ImovelDetailView
from .imovel_list_view import ImovelListView
from .imovel_update_view import ImovelUpdateView
from .imovel_views import ImovelCreateView
from .item_delete_view import MovelDeleteView
from .item_detail_view import MovelDetailView
from .item_export_view import MovelExportView
from .item_import_view import ItemImportTemplateView, ItemImportView
from .item_list_view import MovelListView
from .item_update_view import MovelUpdateView
from .item_views import MovelCreateView
from .patrimonio_search_view import PatrimonioSearchView
from .patrimonio_views import PatrimonioListView

__all__ = [
    "BrandSimilarityCheckView",
    "CategoryUsefulLifeUpdateView",
    "HomeView",
    "ImovelCreateView",
    "ImovelDetailView",
    "ImovelListView",
    "ImovelUpdateView",
    "ItemImportTemplateView",
    "ItemImportView",
    "MovelCreateView",
    "MovelDeleteView",
    "MovelDetailView",
    "MovelExportView",
    "MovelListView",
    "MovelUpdateView",
    "MovelsByCategoryView",
    "PatrimonioListView",
    "PatrimonioSearchView",
]
