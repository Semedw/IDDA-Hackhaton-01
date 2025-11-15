import { useState, useEffect, useRef } from 'react';
import axios from 'axios';

// Create a separate axios instance for search (no auth required)
const searchApi = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export default function StockAutocomplete({ onSelect, value, onChange }) {
  const [query, setQuery] = useState(value || '');
  const [results, setResults] = useState([]);
  const [showResults, setShowResults] = useState(false);
  const [loading, setLoading] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const inputRef = useRef(null);
  const resultsRef = useRef(null);
  const timeoutRef = useRef(null);

  useEffect(() => {
    if (value !== undefined) {
      setQuery(value);
    }
  }, [value]);

  useEffect(() => {
    // Debounce search
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    if (query.length < 1) {
      setResults([]);
      setShowResults(false);
      return;
    }

    timeoutRef.current = setTimeout(() => {
      searchStocks(query);
    }, 300);

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [query]);

  const searchStocks = async (searchQuery) => {
    if (searchQuery.length < 1) {
      setResults([]);
      return;
    }

    setLoading(true);
    try {
      const response = await searchApi.get(`/assets/search/?q=${encodeURIComponent(searchQuery)}`);
      if (response.data && response.data.results) {
        setResults(response.data.results);
        setShowResults(true);
        setSelectedIndex(-1);
      } else {
        setResults([]);
        setShowResults(false);
      }
    } catch (error) {
      console.error('Error searching stocks:', error);
      console.error('Error details:', error.response?.data);
      console.error('Error status:', error.response?.status);
      setResults([]);
      setShowResults(false);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = (stock) => {
    setQuery(stock.symbol);
    setShowResults(false);
    setResults([]);
    if (onSelect) {
      onSelect(stock);
    }
    if (onChange) {
      onChange(stock.symbol);
    }
  };

  const handleKeyDown = (e) => {
    if (!showResults || results.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev < results.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => prev > 0 ? prev - 1 : -1);
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < results.length) {
          handleSelect(results[selectedIndex]);
        } else if (results.length > 0) {
          handleSelect(results[0]);
        }
        break;
      case 'Escape':
        setShowResults(false);
        break;
    }
  };

  useEffect(() => {
    if (selectedIndex >= 0 && resultsRef.current) {
      const selectedElement = resultsRef.current.children[selectedIndex];
      if (selectedElement) {
        selectedElement.scrollIntoView({ block: 'nearest' });
      }
    }
  }, [selectedIndex]);

  return (
    <div className="relative flex-1">
      <input
        ref={inputRef}
        type="text"
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          if (onChange) {
            onChange(e.target.value);
          }
        }}
        onFocus={() => {
          if (results.length > 0) {
            setShowResults(true);
          }
        }}
        onBlur={() => {
          // Delay hiding to allow click on results
          setTimeout(() => setShowResults(false), 200);
        }}
        onKeyDown={handleKeyDown}
        placeholder="Search stocks (e.g., AAPL, TSLA)"
        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      
      {loading && (
        <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
        </div>
      )}

      {showResults && results.length > 0 && (
        <div
          ref={resultsRef}
          className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto"
        >
          {results.map((stock, index) => (
            <div
              key={`${stock.symbol}-${index}`}
              onClick={() => handleSelect(stock)}
              className={`px-4 py-2 cursor-pointer hover:bg-blue-50 transition ${
                index === selectedIndex ? 'bg-blue-100' : ''
              } ${index !== results.length - 1 ? 'border-b border-gray-200' : ''}`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-semibold text-gray-900">{stock.symbol}</div>
                  <div className="text-sm text-gray-600 truncate">{stock.name}</div>
                </div>
                <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                  {stock.type}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {showResults && query.length > 0 && results.length === 0 && !loading && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg p-4 text-center text-gray-500">
          No stocks found
        </div>
      )}
    </div>
  );
}

