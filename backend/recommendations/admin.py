from django.contrib import admin
from .models import Recommendation


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'asset', 'action', 'confidence', 'created_at')
    list_filter = ('action', 'confidence', 'created_at')
    search_fields = ('user__username', 'asset__symbol')

