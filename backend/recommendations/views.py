from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from market.models import Asset
from accounts.models import UserProfile
from .models import Recommendation
from .serializers import RecommendationSerializer
from verbix_ai.ai_utils import ai_generate_recommendations


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_recommendations(request):
    # Get user profile
    try:
        profile = UserProfile.objects.get(user=request.user)
        budget = float(profile.budget)
        risk_profile = profile.risk_profile
    except UserProfile.DoesNotExist:
        return Response({'error': 'User profile not found. Please set your budget and risk profile.'}, 
                       status=status.HTTP_400_BAD_REQUEST)

    # Get tracked assets with optimized query
    tracked_assets = Asset.objects.filter(users=request.user).select_related()
    
    if not tracked_assets.exists():
        return Response({'error': 'No tracked assets found. Please add assets first.'}, 
                       status=status.HTTP_400_BAD_REQUEST)

    # Prepare assets data
    assets_data = [{'symbol': a.symbol, 'name': a.name} for a in tracked_assets]

    # Generate AI recommendations
    ai_result = ai_generate_recommendations(assets_data, budget, risk_profile)

    # Save recommendations with bulk operations
    recommendations = []
    asset_symbols = [rec_data.get('asset_symbol', '').upper() for rec_data in ai_result.get('recommendations', [])]
    
    # Fetch all assets in one query
    assets_dict = {asset.symbol: asset for asset in Asset.objects.filter(symbol__in=asset_symbols)}
    
    for rec_data in ai_result.get('recommendations', []):
        try:
            symbol = rec_data.get('asset_symbol', '').upper()
            asset = assets_dict.get(symbol)
            if not asset:
                continue
                
            recommendation = Recommendation.objects.create(
                user=request.user,
                asset=asset,
                action=rec_data.get('action', 'HOLD'),
                amount_percentage=rec_data.get('amount_percentage', 0),
                rationale=rec_data.get('rationale', ''),
                confidence=rec_data.get('confidence', 'medium')
            )
            recommendations.append(recommendation)
        except (KeyError, ValueError) as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error creating recommendation: {e}")
            continue

    serializer = RecommendationSerializer(recommendations, many=True)
    
    return Response({
        'recommendations': serializer.data,
        'disclaimer': ai_result.get('disclaimer', 'This is not financial advice. Always do your own research.')
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_recommendations(request):
    recommendations = Recommendation.objects.filter(user=request.user)
    serializer = RecommendationSerializer(recommendations, many=True)
    return Response(serializer.data)

