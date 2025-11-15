from rest_framework import serializers
from .models import AnalysisResult
from market.serializers import AssetSerializer


class AnalysisResultSerializer(serializers.ModelSerializer):
    asset = AssetSerializer(read_only=True)

    class Meta:
        model = AnalysisResult
        fields = ('id', 'asset', 'ai_summary', 'sentiment', 'risk_rating', 'created_at')

