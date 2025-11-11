import React, { useState } from 'react';
import { api } from '../utils/api';

const SemanticSearch = ({ workspaceId, onResultClick }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showResults, setShowResults] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) return;
    
    setIsSearching(true);
    setShowResults(true);
    
    try {
      const response = await api.post('/process/search', {
        query: query.trim(),
        workspace_id: workspaceId,
        limit: 10
      });
      
      setResults(response.results || []);
    } catch (error) {
      console.error('Search failed:', error);
      setResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleResultClick = (result) => {
    if (onResultClick) {
      onResultClick(result);
    }
    setShowResults(false);
    setQuery('');
  };

  const getPriorityColor = (priority) => {
    if (!priority || !priority.level) return 'bg-gray-100 text-gray-700';
    
    const colors = {
      'P0': 'bg-red-100 text-red-700 border-red-300',
      'P1': 'bg-orange-100 text-orange-700 border-orange-300',
      'P2': 'bg-yellow-100 text-yellow-700 border-yellow-300',
      'P3': 'bg-blue-100 text-blue-700 border-blue-300',
      'P4': 'bg-gray-100 text-gray-700 border-gray-300'
    };
    
    return colors[priority.level] || 'bg-gray-100 text-gray-700';
  };

  return (
    <div className="relative w-full max-w-2xl">
      {/* Search Bar */}
      <form onSubmit={handleSearch} className="relative">
        <div className="relative">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search: 'Who to call if system down?' or 'Emergency contacts'"
            className="w-full px-4 py-3 pl-12 pr-24 text-sm border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all"
          />
          <svg
            className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          <button
            type="submit"
            disabled={isSearching || !query.trim()}
            className="absolute right-2 top-1/2 -translate-y-1/2 px-4 py-2 bg-blue-500 text-white text-sm font-medium rounded-md hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {isSearching ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>

      {/* Search Results Dropdown */}
      {showResults && (
        <div className="absolute z-50 w-full mt-2 bg-white border-2 border-gray-200 rounded-lg shadow-2xl max-h-96 overflow-y-auto">
          {isSearching ? (
            <div className="p-8 text-center">
              <div className="inline-block w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
              <p className="mt-3 text-sm text-gray-600">Searching across all processes...</p>
            </div>
          ) : results.length === 0 ? (
            <div className="p-8 text-center">
              <svg className="w-12 h-12 mx-auto text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="mt-3 text-sm text-gray-600 font-medium">No results found</p>
              <p className="mt-1 text-xs text-gray-500">Try a different search query</p>
            </div>
          ) : (
            <div>
              <div className="sticky top-0 bg-gradient-to-r from-blue-50 to-indigo-50 px-4 py-3 border-b border-gray-200">
                <p className="text-xs font-semibold text-gray-600">
                  Found {results.length} result{results.length !== 1 ? 's' : ''} for "{query}"
                </p>
              </div>
              
              <div className="divide-y divide-gray-100">
                {results.map((result, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleResultClick(result)}
                    className="w-full text-left px-4 py-3 hover:bg-blue-50 transition-colors group"
                  >
                    <div className="flex items-start gap-3">
                      {/* Priority Badge */}
                      {result.priority && result.priority.level && (
                        <div className={`flex-shrink-0 px-2 py-0.5 rounded text-xs font-bold border ${getPriorityColor(result.priority)}`}>
                          {result.priority.emoji} {result.priority.level}
                        </div>
                      )}
                      
                      <div className="flex-1 min-w-0">
                        {/* Node Title */}
                        <h4 className="font-semibold text-sm text-gray-900 group-hover:text-blue-600 transition-colors">
                          {result.nodeTitle}
                        </h4>
                        
                        {/* Process Name */}
                        <p className="text-xs text-gray-500 mt-0.5">
                          in <span className="font-medium">{result.processName}</span>
                        </p>
                        
                        {/* Node Description */}
                        {result.nodeDescription && (
                          <p className="text-xs text-gray-600 mt-1 line-clamp-2">
                            {result.nodeDescription}
                          </p>
                        )}
                        
                        {/* Contacts (if any) */}
                        {result.contacts && result.contacts.length > 0 && (
                          <div className="flex items-center gap-1 mt-1.5">
                            <svg className="w-3 h-3 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                            </svg>
                            <span className="text-xs text-blue-600 font-medium">
                              {result.contacts.slice(0, 2).join(', ')}
                              {result.contacts.length > 2 && ` +${result.contacts.length - 2} more`}
                            </span>
                          </div>
                        )}
                      </div>
                      
                      {/* Similarity Score */}
                      <div className="flex-shrink-0 text-right">
                        <div className="text-xs font-semibold text-green-600">
                          {Math.round(result.similarity * 100)}%
                        </div>
                        <div className="text-xs text-gray-400">match</div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
              
              <div className="sticky bottom-0 bg-gray-50 px-4 py-2 border-t border-gray-200">
                <button
                  onClick={() => setShowResults(false)}
                  className="text-xs text-gray-600 hover:text-gray-800 font-medium"
                >
                  Close results
                </button>
              </div>
            </div>
          )}
        </div>
      )}
      
      {/* Click outside to close */}
      {showResults && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowResults(false)}
        />
      )}
    </div>
  );
};

export default SemanticSearch;
