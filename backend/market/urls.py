from django.urls import path
from .views import AssetListView, add_asset, remove_asset, asset_detail, my_assets, search_stocks

urlpatterns = [
    path('', AssetListView.as_view(), name='asset-list'),
    path('my/', my_assets, name='my-assets'),
    path('add/', add_asset, name='add-asset'),
    path('search/', search_stocks, name='search-stocks'),
    path('<int:asset_id>/', asset_detail, name='asset-detail'),
    path('<int:asset_id>/remove/', remove_asset, name='remove-asset'),
]

