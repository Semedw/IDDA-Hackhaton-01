from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from market.models import Asset
from analysis.models import AnalysisResult
from accounts.models import UserProfile
from verbix_ai.ai_utils import ai_chat


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat(request):
    question = request.data.get('question', '')
    
    if not question:
        return Response({'error': 'Question is required'}, status=status.HTTP_400_BAD_REQUEST)

    # Get user context
    try:
        profile = UserProfile.objects.get(user=request.user)
        budget = float(profile.budget)
        risk_profile = profile.risk_profile
    except UserProfile.DoesNotExist:
        budget = 0
        risk_profile = 'moderate'

    # Get tracked assets with optimized query
    tracked_assets = Asset.objects.filter(users=request.user).select_related()
    assets_list = [{'symbol': a.symbol, 'name': a.name} for a in tracked_assets]

    # Get latest analysis summaries with optimized query (avoid N+1)
    asset_ids = [a.id for a in tracked_assets]
    if asset_ids:
        # Get the latest analysis for each asset (more efficient than distinct)
        latest_analyses = {}
        analyses = AnalysisResult.objects.filter(
            asset_id__in=asset_ids
        ).select_related('asset').order_by('asset_id', '-created_at')
        
        # Group by asset_id and take the first (latest) for each
        seen_assets = set()
        for analysis in analyses:
            if analysis.asset_id not in seen_assets:
                latest_analyses[analysis.asset.symbol] = analysis.ai_summary
                seen_assets.add(analysis.asset_id)
        
        analysis_summaries = latest_analyses
    else:
        analysis_summaries = {}

    # Build context
    context = {
        'assets': assets_list,
        'budget': budget,
        'risk_profile': risk_profile,
        'analysis_summaries': analysis_summaries
    }

    # Get AI response
    response = ai_chat(question, context)

    return Response({
        'question': question,
        'response': response
    })

