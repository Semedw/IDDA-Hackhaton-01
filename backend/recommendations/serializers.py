from rest_framework import serializers
from .models import Recommendation
from market.serializers import AssetSerializer


class RecommendationSerializer(serializers.ModelSerializer):
    asset = AssetSerializer(read_only=True)

    class Meta:
        model = Recommendation
        fields = ('id', 'asset', 'action', 'amount_percentage', 'rationale', 'confidence', 'created_at')

