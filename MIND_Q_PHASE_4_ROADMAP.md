# 🗺️ Mind-Q Phase 4: Master Roadmap

**Status:** Draft / Ready for Execution  
**Total Tasks:** 50 (41-90)  
**Goal:** Transform Mind-Q from a backend engine into a complete personal knowledge operating system.

---

## 🔷 PHASE 4A: API LAYER (Tasks 41-50)
*Foundation for UI and Automation.*

### Task 41: FastAPI Project Setup 🚀
- **Goal**: Initialize the API server.
- **Steps**:
  - [ ] Create `mind_q_agent/api/app.py` with FastAPI instance.
  - [ ] Configure CORS (allow localhost).
  - [ ] Create `mind_q_agent/api/settings.py`.
  - [ ] Implement Exception Handlers.
- **🧪 Verification**:
  - Run `uvicorn mind_q_agent.api.app:app`.
  - Access `http://localhost:8000/docs`.
  - Verify `/health` returns `{"status": "ok"}`.

### Task 42: Documents API Endpoints 📄
- **Goal**: Upload and manage files via HTTP.
- **Steps**:
  - [ ] `POST /documents/upload`: Handle file upload, save to temp, trigger ingestion.
  - [ ] `GET /documents`: List all documents from KùzuDB/Chroma.
  - [ ] `GET /documents/{id}`: Get metadata.
- **🧪 Verification**:
  - Use Swagger UI to upload a test PDF.
  - Verify file appears in `data/uploads` and Graph DB.

### Task 43: Search API Endpoint 🔍
- **Goal**: Expose semantic search.
- **Steps**:
  - [ ] `GET /search`: Query parameter `q`, returns ranked results.
  - [ ] Integrate `SearchEngine.search()`.
- **🧪 Verification**:
  - Request `/search?q=test`.
  - Verify JSON response matches expected schema (compatible with n8n).

### Task 44: Graph API Endpoint 🕸️
- **Goal**: Data for visualization.
- **Steps**:
  - [ ] `GET /graph/stats`: Node/edge counts.
  - [ ] `GET /graph/visualize`: Nodes/edges in Cytoscape format.
- **🧪 Verification**:
  - Request `/graph/stats`.
  - Check counts match database reality.

### Task 45: Real-Time & WebSockets ⚡
- **Goal**: Live updates for UI/n8n.
- **Steps**:
  - [ ] `WebSocket /ws/events`: Broadcast ingestion/learning events.
  - [ ] Event Bus implementation.
- **🧪 Verification**:
  - Connect via `wscat` or Postman.
  - Trigger an ingestion and verify message receipt.

### Task 46: User Preferences API ⚙️
- **Goal**: Save settings persistence.
- **Steps**:
  - [ ] SQLite `preferences` table.
  - [ ] `GET/PATCH /preferences`.
- **🧪 Verification**:
  - Update a setting via API.
  - Restart server and verify setting persists.

### Task 47: Concept Controls API 🧠
- **Goal**: Adjust learning parameters.
- **Steps**:
  - [ ] `POST /concepts/{name}/boost`: Manually increase weight.
  - [ ] `POST /concepts/{name}/mute`: Ignore concept.
- **🧪 Verification**:
  - Boost a concept.
  - Verify weight increase in KùzuDB.

### Task 48: Statistics & Analytics API 📊
- **Goal**: Usage metrics.
- **Steps**:
  - [ ] `GET /analytics`: Queries per day, new concepts count.
- **🧪 Verification**:
  - Compare API output with direct SQL count.

### Task 49: Export/Import API 📦
- **Goal**: Backup/Restore.
- **Steps**:
  - [ ] `GET /backup`: Zip data directory.
  - [ ] `POST /restore`: Restore data directory.
- **🧪 Verification**:
  - Create backup, wipe data, restore, verify data exists.

### Task 50: OpenAPI Spec for n8n 📚
- **Goal**: Ensure n8n compatibility.
- **Steps**:
  - [ ] Annotate all models (Pydantic).
  - [ ] Customize `openapi.json` for n8n Import.
- **🧪 Verification**:
  - Import OAS into n8n "HTTP Request" node builder (if available) or verify valid JSON schema.

---

## 🔷 PHASE 4B: LLM INTEGRATION (Tasks 51-60)
*The "Brain" of the operation.*

### Task 51: LLM Manager Core 🤖
- **Goal**: Unified interface for AI models.
- **Steps**:
  - [ ] `LLMProvider` abstract base class.
  - [ ] `ModelConfig` management.
- **🧪 Verification**:
  - Unit test: Mock provider returns response.

### Task 52: Local LLM (Ollama) Implementation 🦙
- **Goal**: Free, local privacy.
- **Steps**:
  - [ ] `OllamaProvider` implementation.
  - [ ] Streaming support.
- **🧪 Verification**:
  - Ensure Ollama is running.
  - Send "Hello" via provider, verify response.

### Task 53: Local LLM (LlamaCpp) Implementation 🏎️
- **Goal**: Direct GGUF loading (optional fallback).
- **Steps**:
  - [ ] `LlamaCppProvider`.
  - [ ] Integration with `llama-cpp-python`.
- **🧪 Verification**:
  - Load a small model (e.g., TinyLlama).
  - Generate token.

### Task 54: OpenAI Integration ☁️
- **Goal**: Powerful cloud fallback.
- **Steps**:
  - [ ] `OpenAIProvider`.
  - [ ] Config API Key handling.
- **🧪 Verification**:
  - Test with valid key.

### Task 55: Anthropic/Gemini Integration 🧠
- **Goal**: Alternative cloud providers.
- **Steps**:
  - [ ] `AnthropicProvider` / `GeminiProvider`.
- **🧪 Verification**:
  - Test with valid key.

### Task 57: Context Builder 📚
- **Goal**: RAG Logic.
- **Steps**:
  - [ ] Retrieve vector results + graph neighbors.
  - [ ] Format into System Prompt.
- **🧪 Verification**:
  - Query "Project X".
  - Verify context string contains Project X details.

### Task 58: Chat API Endpoint 💬
- **Goal**: Conversational Interface.
- **Steps**:
  - [ ] `POST /chat`: Accepting messages.
  - [ ] Streaming response handling.
- **🧪 Verification**:
  - Send chat request.
  - Receive relevant answer based on loaded docs.

### Task 59: Prompt Templates System 📝
- **Goal**: Customizable persona.
- **Steps**:
  - [ ] Template storage (YAML).
  - [ ] Template selection API.
- **🧪 Verification**:
  - Change template to "Pirate".
  - Verify responses sound like a pirate.

### Task 60: LLM Response Processing 🔄
- **Goal**: Structured output & Feedback.
- **Steps**:
  - [ ] Extract citations ( [1] ).
  - [ ] Auto-create new graph links from answers.
- **🧪 Verification**:
  - Ask question.
  - Verify answer includes accurate citation links.

---

## 🔷 PHASE 4C: FRONTEND UI (Tasks 61-70)
*The Face of Mind-Q.*

### Design Philosophy 🎨
> **Inspiration**: Google AI Studio / Material 3.
> **Core Values**: Clean, Content-First, Minimalist, "Floating" Panels.
> **Theme**: Neutral Grayscale with Blue Intentions.


### Task 61: React Setup ⚛️
- **Goal**: Initialize UI.
- **Steps**:
  - [ ] Vite + React + TypeScript.
  - [ ] TailwindCSS/Shadcn setup.
- **🧪 Verification**:
  - `npm run dev` loads default page.

### Task 62: Component Library & Layout 🎨
- **Goal**: Basic structure.
- **Steps**:
  - [ ] Sidebar, Header, Main Layout.
  - [ ] Theme provider (Dark/Light).
- **🧪 Verification**:
  - Visual check of responsive layout.

### Task 63: Dashboard Page 📊
- **Goal**: Overview.
- **Steps**:
  - [ ] Stats widgets (Task 48 integration).
- **🧪 Verification**:
  - Verify numbers match API.

### Task 64: Documents Manager UI 📂
- **Goal**: Manage files.
- **Steps**:
  - [ ] File Upload drag-and-drop.
  - [ ] Document list table.
- **🧪 Verification**:
  - Upload file via UI -> Check API -> Check DB.

### Task 65: Chat Interface 💬
- **Goal**: The main interaction point.
- **Steps**:
  - [ ] Chat bubble layout.
  - [ ] Markdown rendering.
  - [ ] Streaming support.
  - [ ] **[USER REQUEST]** Model Quick-Switcher in header.
- **🧪 Verification**:
  - Chat flow works smoothly without page reload.

### Task 66: Knowledge Graph Viz 🕸️
- **Goal**: Visual exploration.
- **Steps**:
  - [ ] Cytoscape.js integration.
  - [ ] Dynamic loading of nodes.
- **🧪 Verification**:
  - Graph interacts (zoom/pan/click).

### Task 67: Search Interface 🔍
- **Goal**: Google-like search.
- **Steps**:
  - [ ] Search bar + Results list.
- **🧪 Verification**:
  - Search returns highlighted results.

### Task 68: Settings Page ⚙️
- **Goal**: Config UI.
- **Steps**:
  - [ ] LLM selection dropdown (Global default).
  - [ ] **[USER REQUEST]** Secure API Key Input Fields (OpenAI / Gemini).
  - [ ] Local Storage persistence for Keys.
- **🧪 Verification**:
  - Change LLM, verify chat uses new model.

### Task 69: Concept Details Modal 💡
- **Goal**: Deep dive.
- **Steps**:
  - [ ] Click node -> Open modal with details/history.
- **🧪 Verification**:
  - Click "Artificial Intelligence" node, see definition.

### Task 70: Responsive Polish 📱
- **Goal**: Mobile support.
- **Steps**:
  - [ ] Mobile navigation.
  - [ ] Touch adjustments.
- **🧪 Verification**:
  - Chrome Mobile Simulator check.

---

## 🔷 PHASE 4D: AUTOMATION via n8n (Tasks 71-80) [REVISED]
*Integration with the best open-source automation tool.*

### Task 71: n8n Integration Service 🔧
- **Goal**: Middleware between Mind-Q and n8n.
- **Steps**:
  - [ ] `IngestionWebhook` for n8n to push content.
  - [ ] `ActionRunner` to execute Mind-Q commands from n8n.
- **🧪 Verification**:
  - Call webhook manually, verify ingestion starts.

### Task 72: Webhooks Event System 📡
- **Goal**: Push Mind-Q events to n8n.
- **Steps**:
  - [ ] Configurable webhook URLs list.
  - [ ] Event triggers (File Added, Concept Created).
- **🧪 Verification**:
  - Set webhook. Add file. Verify receiver gets JSON.

### Task 73: Auto-Discovery Workflow (n8n) 🌍
- **Goal**: Web scraping via n8n.
- **Steps**:
  - [ ] Create n8n workflow JSON.
  - [ ] Schedule -> HTTP Request (News) -> Mind-Q Integration.
- **🧪 Verification**:
  - Run workflow in n8n. Verify new document in Mind-Q.

### Task 74: Email Digest Workflow (n8n) 📧
- **Goal**: Daily summary.
- **Steps**:
  - [ ] Schedule -> Mind-Q API (Stats/Recent) -> Email/Slack.
- **🧪 Verification**:
  - Trigger manually, receive email.

### Tasks 75-80: Advanced Workflows
- **Note**: These define specific templates and integration logic to be loaded into n8n.

---

## 🔷 PHASE 4E: SMART FEATURES & DESKTOP (Tasks 81-90)
*Proactivity and System Integration.*

### Task 81: Smart Search Tools 🎞️
- **Steps**: YouTube/ArXiv fetchers (can be n8n or internal).

### Task 88: Desktop App & Permissions 🖥️🔐
- **Goal**: Native app experience + Security.
- **Steps**:
  - [ ] Electron/Tauri wrapper around React UI.
  - [ ] **System Permissions Module**:
    - Request "Full Disk Access" (macOS).
    - Request "Notification" permissions.
  - [ ] Tray Icon.
- **🧪 Verification**:
  - Build .app/.exe.
  - Launch. Verify OS prompts for permissions.
  - Verify access to user Documents folder.

### Tasks 82-87, 89-90
- Refinements of recommendations, tagging, and deployment.

---

## ✅ SUCCESS CRITERIA
Mind-Q is ready for v1.0 Release when:
1. API is stable and documented.
2. Web UI allows full management without CLI.
3. Chat provides accurate answers from local files.
4. n8n can successfully trigger Mind-Q actions.
5. Desktop App runs with necessary permissions on macOS.
