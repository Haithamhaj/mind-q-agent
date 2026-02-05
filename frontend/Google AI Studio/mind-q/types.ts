export interface Document {
  id: string;
  name: string;
  path: string;
  type: string;
  size: number;
  created_at: string;
  processed: boolean;
  progress?: number;
}

export interface ChatRequest {
  message: string;
  model: string;   // e.g. "qwen2.5:3b" or "gpt-4o"
  provider: "ollama" | "openai" | "gemini";
  stream: boolean;
}

export interface ChatResponse {
  response: string;
  context_used: boolean;
  sources: string[];
}

export interface SearchResult {
  id: string;
  text: string;
  score: number;
  metadata: Record<string, any>;
}

export interface GraphStats {
  node_count: number;
  edge_count: number;
  density: number;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

export type LLMProvider = 'ollama' | 'openai' | 'gemini';