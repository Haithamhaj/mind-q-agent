import React, { useState } from 'react';
import { Search as SearchIcon, ArrowRight, Loader2, AlertCircle, Youtube, BookOpen, Database } from 'lucide-react';
import { Input } from '../components/ui/Input';
import { Button } from '../components/ui/Button';

interface SearchResult {
  id: string;
  text: string;
  title?: string;
  url?: string;
  score?: number;
  metadata: {
    source?: string;
    doc_hash?: string;
    channel?: string;
    authors?: string[];
    published?: string;
    [key: string]: any;
  };
}

const API_BASE = '/api/v1';

type SearchSource = 'internal' | 'youtube' | 'arxiv';

const SearchPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [source, setSource] = useState<SearchSource>('internal');
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
    setResults([]);

    try {
      let endpoint = '';
      if (source === 'internal') {
        endpoint = `${API_BASE}/search/?q=${encodeURIComponent(query.trim())}&limit=10`;
      } else if (source === 'youtube') {
        endpoint = `${API_BASE}/smart/search/youtube?q=${encodeURIComponent(query.trim())}&max_results=10`;
      } else if (source === 'arxiv') {
        endpoint = `${API_BASE}/smart/search/arxiv?q=${encodeURIComponent(query.trim())}&max_results=10`;
      }

      const response = await fetch(endpoint);

      if (!response.ok) {
        throw new Error(`Search failed: ${response.statusText}`);
      }

      const data = await response.json();

      let mappedResults: SearchResult[] = [];

      if (source === 'internal') {
        mappedResults = data.map((item: any, index: number) => ({
          id: item.id || `result-${index}`,
          text: item.text || item.content || item.chunk || '',
          score: item.score || item.similarity || 0,
          metadata: {
            source: item.metadata?.source || item.source || 'Internal Knowledge',
            ...item.metadata
          }
        }));
      } else if (source === 'youtube') {
        mappedResults = data.map((item: any, index: number) => ({
          id: item.url || `yt-${index}`,
          title: item.title,
          text: item.description || '',
          url: item.url,
          metadata: {
            source: 'YouTube',
            channel: item.channel,
            ...item
          }
        }));
      } else if (source === 'arxiv') {
        mappedResults = data.map((item: any, index: number) => ({
          id: item.url || `ax-${index}`,
          title: item.title,
          text: item.summary || '',
          url: item.url,
          metadata: {
            source: 'ArXiv',
            authors: item.authors,
            published: item.published,
            ...item
          }
        }));
      }

      setResults(mappedResults);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
    } finally {
      setIsLoading(false);
    }
  };

  const highlightText = (text: string, searchQuery: string) => {
    if (!searchQuery.trim() || !text) return text || '';
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
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-zinc-900 mb-4">Smart Search</h1>
        <p className="text-zinc-500 max-w-xl mx-auto">
          Search across your internal knowledge base, YouTube, and ArXiv research papers.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex justify-center mb-8">
        <div className="bg-zinc-100 p-1 rounded-xl flex gap-1">
          {[
            { id: 'internal', label: 'Internal DB', icon: Database },
            { id: 'youtube', label: 'YouTube', icon: Youtube },
            { id: 'arxiv', label: 'Research', icon: BookOpen },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setSource(tab.id as SearchSource)}
              className={`flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-all ${source === tab.id
                ? 'bg-white text-zinc-900 shadow-sm'
                : 'text-zinc-500 hover:text-zinc-700'
                }`}
            >
              <tab.icon className="w-4 h-4 mr-2" />
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      <form onSubmit={handleSearch} className="flex gap-3 mb-12">
        <div className="relative flex-1">
          <SearchIcon className="absolute left-3 top-2.5 w-5 h-5 text-zinc-400" />
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={`Search ${source === 'internal' ? 'internal knowledge' : source}...`}
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
            {results.length} Results Found ({source})
          </h3>

          {results.length === 0 && !error && (
            <div className="text-center py-12 text-zinc-500">
              <SearchIcon className="w-12 h-12 mx-auto mb-4 opacity-30" />
              <p>No results found for "{query}"</p>
            </div>
          )}

          {results.map((res) => (
            <div key={res.id} className="bg-white p-6 rounded-xl border border-zinc-200 shadow-sm hover:border-blue-300 transition-colors group">
              <div className="flex justify-between items-start mb-2">
                <div className="flex-1">
                  {res.title && (
                    <a href={res.url} target="_blank" rel="noopener noreferrer" className="text-lg font-bold text-blue-600 hover:underline block mb-1">
                      {res.title}
                    </a>
                  )}
                  <div className="flex items-center gap-2 text-xs text-zinc-500">
                    <span className="font-medium bg-zinc-100 px-2 py-0.5 rounded">{res.metadata.source}</span>
                    {res.metadata.channel && <span>• {res.metadata.channel}</span>}
                    {res.metadata.authors && <span>• {res.metadata.authors.slice(0, 2).join(', ')}</span>}
                    {res.metadata.published && <span>• {new Date(res.metadata.published).toLocaleDateString()}</span>}
                  </div>
                </div>
                {res.score !== undefined && source === 'internal' && (
                  <span className="inline-flex items-center rounded-full bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 ring-1 ring-inset ring-blue-700/10">
                    {Math.round(res.score * 100)}%
                  </span>
                )}
              </div>

              <p
                className="text-zinc-800 leading-relaxed text-sm"
                dangerouslySetInnerHTML={{
                  __html: highlightText((res.text || '').substring(0, 300) + (res.text && res.text.length > 300 ? '...' : ''), query)
                }}
              />

              {(res.url || source === 'internal') && (
                <div className="mt-4 flex items-center text-blue-600 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer">
                  <a href={res.url || '#'} target={res.url ? "_blank" : "_self"} rel="noopener noreferrer" className="flex items-center">
                    {res.url ? 'View Content' : 'View in Context'} <ArrowRight className="w-4 h-4 ml-1" />
                  </a>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SearchPage;