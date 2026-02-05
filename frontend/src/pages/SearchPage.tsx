import React, { useState } from 'react';
import { Search as SearchIcon, ArrowRight } from 'lucide-react';
import { Input } from '../components/ui/Input';
import { Button } from '../components/ui/Button';
import { SearchResult } from '../types';

const SearchPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query) return;

    // Mock search results
    setResults([
      { id: '1', text: 'The quarterly financial report indicates a 20% growth in the APAC region...', score: 0.89, metadata: { source: 'Q3_Financials.csv' } },
      { id: '2', text: 'Project Alpha specifications require a latency of under 50ms for the realtime module...', score: 0.75, metadata: { source: 'Project_Specs.pdf' } },
      { id: '3', text: 'Meeting notes from 10/28 suggest we move the deadline to next Friday...', score: 0.62, metadata: { source: 'Meeting_Notes.txt' } },
    ]);
    setHasSearched(true);
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
            placeholder="Search for concepts, e.g. 'project alpha latency requirements'..." 
            className="pl-10 h-12 text-lg shadow-sm"
          />
        </div>
        <Button type="submit" size="lg" className="h-12 px-8">Search</Button>
      </form>

      {hasSearched && (
        <div className="space-y-6">
            <h3 className="text-sm font-semibold text-zinc-500 uppercase tracking-wide mb-4">
                {results.length} Results Found
            </h3>
            
            {results.map((res) => (
                <div key={res.id} className="bg-white p-6 rounded-xl border border-zinc-200 shadow-sm hover:border-blue-300 transition-colors group">
                    <div className="flex justify-between items-start mb-2">
                        <span className="inline-flex items-center rounded-full bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 ring-1 ring-inset ring-blue-700/10">
                            Score: {Math.round(res.score * 100)}%
                        </span>
                        <span className="text-xs text-zinc-400 font-mono">{res.metadata.source}</span>
                    </div>
                    <p className="text-zinc-800 leading-relaxed">
                        "...<span className="font-semibold text-zinc-900 bg-yellow-100 px-0.5">{res.text.substring(0, 50)}</span>{res.text.substring(50)}..."
                    </p>
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