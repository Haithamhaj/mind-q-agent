
export interface Document {
    id: string;
    name: string;
    path: string;
    type: string;
    size: number;
    created_at: string;
    processed: boolean;
}

export interface ChatRequest {
    message: string;
    model: string;
    provider: "ollama" | "openai" | "gemini";
    temperature?: number;
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
