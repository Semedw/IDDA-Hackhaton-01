import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../utils/api';
import StockAutocomplete from '../components/StockAutocomplete';

export default function Dashboard() {
  const [assets, setAssets] = useState([]);
  const [news, setNews] = useState([]);
  const [profile, setProfile] = useState(null);
  const [newAsset, setNewAsset] = useState({ symbol: '', type: 'stock', name: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAssets();
    fetchNews();
    fetchProfile();
  }, []);

  const fetchAssets = async () => {
    try {
      const response = await api.get('/assets/my/');
      setAssets(response.data);
    } catch (error) {
      console.error('Error fetching assets:', error);
    }
  };

  const fetchNews = async () => {
    try {
      const response = await api.get('/news/?limit=10');
      setNews(response.data);
    } catch (error) {
      console.error('Error fetching news:', error);
    }
  };

  const fetchProfile = async () => {
    try {
      const response = await api.get('/auth/profile/');
      setProfile(response.data);
    } catch (error) {
      console.error('Error fetching profile:', error);
    }
  };

  const handleAddAsset = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    // Basic validation
    if (!newAsset.symbol.trim()) {
      setError('Please enter a stock symbol');
      setLoading(false);
      return;
    }

    try {
      await api.post('/assets/add/', newAsset);
      setNewAsset({ symbol: '', type: 'stock', name: '' });
      setError('');
      fetchAssets();
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Failed to add asset';
      setError(errorMessage);
      // Also show alert for visibility
      alert(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveAsset = async (assetId) => {
    if (!window.confirm('Remove this asset from tracking?')) return;
    try {
      await api.delete(`/assets/${assetId}/remove/`);
      fetchAssets();
    } catch (error) {
      alert('Failed to remove asset');
    }
  };

  const handleUpdateProfile = async () => {
    const budget = prompt('Enter your budget:', profile?.budget || 0);
    const riskProfile = prompt('Enter risk profile (conservative/moderate/aggressive):', profile?.risk_profile || 'moderate');
    
    if (budget && riskProfile) {
      try {
        await api.put('/auth/profile/', { budget, risk_profile: riskProfile });
        fetchProfile();
      } catch (error) {
        alert('Failed to update profile');
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <button
          onClick={handleUpdateProfile}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          Update Profile
        </button>
      </div>

      {/* Profile Summary */}
      {profile && (
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <h2 className="text-xl font-semibold mb-4">Your Profile</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Budget</p>
              <p className="text-2xl font-bold text-blue-600">${parseFloat(profile.budget).toLocaleString()}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Risk Profile</p>
              <p className="text-2xl font-bold text-gray-900 capitalize">{profile.risk_profile}</p>
            </div>
          </div>
        </div>
      )}

      {/* Add Asset Form */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
        <h2 className="text-xl font-semibold mb-4">Add Asset to Track</h2>
        <form onSubmit={handleAddAsset} className="space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center gap-2">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <span>{error}</span>
            </div>
          )}
          <div className="flex gap-4">
            <StockAutocomplete
              value={newAsset.symbol}
              onChange={(symbol) => {
                setNewAsset({ ...newAsset, symbol, type: 'stock' });
                setError(''); // Clear error when user types
              }}
              onSelect={(stock) => {
                setNewAsset({
                  symbol: stock.symbol,
                  name: stock.name,
                  type: 'stock'
                });
                setError(''); // Clear error when selecting from autocomplete
              }}
            />
            <select
              value={newAsset.type}
              onChange={(e) => {
                setNewAsset({ ...newAsset, type: e.target.value });
                setError(''); // Clear error when changing type
              }}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="stock">Stock</option>
              <option value="crypto">Crypto</option>
            </select>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
            >
              {loading ? 'Adding...' : 'Add'}
            </button>
          </div>
          {newAsset.type === 'stock' && (
            <p className="text-sm text-gray-500">
              💡 Tip: Use the autocomplete to find valid stock symbols. Invalid symbols will be rejected.
            </p>
          )}
        </form>
      </div>

      {/* Tracked Assets */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
        <h2 className="text-xl font-semibold mb-4">Tracked Assets</h2>
        {assets.length === 0 ? (
          <p className="text-gray-500">No assets tracked yet. Add one above!</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {assets.map((asset) => (
              <div key={asset.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h3 className="font-semibold text-lg">{asset.symbol}</h3>
                    <p className="text-sm text-gray-600">{asset.name}</p>
                    <p className="text-xs text-gray-500 capitalize">{asset.type}</p>
                  </div>
                  <button
                    onClick={() => handleRemoveAsset(asset.id)}
                    className="text-red-600 hover:text-red-700 text-sm"
                  >
                    Remove
                  </button>
                </div>
                {asset.current_price && (
                  <p className="text-xl font-bold text-green-600">${asset.current_price.toLocaleString()}</p>
                )}
                <Link
                  to={`/asset/${asset.id}`}
                  className="mt-2 inline-block text-sm text-blue-600 hover:text-blue-700"
                >
                  View Details →
                </Link>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Latest News */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
        <h2 className="text-xl font-semibold mb-4">Latest News</h2>
        {news.length === 0 ? (
          <p className="text-gray-500">No news available</p>
        ) : (
          <div className="space-y-4">
            {news.map((item) => (
              <div key={item.id} className="border-b border-gray-200 pb-4 last:border-0">
                <a
                  href={item.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-lg font-semibold text-blue-600 hover:text-blue-700"
                >
                  {item.title}
                </a>
                {item.summary && (
                  <p className="text-sm text-gray-600 mt-1">{item.summary.substring(0, 150)}...</p>
                )}
                <p className="text-xs text-gray-500 mt-1">{item.source} • {new Date(item.published_at).toLocaleDateString()}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

