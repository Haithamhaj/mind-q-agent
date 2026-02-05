import React, { useEffect, useState, useRef } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
import cytoscape from 'cytoscape';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Network, Share2, Database, Loader2, RefreshCw, ZoomIn, ZoomOut, Maximize } from 'lucide-react';
import { Button } from '../components/ui/Button';

interface GraphStats {
    nodes: number;
    edges: number;
    status: string;
}

interface CyElement {
    data: {
        id?: string;
        label?: string;
        type?: string;
        source?: string;
        target?: string;
    };
}

const GraphPage: React.FC = () => {
    const [stats, setStats] = useState<GraphStats | null>(null);
    const [elements, setElements] = useState<CyElement[]>([]);
    const [loading, setLoading] = useState(true);
    const [graphLoading, setGraphLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const cyRef = useRef<cytoscape.Core | null>(null);

    const fetchStats = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch('/api/v1/graph/stats');
            if (!response.ok) {
                throw new Error('Failed to fetch stats');
            }
            const data = await response.json();
            setStats(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unknown error');
        } finally {
            setLoading(false);
        }
    };

    const fetchGraphData = async () => {
        setGraphLoading(true);
        try {
            const response = await fetch('/api/v1/graph/visualize');
            if (!response.ok) {
                throw new Error('Failed to fetch graph data');
            }
            const data: CyElement[] = await response.json();
            setElements(data);
        } catch (err) {
            console.error('Graph fetch error:', err);
        } finally {
            setGraphLoading(false);
        }
    };

    useEffect(() => {
        fetchStats();
        fetchGraphData();
    }, []);

    const handleZoomIn = () => {
        if (cyRef.current) {
            cyRef.current.zoom(cyRef.current.zoom() * 1.2);
        }
    };

    const handleZoomOut = () => {
        if (cyRef.current) {
            cyRef.current.zoom(cyRef.current.zoom() * 0.8);
        }
    };

    const handleFit = () => {
        if (cyRef.current) {
            cyRef.current.fit(undefined, 50);
        }
    };

    const chartData = stats ? [
        { name: 'Nodes', count: stats.nodes },
        { name: 'Edges', count: stats.edges },
    ] : [];

    // Cytoscape stylesheet
    const cytoscapeStylesheet: cytoscape.Stylesheet[] = [
        {
            selector: 'node[type="Document"]',
            style: {
                'background-color': '#3b82f6',
                'label': 'data(label)',
                'color': '#1e3a5f',
                'text-valign': 'bottom',
                'text-halign': 'center',
                'font-size': '10px',
                'text-margin-y': 8,
                'width': 40,
                'height': 40,
                'border-width': 3,
                'border-color': '#1d4ed8',
            },
        },
        {
            selector: 'node[type="Concept"]',
            style: {
                'background-color': '#a855f7',
                'label': 'data(label)',
                'color': '#4c1d95',
                'text-valign': 'bottom',
                'text-halign': 'center',
                'font-size': '9px',
                'text-margin-y': 6,
                'width': 30,
                'height': 30,
                'border-width': 2,
                'border-color': '#7c3aed',
            },
        },
        {
            selector: 'edge',
            style: {
                'width': 2,
                'line-color': '#94a3b8',
                'target-arrow-color': '#94a3b8',
                'target-arrow-shape': 'triangle',
                'curve-style': 'bezier',
                'opacity': 0.7,
            },
        },
        {
            selector: 'node:selected',
            style: {
                'border-width': 4,
                'border-color': '#f59e0b',
            },
        },
    ];

    return (
        <div className="p-8 max-w-6xl mx-auto">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-zinc-900">Knowledge Graph</h1>
                    <p className="text-zinc-500 mt-1">Explore semantic connections in your knowledge base.</p>
                </div>
                <Button onClick={() => { fetchStats(); fetchGraphData(); }} disabled={loading} variant="secondary" size="sm">
                    <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                    Refresh
                </Button>
            </div>

            {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
                    {error}
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-white p-6 rounded-xl border border-zinc-200 shadow-sm flex items-center">
                    <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mr-4">
                        <Database className="w-6 h-6 text-purple-600" />
                    </div>
                    <div>
                        <p className="text-sm text-zinc-500 font-medium">Total Nodes</p>
                        <p className="text-2xl font-bold text-zinc-900">
                            {loading ? <Loader2 className="w-6 h-6 animate-spin" /> : (stats ? stats.nodes.toLocaleString() : '0')}
                        </p>
                    </div>
                </div>
                <div className="bg-white p-6 rounded-xl border border-zinc-200 shadow-sm flex items-center">
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
                        <Share2 className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                        <p className="text-sm text-zinc-500 font-medium">Total Edges</p>
                        <p className="text-2xl font-bold text-zinc-900">
                            {loading ? <Loader2 className="w-6 h-6 animate-spin" /> : (stats ? stats.edges.toLocaleString() : '0')}
                        </p>
                    </div>
                </div>
                <div className="bg-white p-6 rounded-xl border border-zinc-200 shadow-sm flex items-center">
                    <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mr-4">
                        <Network className="w-6 h-6 text-green-600" />
                    </div>
                    <div>
                        <p className="text-sm text-zinc-500 font-medium">Graph Density</p>
                        <p className="text-2xl font-bold text-zinc-900">
                            {loading ? <Loader2 className="w-6 h-6 animate-spin" /> : (stats ? (stats.edges / Math.max(stats.nodes, 1)).toFixed(2) : '0')}
                        </p>
                    </div>
                </div>
            </div>

            {/* Interactive Graph Visualization */}
            <div className="bg-zinc-950 rounded-xl overflow-hidden shadow-lg h-[500px] mb-8 relative border border-zinc-800">
                {/* Controls */}
                <div className="absolute top-4 left-4 z-10 flex gap-2">
                    <div className="bg-zinc-900/80 backdrop-blur px-3 py-1 rounded text-xs text-zinc-300 border border-zinc-700">
                        Interactive View
                    </div>
                </div>
                <div className="absolute top-4 right-4 z-10 flex gap-2">
                    <Button variant="secondary" size="icon" onClick={handleZoomIn} className="w-8 h-8 bg-zinc-800 border-zinc-700 hover:bg-zinc-700">
                        <ZoomIn className="w-4 h-4 text-zinc-300" />
                    </Button>
                    <Button variant="secondary" size="icon" onClick={handleZoomOut} className="w-8 h-8 bg-zinc-800 border-zinc-700 hover:bg-zinc-700">
                        <ZoomOut className="w-4 h-4 text-zinc-300" />
                    </Button>
                    <Button variant="secondary" size="icon" onClick={handleFit} className="w-8 h-8 bg-zinc-800 border-zinc-700 hover:bg-zinc-700">
                        <Maximize className="w-4 h-4 text-zinc-300" />
                    </Button>
                </div>

                {/* Legend */}
                <div className="absolute bottom-4 left-4 z-10 bg-zinc-900/80 backdrop-blur px-3 py-2 rounded text-xs border border-zinc-700 flex gap-4">
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                        <span className="text-zinc-300">Documents</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-purple-500"></div>
                        <span className="text-zinc-300">Concepts</span>
                    </div>
                </div>

                {graphLoading ? (
                    <div className="w-full h-full flex items-center justify-center">
                        <div className="text-center">
                            <Loader2 className="w-12 h-12 text-zinc-500 mx-auto mb-4 animate-spin" />
                            <p className="text-zinc-500 text-sm">Loading graph...</p>
                        </div>
                    </div>
                ) : elements.length === 0 ? (
                    <div className="w-full h-full flex items-center justify-center">
                        <div className="text-center">
                            <Network className="w-16 h-16 text-zinc-700 mx-auto mb-4" />
                            <p className="text-zinc-500 text-sm">No graph data available</p>
                            <p className="text-zinc-700 text-xs mt-1">Upload some documents to see connections</p>
                        </div>
                    </div>
                ) : (
                    <CytoscapeComponent
                        elements={elements}
                        stylesheet={cytoscapeStylesheet}
                        layout={{ name: 'cose', animate: true, animationDuration: 500 }}
                        style={{ width: '100%', height: '100%' }}
                        cy={(cy) => { cyRef.current = cy; }}
                        wheelSensitivity={0.3}
                    />
                )}
            </div>

            {/* Stats Chart */}
            {stats && (
                <div className="bg-white p-6 rounded-xl border border-zinc-200 shadow-sm">
                    <h3 className="text-lg font-bold text-zinc-900 mb-6">Distribution</h3>
                    <div className="h-[300px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={chartData}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                <XAxis dataKey="name" tick={{ fill: '#71717a' }} axisLine={false} tickLine={false} />
                                <YAxis tick={{ fill: '#71717a' }} axisLine={false} tickLine={false} />
                                <Tooltip
                                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                    cursor={{ fill: '#f4f4f5' }}
                                />
                                <Bar dataKey="count" fill="#2563eb" radius={[4, 4, 0, 0]} barSize={50} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            )}
        </div>
    );
};

export default GraphPage;