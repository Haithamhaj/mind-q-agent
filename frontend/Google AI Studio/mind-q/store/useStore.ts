import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { LLMProvider } from '../types';

interface SettingsState {
  provider: LLMProvider;
  model: string;
  openaiKey: string;
  geminiKey: string;
  
  setProvider: (provider: LLMProvider) => void;
  setModel: (model: string) => void;
  setOpenaiKey: (key: string) => void;
  setGeminiKey: (key: string) => void;
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      provider: 'ollama',
      model: 'qwen2.5:3b',
      openaiKey: '',
      geminiKey: '',
      
      setProvider: (provider) => set({ provider }),
      setModel: (model) => set({ model }),
      setOpenaiKey: (key) => set({ openaiKey: key }),
      setGeminiKey: (key) => set({ geminiKey: key }),
    }),
    {
      name: 'mind-q-settings',
    }
  )
);