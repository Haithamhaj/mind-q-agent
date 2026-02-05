import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Network, Share2, Database } from 'lucide-react';

const data = [
  { name: 'Concepts', count: 420 },
  { name: 'Relations', count: 1250 },
  { name: 'Chunks', count: 850 },
  { name: 'Sources', count: 15 },
];

const GraphPage: React.FC = () => {
  return (
    <div className="p-8 max-w-6xl mx-auto">
       <div className="flex justify-between items-center mb-8">
        <div>
            <h1 className="text-2xl font-bold text-zinc-900">Knowledge Graph Stats</h1>
            <p className="text-zinc-500 mt-1">Overview of the semantic connections in your knowledge base.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-xl border border-zinc-200 shadow-sm flex items-center">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mr-4">
                <Database className="w-6 h-6 text-purple-600" />
            </div>
            <div>
                <p className="text-sm text-zinc-500 font-medium">Total Nodes</p>
                <p className="text-2xl font-bold text-zinc-900">1,270</p>
            </div>
        </div>
        <div className="bg-white p-6 rounded-xl border border-zinc-200 shadow-sm flex items-center">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
                <Share2 className="w-6 h-6 text-blue-600" />
            </div>
            <div>
                <p className="text-sm text-zinc-500 font-medium">Total Edges</p>
                <p className="text-2xl font-bold text-zinc-900">3,450</p>
            </div>
        </div>
        <div className="bg-white p-6 rounded-xl border border-zinc-200 shadow-sm flex items-center">
             <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mr-4">
                <Network className="w-6 h-6 text-green-600" />
            </div>
            <div>
                <p className="text-sm text-zinc-500 font-medium">Graph Density</p>
                <p className="text-2xl font-bold text-zinc-900">0.42</p>
            </div>
        </div>
      </div>

      {/* Visualization Container Placeholder */}
      <div className="bg-zinc-950 rounded-xl overflow-hidden shadow-lg h-[400px] mb-8 relative border border-zinc-800">
          <div className="absolute top-4 left-4 z-10 bg-zinc-900/80 backdrop-blur px-3 py-1 rounded text-xs text-zinc-300 border border-zinc-700">
              Interactive View
          </div>
          {/* Mock Force Directed Graph using CSS/SVG for aesthetics */}
          <div className="w-full h-full flex items-center justify-center relative overflow-hidden">
             <div className="absolute inset-0 opacity-20">
                <svg width="100%" height="100%">
                    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                        <path d="M 40 0 L 0 0 0 40" fill="none" stroke="white" strokeWidth="0.5"/>
                    </pattern>
                    <rect width="100%" height="100%" fill="url(#grid)" />
                </svg>
             </div>
             <div className="text-center">
                <Network className="w-16 h-16 text-zinc-700 mx-auto mb-4 animate-pulse" />
                <p className="text-zinc-500 text-sm">WebGL Graph Visualization Component</p>
                <p className="text-zinc-700 text-xs mt-1">(Requires react-force-graph)</p>
             </div>
          </div>
      </div>

      {/* Stats Chart */}
      <div className="bg-white p-6 rounded-xl border border-zinc-200 shadow-sm">
        <h3 className="text-lg font-bold text-zinc-900 mb-6">Distribution</h3>
        <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="name" tick={{fill: '#71717a'}} axisLine={false} tickLine={false} />
                    <YAxis tick={{fill: '#71717a'}} axisLine={false} tickLine={false} />
                    <Tooltip 
                        contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                        cursor={{fill: '#f4f4f5'}}
                    />
                    <Bar dataKey="count" fill="#2563eb" radius={[4, 4, 0, 0]} barSize={50} />
                </BarChart>
            </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default GraphPage;