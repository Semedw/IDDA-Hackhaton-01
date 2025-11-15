from django.contrib import admin
from .models import Asset, PricePoint


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name', 'type', 'created_at')
    list_filter = ('type',)
    search_fields = ('symbol', 'name')


@admin.register(PricePoint)
class PricePointAdmin(admin.ModelAdmin):
    list_display = ('asset', 'price', 'timestamp')
    list_filter = ('asset', 'timestamp')

