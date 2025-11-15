import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../utils/api';

export default function AssetDetail() {
  const { id } = useParams();
  const [asset, setAsset] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    fetchAsset();
    fetchAnalysis();
    
    // Refresh asset data every 6 seconds to show updated price history
    const interval = setInterval(() => {
      fetchAsset();
    }, 6000);
    
    return () => clearInterval(interval);
  }, [id]);

  const fetchAsset = async () => {
    try {
      const response = await api.get(`/assets/${id}/`);
      setAsset(response.data);
      // Debug: log price history
      if (response.data.recent_prices) {
        console.log(`Price history for ${response.data.symbol}:`, response.data.recent_prices.length, 'points');
      }
    } catch (error) {
      console.error('Error fetching asset:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalysis = async () => {
    try {
      const response = await api.get(`/analysis/${id}/`);
      setAnalysis(response.data);
    } catch (error) {
      // Analysis might not exist yet
      setAnalysis(null);
    }
  };

  const handleRunAnalysis = async () => {
    setAnalyzing(true);
    try {
      const response = await api.post('/analysis/run/', { asset_id: parseInt(id) });
      setAnalysis(response.data);
    } catch (error) {
      alert(error.response?.data?.error || 'Failed to run analysis');
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading) {
    return <div className="text-center py-12">Loading...</div>;
  }

  if (!asset) {
    return <div className="text-center py-12">Asset not found</div>;
  }

  const sentimentColors = {
    positive: 'bg-green-100 text-green-800',
    neutral: 'bg-gray-100 text-gray-800',
    negative: 'bg-red-100 text-red-800',
  };

  const riskColors = {
    low: 'bg-blue-100 text-blue-800',
    medium: 'bg-yellow-100 text-yellow-800',
    high: 'bg-red-100 text-red-800',
  };

  return (
    <div className="space-y-6">
      <Link to="/dashboard" className="text-blue-600 hover:text-blue-700">← Back to Dashboard</Link>
      
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{asset.symbol}</h1>
            <p className="text-lg text-gray-600">{asset.name}</p>
            <p className="text-sm text-gray-500 capitalize">{asset.type}</p>
          </div>
          {asset.current_price && (
            <div className="text-right">
              <p className="text-sm text-gray-600">Current Price</p>
              <p className="text-3xl font-bold text-green-600">${asset.current_price.toLocaleString()}</p>
            </div>
          )}
        </div>
      </div>

      {/* Price Chart Placeholder */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
        <h2 className="text-xl font-semibold mb-4">Price History</h2>
        {asset.recent_prices && asset.recent_prices.length > 0 ? (
          <div>
            <div className="h-64 flex items-end justify-between gap-1 mb-4">
              {asset.recent_prices.slice(0, 30).map((price, idx) => {
                const prices = asset.recent_prices.map(p => parseFloat(p.price));
                const maxPrice = Math.max(...prices);
                const minPrice = Math.min(...prices);
                const range = maxPrice - minPrice || 1; // Avoid division by zero
                const height = ((parseFloat(price.price) - minPrice) / range) * 100;
                return (
                  <div key={price.id || idx} className="flex-1 flex flex-col items-center group">
                    <div
                      className="w-full bg-blue-500 rounded-t hover:bg-blue-600 transition-colors cursor-pointer"
                      style={{ height: `${Math.max(height, 5)}%` }}
                      title={`$${parseFloat(price.price).toFixed(2)} - ${new Date(price.timestamp).toLocaleString()}`}
                    />
                  </div>
                );
              })}
            </div>
            <div className="text-xs text-gray-500 text-center">
              Showing last {Math.min(asset.recent_prices.length, 30)} price points
            </div>
          </div>
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-500 mb-2">No price history available yet</p>
            <p className="text-sm text-gray-400">Price history will appear here as data is collected every 5 seconds</p>
          </div>
        )}
      </div>

      {/* AI Analysis */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">AI Analysis</h2>
          <button
            onClick={handleRunAnalysis}
            disabled={analyzing}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
          >
            {analyzing ? 'Analyzing...' : 'Run Analysis'}
          </button>
        </div>

        {analysis ? (
          <div className="space-y-4">
            <div>
              <p className="text-sm text-gray-600 mb-2">Summary</p>
              <p className="text-gray-900">{analysis.ai_summary}</p>
            </div>
            <div className="flex gap-4">
              <div>
                <p className="text-sm text-gray-600 mb-1">Sentiment</p>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${sentimentColors[analysis.sentiment] || sentimentColors.neutral}`}>
                  {analysis.sentiment}
                </span>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Risk Rating</p>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${riskColors[analysis.risk_rating] || riskColors.medium}`}>
                  {analysis.risk_rating}
                </span>
              </div>
            </div>
            <p className="text-xs text-gray-500">Analysis generated: {new Date(analysis.created_at).toLocaleString()}</p>
          </div>
        ) : (
          <p className="text-gray-500">No analysis available. Click "Run Analysis" to generate one.</p>
        )}
      </div>
    </div>
  );
}

