import React from 'react';
import { useSettingsStore } from '../store/useStore';
import { Input } from '../components/ui/Input';
import { Button } from '../components/ui/Button';
import { Save, Key } from 'lucide-react';

const SettingsPage: React.FC = () => {
    const { openaiKey, geminiKey, setOpenaiKey, setGeminiKey } = useSettingsStore();
    const [localOpenai, setLocalOpenai] = React.useState(openaiKey);
    const [localGemini, setLocalGemini] = React.useState(geminiKey);
    const [saved, setSaved] = React.useState(false);

    const handleSave = (e: React.FormEvent) => {
        e.preventDefault();
        setOpenaiKey(localOpenai);
        setGeminiKey(localGemini);
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
    };

    return (
        <div className="max-w-3xl mx-auto p-8">
            <h1 className="text-2xl font-bold text-zinc-900 mb-2">Settings</h1>
            <p className="text-zinc-500 mb-8">Manage your API keys and application preferences.</p>

            <div className="bg-white border border-zinc-200 rounded-xl shadow-sm overflow-hidden">
                <div className="p-6 border-b border-zinc-200 bg-zinc-50">
                    <div className="flex items-center">
                        <Key className="w-5 h-5 text-zinc-500 mr-2" />
                        <h2 className="font-semibold text-zinc-900">API Credentials</h2>
                    </div>
                    <p className="text-sm text-zinc-500 mt-1 ml-7">
                        Keys are stored locally in your browser and used to authenticate requests via the backend proxy.
                    </p>
                </div>

                <form onSubmit={handleSave} className="p-6 space-y-6">
                    <div>
                        <Input
                            label="OpenAI API Key"
                            type="password"
                            placeholder="sk-..."
                            value={localOpenai}
                            onChange={(e) => setLocalOpenai(e.target.value)}
                        />
                        <p className="text-xs text-zinc-400 mt-1">Required for GPT-4o models.</p>
                    </div>

                    <div>
                        <Input
                            label="Gemini API Key"
                            type="password"
                            placeholder="AIza..."
                            value={localGemini}
                            onChange={(e) => setLocalGemini(e.target.value)}
                        />
                        <p className="text-xs text-zinc-400 mt-1">Required for Gemini 1.5 models.</p>
                    </div>

                    <div className="pt-4 flex items-center justify-between">
                        <span className={`text-sm font-medium ${saved ? 'text-green-600' : 'text-transparent'} transition-colors`}>
                            Settings saved successfully.
                        </span>
                        <Button type="submit">
                            <Save className="w-4 h-4 mr-2" />
                            Save Changes
                        </Button>
                    </div>
                </form>
            </div>

            <div className="mt-8 bg-white border border-zinc-200 rounded-xl shadow-sm p-6">
                <h2 className="font-semibold text-zinc-900 mb-4">Backend Connection</h2>
                <div className="flex items-center justify-between p-4 bg-zinc-50 rounded-lg border border-zinc-200">
                    <div>
                        <p className="text-sm font-medium text-zinc-900">API Endpoint</p>
                        <p className="text-xs text-zinc-500 font-mono mt-1">/api/v1</p>
                    </div>
                    <div className="flex items-center">
                        <div className="w-2.5 h-2.5 rounded-full bg-green-500 mr-2 animate-pulse"></div>
                        <span className="text-xs font-medium text-green-700">Connected</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SettingsPage;