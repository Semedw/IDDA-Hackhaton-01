from rest_framework import serializers
from .models import Asset, PricePoint


class PricePointSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    
    class Meta:
        model = PricePoint
        fields = ('id', 'timestamp', 'price')
    
    def get_price(self, obj):
        # Convert Decimal to float for JSON serialization
        return float(obj.price)


class AssetSerializer(serializers.ModelSerializer):
    current_price = serializers.SerializerMethodField()
    is_tracked = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        fields = (
            'id', 'type', 'symbol', 'name', 'current_price', 'is_tracked', 'created_at',
            'previous_close', 'market_cap', 'volume', 'day_high', 'day_low',
            'year_high', 'year_low', 'pe_ratio', 'dividend_yield',
            'price_change', 'price_change_percent', 'last_updated'
        )

    def get_current_price(self, obj):
        # Use model field if available, otherwise get from latest price point
        if obj.current_price:
            return float(obj.current_price)
        latest_price = obj.prices.first()
        return float(latest_price.price) if latest_price else None

    def get_is_tracked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.users.filter(id=request.user.id).exists()
        return False


class AssetDetailSerializer(AssetSerializer):
    recent_prices = serializers.SerializerMethodField()

    class Meta(AssetSerializer.Meta):
        fields = AssetSerializer.Meta.fields + ('recent_prices',)

    def get_recent_prices(self, obj):
        prices = obj.prices.all()[:30]  # Limit to last 30 prices
        return PricePointSerializer(prices, many=True).data

