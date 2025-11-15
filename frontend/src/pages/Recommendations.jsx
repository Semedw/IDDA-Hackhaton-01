import { useState, useEffect } from 'react';
import api from '../utils/api';

export default function Recommendations() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [disclaimer, setDisclaimer] = useState('');

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const response = await api.post('/recommendations/generate/');
      setRecommendations(response.data.recommendations);
      setDisclaimer(response.data.disclaimer);
    } catch (error) {
      alert(error.response?.data?.error || 'Failed to generate recommendations');
    } finally {
      setLoading(false);
    }
  };

  const actionColors = {
    BUY: 'bg-green-100 text-green-800 border-green-300',
    HOLD: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    SELL: 'bg-red-100 text-red-800 border-red-300',
  };

  const confidenceColors = {
    low: 'text-gray-600',
    medium: 'text-blue-600',
    high: 'text-green-600',
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">AI Recommendations</h1>
        <button
          onClick={handleGenerate}
          disabled={loading}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
        >
          {loading ? 'Generating...' : 'Generate Recommendations'}
        </button>
      </div>

      {disclaimer && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-sm text-yellow-800 font-semibold">⚠️ Disclaimer</p>
          <p className="text-sm text-yellow-700 mt-1">{disclaimer}</p>
        </div>
      )}

      {recommendations.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm p-12 border border-gray-200 text-center">
          <p className="text-gray-500 text-lg mb-2">No recommendations yet</p>
          <p className="text-gray-400 text-sm">Click "Generate Recommendations" to get AI-powered investment suggestions based on your tracked assets and budget.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {recommendations.map((rec) => (
            <div
              key={rec.id}
              className="bg-white rounded-xl shadow-sm p-6 border border-gray-200 hover:shadow-md transition"
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-bold text-gray-900">{rec.asset.symbol}</h3>
                  <p className="text-sm text-gray-600">{rec.asset.name}</p>
                </div>
                <span
                  className={`px-3 py-1 rounded-full text-sm font-semibold border ${actionColors[rec.action] || actionColors.HOLD}`}
                >
                  {rec.action}
                </span>
              </div>

              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Recommended Allocation</p>
                  <p className="text-2xl font-bold text-blue-600">{rec.amount_percentage}%</p>
                </div>

                <div>
                  <p className="text-sm text-gray-600 mb-1">Rationale</p>
                  <p className="text-gray-900">{rec.rationale}</p>
                </div>

                <div>
                  <p className="text-sm text-gray-600 mb-1">Confidence</p>
                  <p className={`font-semibold capitalize ${confidenceColors[rec.confidence] || confidenceColors.medium}`}>
                    {rec.confidence}
                  </p>
                </div>
              </div>

              <p className="text-xs text-gray-500 mt-4">
                Generated: {new Date(rec.created_at).toLocaleString()}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

