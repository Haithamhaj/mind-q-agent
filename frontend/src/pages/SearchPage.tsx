import React, { useState } from 'react';
import { Search as SearchIcon, ArrowRight, Loader2, AlertCircle } from 'lucide-react';
import { Input } from '../components/ui/Input';
import { Button } from '../components/ui/Button';

interface SearchResult {
  id: string;
  text: string;
  score: number;
  metadata: {
    source?: string;
    doc_hash?: string;
    [key: string]: any;
  };
}

const API_BASE = '/api/v1';

const SearchPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [hasSearched, setHasSearched] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setError(null);
    setHasSearched(true);

    try {
      const response = await fetch(`${API_BASE}/search/?q=${encodeURIComponent(query.trim())}&limit=10`);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Search failed: ${response.statusText}`);
      }

      const data = await response.json();

      // Map backend response to frontend format
      const mappedResults: SearchResult[] = data.map((item: any, index: number) => ({
        id: item.id || `result-${index}`,
        text: item.text || item.content || item.chunk || '',
        score: item.score || item.similarity || 0,
        metadata: {
          source: item.metadata?.source || item.source || item.metadata?.title || 'Unknown',
          ...item.metadata
        }
      }));

      setResults(mappedResults);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  // Highlight matching terms in text
  const highlightText = (text: string, searchQuery: string) => {
    if (!searchQuery.trim()) return text;

    const terms = searchQuery.toLowerCase().split(/\s+/).filter(t => t.length > 2);
    let highlighted = text;

    terms.forEach(term => {
      const regex = new RegExp(`(${term})`, 'gi');
      highlighted = highlighted.replace(regex, '<mark class="bg-yellow-100 px-0.5 font-semibold text-zinc-900">$1</mark>');
    });

    return highlighted;
  };

  return (
    <div className="max-w-4xl mx-auto p-8">
      <div className="text-center mb-10">
        <h1 className="text-3xl font-bold text-zinc-900 mb-4">Semantic Search</h1>
        <p className="text-zinc-500 max-w-xl mx-auto">
          Find exact concepts and answers buried deep within your uploaded documents using vector similarity.
        </p>
      </div>

      <form onSubmit={handleSearch} className="flex gap-3 mb-12">
        <div className="relative flex-1">
          <SearchIcon className="absolute left-3 top-2.5 w-5 h-5 text-zinc-400" />
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for concepts, e.g. 'AI agents' or 'project requirements'..."
            className="pl-10 h-12 text-lg shadow-sm"
          />
        </div>
        <Button type="submit" size="lg" className="h-12 px-8" disabled={isLoading || !query.trim()}>
          {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Search'}
        </Button>
      </form>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6 flex items-center gap-2">
          <AlertCircle className="w-5 h-5" />
          {error}
        </div>
      )}

      {hasSearched && !isLoading && (
        <div className="space-y-6">
          <h3 className="text-sm font-semibold text-zinc-500 uppercase tracking-wide mb-4">
            {results.length} Results Found
          </h3>

          {results.length === 0 && !error && (
            <div className="text-center py-12 text-zinc-500">
              <SearchIcon className="w-12 h-12 mx-auto mb-4 opacity-30" />
              <p>No results found for "{query}"</p>
              <p className="text-sm mt-2">Try different keywords or upload more documents</p>
            </div>
          )}

          {results.map((res) => (
            <div key={res.id} className="bg-white p-6 rounded-xl border border-zinc-200 shadow-sm hover:border-blue-300 transition-colors group">
              <div className="flex justify-between items-start mb-2">
                <span className="inline-flex items-center rounded-full bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 ring-1 ring-inset ring-blue-700/10">
                  Score: {Math.round(res.score * 100)}%
                </span>
                <span className="text-xs text-zinc-400 font-mono">{res.metadata.source}</span>
              </div>
              <p
                className="text-zinc-800 leading-relaxed"
                dangerouslySetInnerHTML={{
                  __html: `"...${highlightText(res.text.substring(0, 300), query)}${res.text.length > 300 ? '...' : ''}"`
                }}
              />
              <div className="mt-4 flex items-center text-blue-600 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer">
                View in context <ArrowRight className="w-4 h-4 ml-1" />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SearchPage;