import React from 'react';
import { useSettingsStore } from '../../store/useStore';
import { ChevronDown, Sparkles } from 'lucide-react';
import { Button } from '../ui/Button';

const Header: React.FC = () => {
  const { provider, model, setProvider, setModel } = useSettingsStore();

  const handleProviderChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setProvider(e.target.value as any);
  };

  const handleModelChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setModel(e.target.value);
  };

  return (
    <header className="h-16 flex items-center justify-between px-6 border-b border-zinc-200 bg-white z-10 sticky top-0">
      <div className="flex items-center space-x-2">
        <span className="text-zinc-500 text-sm">Model:</span>
        <div className="relative group">
          <div className="flex items-center space-x-2 bg-zinc-50 border border-zinc-200 hover:border-zinc-300 rounded-md px-3 py-1.5 transition-colors cursor-pointer">
             <Sparkles className="w-4 h-4 text-blue-600" />
             <select 
               value={provider} 
               onChange={handleProviderChange}
               className="bg-transparent text-sm font-medium text-zinc-900 outline-none appearance-none cursor-pointer"
             >
                <option value="ollama">Ollama</option>
                <option value="openai">OpenAI</option>
                <option value="gemini">Gemini</option>
             </select>
             <span className="text-zinc-300">/</span>
             <select 
               value={model} 
               onChange={handleModelChange}
               className="bg-transparent text-sm font-medium text-zinc-900 outline-none appearance-none cursor-pointer pr-4"
             >
                {provider === 'ollama' && (
                  <>
                    <option value="qwen2.5:3b">qwen2.5:3b</option>
                    <option value="llama3.1:8b">llama3.1:8b</option>
                    <option value="mistral">mistral</option>
                  </>
                )}
                {provider === 'openai' && (
                  <>
                    <option value="gpt-4o">GPT-4o</option>
                    <option value="gpt-4-turbo">GPT-4 Turbo</option>
                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                  </>
                )}
                 {provider === 'gemini' && (
                  <>
                    <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
                    <option value="gemini-1.5-flash">Gemini 1.5 Flash</option>
                  </>
                )}
             </select>
             <ChevronDown className="w-3 h-3 text-zinc-400 absolute right-2 pointer-events-none" />
          </div>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <Button variant="ghost" size="sm">Help</Button>
        <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold text-xs border border-blue-200">
          JD
        </div>
      </div>
    </header>
  );
};

export default Header;