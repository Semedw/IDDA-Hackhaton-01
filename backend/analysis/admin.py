from django.contrib import admin
from .models import AnalysisResult


@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
    list_display = ('asset', 'sentiment', 'risk_rating', 'created_at')
    list_filter = ('sentiment', 'risk_rating', 'created_at')
    search_fields = ('asset__symbol', 'asset__name')

