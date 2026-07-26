from .brand_views import BrandSimilarityCheckView
from .dashboard import MovelsByCategoryView
from .home_view import HomeView
from .imovel_detail_view import ImovelDetailView
from .imovel_list_view import ImovelListView
from .imovel_views import ImovelCreateView
from .item_detail_view import MovelDetailView
from .item_export_view import MovelExportView
from .item_import_view import ItemImportTemplateView, ItemImportView
from .item_list_view import MovelListView
from .item_views import MovelCreateView
from .patrimonio_views import PatrimonioChoiceView, PatrimonioListView

__all__ = [
    "BrandSimilarityCheckView",
    "HomeView",
    "ImovelCreateView",
    "ImovelDetailView",
    "ImovelListView",
    "ItemImportTemplateView",
    "ItemImportView",
    "MovelCreateView",
    "MovelDetailView",
    "MovelExportView",
    "MovelListView",
    "MovelsByCategoryView",
    "PatrimonioChoiceView",
    "PatrimonioListView",
]
