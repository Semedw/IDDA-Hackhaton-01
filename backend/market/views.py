import requests
import os
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Asset, PricePoint
from .serializers import AssetSerializer, AssetDetailSerializer

RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY', 'd4c7v6pr01qudf6h31f0d4c7v6pr01qudf6h31fg')
RAPIDAPI_HOST = 'apidojo-yahoo-finance-v1.p.rapidapi.com'


class AssetListView(generics.ListAPIView):
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Optimize query to avoid N+1 issues
        return Asset.objects.prefetch_related('prices', 'users').all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


def validate_stock_exists(symbol):
    """Validate if a stock symbol exists using Yahoo Finance API or fallback list"""
    # List of known valid stocks (same as search fallback)
    known_stocks = {
        'AAPL': 'Apple Inc.',
        'MSFT': 'Microsoft Corporation',
        'GOOGL': 'Alphabet Inc.',
        'AMZN': 'Amazon.com Inc.',
        'TSLA': 'Tesla, Inc.',
        'META': 'Meta Platforms Inc.',
        'NVDA': 'NVIDIA Corporation',
        'JPM': 'JPMorgan Chase & Co.',
        'V': 'Visa Inc.',
        'JNJ': 'Johnson & Johnson',
        'WMT': 'Walmart Inc.',
        'PG': 'Procter & Gamble Co.',
        'MA': 'Mastercard Inc.',
        'UNH': 'UnitedHealth Group Inc.',
        'HD': 'The Home Depot, Inc.',
        'DIS': 'The Walt Disney Company',
        'PYPL': 'PayPal Holdings, Inc.',
        'BAC': 'Bank of America Corp.',
        'NFLX': 'Netflix, Inc.',
        'ADBE': 'Adobe Inc.',
    }
    
    symbol_upper = symbol.upper()
    
    # Check known stocks first
    if symbol_upper in known_stocks:
        return {
            'exists': True,
            'name': known_stocks[symbol_upper]
        }
    
    # Check database for existing assets
    try:
        from .models import Asset
        existing_asset = Asset.objects.filter(symbol=symbol_upper, type='stock').first()
        if existing_asset:
            return {
                'exists': True,
                'name': existing_asset.name
            }
    except Exception:
        pass
    
    # Try API validation (may fail due to quota)
    try:
        url = f'https://{RAPIDAPI_HOST}/auto-complete'
        headers = {
            'x-rapidapi-host': RAPIDAPI_HOST,
            'x-rapidapi-key': RAPIDAPI_KEY
        }
        params = {'q': symbol, 'region': 'US'}
        
        response = requests.get(url, headers=headers, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if symbol exists in quotes
            if 'quotes' in data:
                for quote in data['quotes']:
                    if quote.get('symbol', '').upper() == symbol_upper:
                        quote_type = quote.get('quoteType', '').lower()
                        if quote_type in ['equity', 'stock']:
                            return {
                                'exists': True,
                                'name': quote.get('longname') or quote.get('shortname') or symbol
                            }
            
            # Alternative check in data array
            if 'data' in data:
                for item in data['data']:
                    if item.get('symbol', '').upper() == symbol_upper:
                        return {
                            'exists': True,
                            'name': item.get('name') or item.get('shortName') or symbol
                        }
        
        # If API returns but symbol not found, check if it's a quota error
        if response.status_code == 429:
            # Quota exceeded - allow known stocks or assume valid
            return {'exists': True, 'name': symbol}
        
        return {'exists': False, 'name': None}
    except Exception as e:
        # On error (timeout, network, etc.), allow the stock (don't block user)
        # This is more permissive since API might be down
        return {'exists': True, 'name': symbol}


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_asset(request):
    symbol = request.data.get('symbol', '').upper().strip()
    asset_type = request.data.get('type', 'stock')
    name = request.data.get('name', symbol)

    if not symbol:
        return Response({'error': 'Symbol is required'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate stock exists if it's a stock
    if asset_type == 'stock':
        validation = validate_stock_exists(symbol)
        if not validation['exists']:
            return Response({
                'error': f'Stock symbol "{symbol}" not found. Please check the symbol and try again.',
                'symbol': symbol
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Use the validated name if available
        if validation['name'] and validation['name'] != symbol:
            name = validation['name']

    asset, created = Asset.objects.get_or_create(
        symbol=symbol,
        defaults={'type': asset_type, 'name': name}
    )

    # Add to user's tracked assets
    asset.users.add(request.user)

    # Fetch current price
    fetch_price(asset)

    serializer = AssetSerializer(asset, context={'request': request})
    return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_asset(request, asset_id):
    try:
        asset = Asset.objects.get(id=asset_id)
        asset.users.remove(request.user)
        return Response({'message': 'Asset removed from tracking'}, status=status.HTTP_200_OK)
    except Asset.DoesNotExist:
        return Response({'error': 'Asset not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def asset_detail(request, asset_id):
    try:
        # Optimize query to avoid N+1 issues
        asset = Asset.objects.prefetch_related('prices', 'users').get(id=asset_id)
        serializer = AssetDetailSerializer(asset, context={'request': request})
        return Response(serializer.data)
    except Asset.DoesNotExist:
        return Response({'error': 'Asset not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_assets(request):
    # Optimize query to avoid N+1 issues
    assets = Asset.objects.filter(users=request.user).prefetch_related('prices', 'users')
    serializer = AssetSerializer(assets, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])  # Allow unauthenticated for search
def search_stocks(request):
    """Search for stocks using Yahoo Finance API"""
    query = request.query_params.get('q', '').strip().upper()
    
    if not query or len(query) < 1:
        return Response({'results': []})
    
    try:
        # Use Yahoo Finance search API
        url = f'https://{RAPIDAPI_HOST}/auto-complete'
        headers = {
            'x-rapidapi-host': RAPIDAPI_HOST,
            'x-rapidapi-key': RAPIDAPI_KEY
        }
        params = {'q': query, 'region': 'US'}
        
        response = requests.get(url, headers=headers, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            results = []
            
            # Parse the response - Yahoo Finance returns different formats
            if 'quotes' in data:
                for quote in data['quotes'][:10]:  # Limit to 10 results
                    symbol = quote.get('symbol', '')
                    shortname = quote.get('shortname', '')
                    longname = quote.get('longname', '') or shortname
                    quote_type = quote.get('quoteType', '').lower()
                    
                    # Only include stocks (not options, ETFs, etc.)
                    if quote_type in ['equity', 'stock'] and symbol:
                        results.append({
                            'symbol': symbol,
                            'name': longname or shortname or symbol,
                            'type': 'stock'
                        })
            
            # Alternative: if response has different structure
            if not results and 'data' in data:
                for item in data['data'][:10]:
                    symbol = item.get('symbol', '')
                    name = item.get('name', '') or item.get('shortName', '') or symbol
                    if symbol:
                        results.append({
                            'symbol': symbol,
                            'name': name,
                            'type': 'stock'
                        })
            
            if results:
                return Response({'results': results})
        
        # Fallback: Use hardcoded popular stocks if API fails or quota exceeded
        popular_stocks = [
            {'symbol': 'AAPL', 'name': 'Apple Inc.', 'type': 'stock'},
            {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'type': 'stock'},
            {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'type': 'stock'},
            {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'type': 'stock'},
            {'symbol': 'TSLA', 'name': 'Tesla, Inc.', 'type': 'stock'},
            {'symbol': 'META', 'name': 'Meta Platforms Inc.', 'type': 'stock'},
            {'symbol': 'NVDA', 'name': 'NVIDIA Corporation', 'type': 'stock'},
            {'symbol': 'JPM', 'name': 'JPMorgan Chase & Co.', 'type': 'stock'},
            {'symbol': 'V', 'name': 'Visa Inc.', 'type': 'stock'},
            {'symbol': 'JNJ', 'name': 'Johnson & Johnson', 'type': 'stock'},
            {'symbol': 'WMT', 'name': 'Walmart Inc.', 'type': 'stock'},
            {'symbol': 'PG', 'name': 'Procter & Gamble Co.', 'type': 'stock'},
            {'symbol': 'MA', 'name': 'Mastercard Inc.', 'type': 'stock'},
            {'symbol': 'UNH', 'name': 'UnitedHealth Group Inc.', 'type': 'stock'},
            {'symbol': 'HD', 'name': 'The Home Depot, Inc.', 'type': 'stock'},
            {'symbol': 'DIS', 'name': 'The Walt Disney Company', 'type': 'stock'},
            {'symbol': 'PYPL', 'name': 'PayPal Holdings, Inc.', 'type': 'stock'},
            {'symbol': 'BAC', 'name': 'Bank of America Corp.', 'type': 'stock'},
            {'symbol': 'NFLX', 'name': 'Netflix, Inc.', 'type': 'stock'},
            {'symbol': 'ADBE', 'name': 'Adobe Inc.', 'type': 'stock'},
        ]
        
        # Filter popular stocks by query
        matching_stocks = [
            stock for stock in popular_stocks 
            if query.upper() in stock['symbol'].upper() or query.upper() in stock['name'].upper()
        ][:10]
        
        # Also check database
        from .models import Asset
        matching_assets = Asset.objects.filter(
            symbol__icontains=query,
            type='stock'
        )[:10]
        
        # Combine and deduplicate
        db_results = [{
            'symbol': asset.symbol,
            'name': asset.name,
            'type': 'stock'
        } for asset in matching_assets]
        
        # Merge results, avoiding duplicates
        seen_symbols = set()
        all_results = []
        for result in matching_stocks + db_results:
            if result['symbol'] not in seen_symbols:
                seen_symbols.add(result['symbol'])
                all_results.append(result)
                if len(all_results) >= 10:
                    break
        
        return Response({'results': all_results})
            
    except requests.exceptions.Timeout:
        # Fallback to popular stocks and database search
        popular_stocks = [
            {'symbol': 'AAPL', 'name': 'Apple Inc.', 'type': 'stock'},
            {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'type': 'stock'},
            {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'type': 'stock'},
            {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'type': 'stock'},
            {'symbol': 'TSLA', 'name': 'Tesla, Inc.', 'type': 'stock'},
            {'symbol': 'META', 'name': 'Meta Platforms Inc.', 'type': 'stock'},
            {'symbol': 'NVDA', 'name': 'NVIDIA Corporation', 'type': 'stock'},
        ]
        matching_stocks = [
            stock for stock in popular_stocks 
            if query.upper() in stock['symbol'].upper() or query.upper() in stock['name'].upper()
        ][:10]
        from .models import Asset
        matching_assets = Asset.objects.filter(
            symbol__icontains=query,
            type='stock'
        )[:10]
        db_results = [{
            'symbol': asset.symbol,
            'name': asset.name,
            'type': 'stock'
        } for asset in matching_assets]
        seen_symbols = set()
        all_results = []
        for result in matching_stocks + db_results:
            if result['symbol'] not in seen_symbols:
                seen_symbols.add(result['symbol'])
                all_results.append(result)
                if len(all_results) >= 10:
                    break
        return Response({'results': all_results})
    except Exception as e:
        # Fallback to popular stocks and database search on error
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f'Error in stock search: {str(e)}')
        popular_stocks = [
            {'symbol': 'AAPL', 'name': 'Apple Inc.', 'type': 'stock'},
            {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'type': 'stock'},
            {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'type': 'stock'},
            {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'type': 'stock'},
            {'symbol': 'TSLA', 'name': 'Tesla, Inc.', 'type': 'stock'},
            {'symbol': 'META', 'name': 'Meta Platforms Inc.', 'type': 'stock'},
            {'symbol': 'NVDA', 'name': 'NVIDIA Corporation', 'type': 'stock'},
        ]
        matching_stocks = [
            stock for stock in popular_stocks 
            if query.upper() in stock['symbol'].upper() or query.upper() in stock['name'].upper()
        ][:10]
        from .models import Asset
        matching_assets = Asset.objects.filter(
            symbol__icontains=query,
            type='stock'
        )[:10]
        db_results = [{
            'symbol': asset.symbol,
            'name': asset.name,
            'type': 'stock'
        } for asset in matching_assets]
        seen_symbols = set()
        all_results = []
        for result in matching_stocks + db_results:
            if result['symbol'] not in seen_symbols:
                seen_symbols.add(result['symbol'])
                all_results.append(result)
                if len(all_results) >= 10:
                    break
        return Response({'results': all_results})


def fetch_price(asset):
    """Fetch current price from external API and update asset"""
    try:
        if asset.type == 'crypto':
            # CoinGecko API
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={asset.symbol.lower()}&vs_currencies=usd"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                price = data.get(asset.symbol.lower(), {}).get('usd')
                if price:
                    price = float(price)
                    asset.current_price = price
                    asset.save(update_fields=['current_price'])
                    PricePoint.objects.create(asset=asset, price=price)
        else:
            # Use Yahoo Finance API for stocks
            from .price_updater import fetch_stock_price
            price = fetch_stock_price(asset)
            if price:
                asset.current_price = price
                asset.save(update_fields=['current_price'])
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error fetching price for {asset.symbol}: {e}")

