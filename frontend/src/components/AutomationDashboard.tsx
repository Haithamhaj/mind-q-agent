import React, { useState, useEffect } from 'react';
import { Settings, Play, CheckCircle, AlertCircle, Plus } from 'lucide-react';

interface Automation {
    id: string;
    name: string;
    active: boolean;
    execution_count: number;
    last_execution: string | null;
}

interface DashboardData {
    summary: {
        total_automations: number;
        active_automations: number;
        total_executions: number;
        success_rate: number;
    };
    recent_executions: any[];
    automations: Automation[];
}

const AutomationDashboard: React.FC = () => {
    const [data, setData] = useState<DashboardData | null>(null);
    const [loading, setLoading] = useState(true);
    const [prompt, setPrompt] = useState('');
    const [creating, setCreating] = useState(false);
    const [createResult, setCreateResult] = useState<any | null>(null);

    const userId = "user1"; // Hardcoded for MVP

    useEffect(() => {
        fetchDashboard();
    }, []);

    const fetchDashboard = async () => {
        try {
            const res = await fetch(`http://localhost:8000/api/v1/automation/monitoring/dashboard/${userId}`);
            const json = await res.json();
            setData(json);
            setLoading(false);
        } catch (err) {
            console.error(err);
            setLoading(false);
        }
    };

    const handleCreate = async () => {
        if (!prompt.trim()) return;
        setCreating(true);
        setCreateResult(null);
        try {
            const res = await fetch('http://localhost:8000/api/v1/automation/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt, user_id: userId })
            });
            const json = await res.json();
            setCreateResult(json);
            setPrompt('');
            fetchDashboard();
        } catch (err) {
            console.error(err);
        } finally {
            setCreating(false);
        }
    };

    const toggleAutomation = async (id: string, currentActive: boolean) => {
        try {
            await fetch(`http://localhost:8000/api/v1/automation/${id}/activate?active=${!currentActive}`, {
                method: 'POST'
            });
            fetchDashboard();
        } catch (err) {
            console.error(err);
        }
    };

    if (loading) return <div className="p-8">Loading dashboard...</div>;

    return (
        <div className="p-8 max-w-6xl mx-auto">
            <h1 className="text-3xl font-bold mb-8 text-gray-800">Automation Dashboard</h1>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                {[
                    { label: 'Total Automations', value: data?.summary.total_automations, icon: Settings, color: 'text-blue-600' },
                    { label: 'Active', value: data?.summary.active_automations, icon: Play, color: 'text-green-600' },
                    { label: 'Total Executions', value: data?.summary.total_executions, icon: CheckCircle, color: 'text-purple-600' },
                    { label: 'Success Rate', value: `${data?.summary.success_rate}%`, icon: AlertCircle, color: 'text-orange-600' },
                ].map((stat, i) => (
                    <div key={i} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center">
                        <div className={`p-4 rounded-full bg-opacity-10 mr-4 ${stat.color} bg-current`}>
                            <stat.icon size={24} />
                        </div>
                        <div>
                            <p className="text-sm text-gray-500 font-medium">{stat.label}</p>
                            <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                        </div>
                    </div>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Create Automation */}
                <div className="lg:col-span-1">
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 h-full">
                        <h2 className="text-xl font-bold mb-4 flex items-center">
                            <Plus className="mr-2" size={20} /> New Automation
                        </h2>
                        <p className="text-gray-500 mb-4 text-sm">
                            Describe what you want to automate in natural language.
                        </p>
                        <textarea
                            className="w-full p-3 border rounded-lg mb-4 focus:ring-2 focus:ring-blue-500 focus:outline-none h-32"
                            placeholder="e.g., Send me a daily email digest of AI news..."
                            value={prompt}
                            onChange={(e) => setPrompt(e.target.value)}
                        />
                        <button
                            onClick={handleCreate}
                            disabled={creating || !prompt}
                            className={`w-full py-3 rounded-lg font-bold text-white transition-colors ${creating || !prompt ? 'bg-gray-300' : 'bg-blue-600 hover:bg-blue-700'
                                }`}
                        >
                            {creating ? 'Creating...' : 'Create Automation'}
                        </button>

                        {createResult && (
                            <div className="mt-4 p-4 bg-green-50 text-green-700 rounded-lg text-sm">
                                <p className="font-bold">Success!</p>
                                <p>{createResult.explanation}</p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Automation List */}
                <div className="lg:col-span-2">
                    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                        <div className="p-6 border-b border-gray-100">
                            <h2 className="text-xl font-bold">Your Automations</h2>
                        </div>
                        <div className="divide-y divide-gray-100">
                            {data?.automations.length === 0 ? (
                                <div className="p-8 text-center text-gray-400">No automations yet. Create one!</div>
                            ) : (
                                data?.automations.map((auto) => (
                                    <div key={auto.id} className="p-6 flex items-center justify-between hover:bg-gray-50 transition-colors">
                                        <div>
                                            <h3 className="font-bold text-gray-900">{auto.name}</h3>
                                            <div className="flex items-center text-sm text-gray-500 mt-1">
                                                <span className="mr-4">Executions: {auto.execution_count}</span>
                                                <span>Last: {auto.last_execution ? new Date(auto.last_execution).toLocaleDateString() : 'Never'}</span>
                                            </div>
                                        </div>
                                        <button
                                            onClick={() => toggleAutomation(auto.id, auto.active)}
                                            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${auto.active
                                                    ? 'bg-green-100 text-green-700 hover:bg-green-200'
                                                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                                }`}
                                        >
                                            {auto.active ? 'Active' : 'Paused'}
                                        </button>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AutomationDashboard;
