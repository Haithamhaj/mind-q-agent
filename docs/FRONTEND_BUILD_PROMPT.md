# Mind-Q Frontend Build Specification (Master Prompt)

**Role**: You are an expert Frontend Engineer and UI/UX Designer specializing in building AI Interfaces similar to **Google AI Studio** and **ChatGPT**.

**Goal**: Build a modern, clean, and responsive React application for **Mind-Q**, a local-first intelligent knowledge agent.

---

## 🎨 Design Philosophy (The "Google AI Studio" Look)
- **Aesthetic**: Extreme minimalism. Use plenty of whitespace.
- **Color Palette**: 
  - Backgrounds: `bg-white` (Light) / `bg-zinc-950` (Dark).
  - Surfaces: `bg-zinc-50` / `bg-zinc-900`.
  - Accents: Deep Blue (`blue-600`) for primary actions.
  - Text: High contrast for readability (`text-zinc-900` / `text-zinc-100`).
- **Layout**: 
  - **Sidebar**: Collapsible, floating or sleek left rail.
  - **Main Area**: Centered content. "Floating" cards for inputs.
  - **Typography**: Inter or Roboto (Clean sans-serif).
- **Interactions**: Snappy, instant feedback, skeleton loaders.

---

## 🛠️ Tech Stack Requirements
- **Framework**: Vite + React + TypeScript.
- **Styling**: TailwindCSS.
- **Icons**: Lucide React.
- **Components**: Radix UI or Shadcn/UI (highly recommended for the premium feel).
- **State Management**: Zustand or React Context.
- **Networking**: TanStack Query (React Query) + Axios.
- **Markdown**: `react-markdown` + `remark-gfm` + `react-syntax-highlighter` (for code blocks).

---

## 🔌 Backend API Specification
The backend is running at `http://localhost:8000/api/v1`.

### 1. Chat & LLM (`/chat`)
- **POST `/chat`**: Send a message.
  - Payload: `{ "message": "Hi", "model": "qwen2.5:3b", "provider": "ollama", "stream": true }`
  - **Requirement**: Use **Streaming** response handling to show text character-by-character.
  - **UI**: 
    - Chat Bubble layout (User Right / AI Left).
    - **Model Switcher**: A dropdown in the header to select Provider (Ollama/OpenAI/Gemini) and Model Name.

### 2. Documents Library (`/documents`)
- **POST `/documents/upload`**: Multipart/form-data upload.
- **GET `/documents`**: List all files.
- **UI**: Drag-and-drop zone. Table view of files with status icons.

### 3. Search (`/search`)
- **GET `/search?q=...`**: Returns semantic search results.
- **UI**: A global search bar (Cmd+K style) or a dedicated search page with highlighted result snippets.

### 4. Knowledge Graph (`/graph`)
- **GET `/graph/stats`**: Node/Edge counts.
- **GET `/graph/visualize`**: Data for visualization.
- **UI**: A dashboard widget showing "Total Concepts" and "Total Connections".

### 5. Settings (`/preferences`)
- **GET/PATCH `/preferences`**: User settings.
- **UI Requirements**:
  - **API Key Manager**: Secure input fields for `OPENAI_API_KEY` and `GEMINI_API_KEY`.
  - Save these in **LocalStorage** (for client-side usage) or send to backend if backend proxying is preferred (Phase 4B uses backend proxy, so inputs should just verify or save to user config).

---

## 📱 Core Features to Build

### 1. The Shell (Layout)
- Sidebar with navigation:
  - 💬 **Chat** (Home)
  - 📂 **Library** (Documents)
  - 🔍 **Search**
  - 🕸️ **Graph**
  - ⚙️ **Settings**
- Header with **Model Switcher** (Dropdown).

### 2. Chat Interface (Priority #1)
- Center stage input box (floating, shadow-lg).
- Auto-growing textarea.
- Markdown rendering for AI responses (Tables, Code blocks).
- "Stop Generating" button.

### 3. Settings Page
- Tabbed interface (General, Models, Keys).
- Input fields for API Keys.

---

## 🚀 Implementation Steps for You
1. Initialize Vite project with TypeScript & Tailwind.
2. Set up the Router (React Router).
3. Create the Layout (Sidebar + Header).
4. Build the `ChatInterface` component with Streaming logic.
5. Build the `ModelSelector` component.
6. Build the `DocumentUploader` component.

**Start by scaffolding the project structure and the Main Layout.**

---

## 🏗️ Appendix: Data Models (TypeScript Interfaces)
Use these exact types to ensure compatibility with the Backend.

```typescript
// src/api/types.ts

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
```

## 📂 Recommended Folder Structure
```
src/
├── api/          # Axios client & types
├── components/   # Reusable UI components
│   ├── ui/       # Shadcn primitives (Button, Input, etc.)
│   ├── chat/     # Chat-specific components
│   └── shared/   # Layouts, Headers, Sidebar
├── hooks/        # React hooks (useChat, useDocuments)
├── pages/        # Route pages
├── store/        # Zustand store (useSettingsStore)
└── lib/          # Utils (cn, formatters)
```
