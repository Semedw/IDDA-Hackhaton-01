from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from market.models import Asset
from market.views import fetch_price
from .models import AnalysisResult
from .serializers import AnalysisResultSerializer
from verbix_ai.ai_utils import ai_analyze_text


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def run_analysis(request):
    asset_id = request.data.get('asset_id')
    symbol = request.data.get('symbol')

    if not asset_id and not symbol:
        return Response({'error': 'asset_id or symbol is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        if asset_id:
            asset = Asset.objects.get(id=asset_id)
        else:
            asset = Asset.objects.get(symbol=symbol.upper())
    except Asset.DoesNotExist:
        return Response({'error': 'Asset not found'}, status=status.HTTP_404_NOT_FOUND)

    # Fetch latest price (this will update asset.current_price)
    fetch_price(asset)
    # Refresh asset from DB to get updated current_price
    asset.refresh_from_db()
    latest_price = asset.prices.first()

    # Prepare analysis text with current price
    current_price = asset.current_price or (latest_price.price if latest_price else None)
    price_str = f"${current_price:.2f}" if current_price else 'N/A'
    
    analysis_text = f"""
    Asset: {asset.name} ({asset.symbol})
    Type: {asset.type}
    Current Price: {price_str}
    """
    
    # Get AI analysis
    ai_result = ai_analyze_text(analysis_text)

    # Save analysis result
    analysis = AnalysisResult.objects.create(
        asset=asset,
        ai_summary=ai_result.get('summary', 'No summary available'),
        sentiment=ai_result.get('sentiment', 'neutral'),
        risk_rating=ai_result.get('risk_rating', 'medium')
    )

    serializer = AnalysisResultSerializer(analysis)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_analysis(request, asset_id):
    try:
        asset = Asset.objects.get(id=asset_id)
        analysis = AnalysisResult.objects.filter(asset=asset).first()
        
        if not analysis:
            return Response({'error': 'No analysis found for this asset'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = AnalysisResultSerializer(analysis)
        return Response(serializer.data)
    except Asset.DoesNotExist:
        return Response({'error': 'Asset not found'}, status=status.HTTP_404_NOT_FOUND)

