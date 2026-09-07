from .brand_views import BrandSimilarityCheckView
from .category_useful_life_update_view import CategoryUsefulLifeUpdateView
from .dashboard import MovableAssetsByCategoryView
from .home_view import HomeView
from .real_estate_detail_view import RealEstateDetailView
from .real_estate_list_view import RealEstateListView
from .real_estate_map_view import RealEstateMapView
from .real_estate_update_view import RealEstateUpdateView
from .real_estate_views import RealEstateCreateView
from .item_delete_view import MovableAssetDeleteView
from .item_detail_view import MovableAssetDetailView
from .item_export_view import MovableAssetExportView
from .item_import_template_view import ItemImportTemplateView
from .item_import_view import ItemImportView
from .item_list_view import MovableAssetListView
from .item_update_view import MovableAssetUpdateView
from .item_views import MovableAssetCreateView
from .asset_search_view import AssetSearchView
from .asset_views import AssetListView

__all__ = [
    "BrandSimilarityCheckView",
    "CategoryUsefulLifeUpdateView",
    "HomeView",
    "RealEstateCreateView",
    "RealEstateDetailView",
    "RealEstateListView",
    "RealEstateMapView",
    "RealEstateUpdateView",
    "ItemImportTemplateView",
    "ItemImportView",
    "MovableAssetCreateView",
    "MovableAssetDeleteView",
    "MovableAssetDetailView",
    "MovableAssetExportView",
    "MovableAssetListView",
    "MovableAssetUpdateView",
    "MovableAssetsByCategoryView",
    "AssetListView",
    "AssetSearchView",
]
