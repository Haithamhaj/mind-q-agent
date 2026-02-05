# Mind-Q Phase 5: The Active Observer (SRS & Roadmap)

## 1. Executive Summary
**Goal**: Transform Mind-Q from a passive repository into an **Active Personal Companion** that automatically learns from the user's digital footprint.
**Core Philosophy**: "Zero-Click Ingestion". The system should know what the user is working on, reading, or watching without manual input, while maintaining **100% Local Privacy**.

---

## 2. System Architecture (The "Senses")

The "Observer" module consists of three main sensory inputs feeding into the existing Mind-Q Brain.

### 2.1. The Browser Eye (Chrome/Edge Extension)
-   **Role**: Captures web activity (Articles, Papers, Videos).
-   **Mechanism**: A lightweight extension that extracts main content and metadata.
-   **Triggers**:
    -   *Time-based*: User stays on a page > 30 seconds.
    -   *Interaction-based*: User copies text or bookmarks a page.
-   **Privacy**: Whitelist/Blacklist domains (e.g., ignore banking sites).

### 2.2. The Desktop Ear (Screen & App Watcher)
-   **Role**: Understands context from active applications (VS Code, Word, Slack).
-   **Mechanism**: Uses OS Accessibility APIs (Mac/Windows) to read window titles and active text selection.
-   **OCR Fallback**: If text cannot be selected, take a low-res screenshot and run local OCR (Tesseract).

### 2.3. The Event Loop (Processing Pipeline)
-   **Role**: Queues incoming raw signals and decides what to keep.
-   **The "Filter"**: A lightweight LLM (Flash Model) checks: "Is this useful information?"
-   **The "Linker"**: Connects new info to the existing Knowledge Graph (kuzu).

---

## 3. Functional Requirements

### 3.1. Web Observation
-   **REQ-5.1.1**: Detect URL changes and classify page type (Article, Video, Social, Other).
-   **REQ-5.1.2**: Extract "Main Content" from clutter (Reader Mode logic).
-   **REQ-5.1.3**: For **YouTube**, extract the transcript (Closed Captions) automatically.
-   **REQ-5.1.4**: Capture "Search Queries" from Google/Bing to understand intent.

### 3.2. Desktop Observation
-   **REQ-5.2.1**: Monitor active window focus time.
-   **REQ-5.2.2**: Capture Clipboard events (Copy/Cut) as high-priority signals.
-   **REQ-5.2.3**: Application-specific adapters (VS Code Plugin, Obsidian Plugin).

### 3.3. Memory & Synthesis
-   **REQ-5.3.1**: **Short-term Memory (Daily Context)**: "What did I do today?" summary.
-   **REQ-5.3.2**: **Long-term Consolidation**: Move repeated/important topics to permanent Graph storage.
-   **REQ-5.3.3**: **Contextual Suggestion**: If user searches for X, show related stored notes about X.

---

## 4. Non-Functional Requirements (Constraints)
-   **Privacy First**: No data leaves the device. All OCR and LLM filtering happens locally (Ollama/LlamaCpp).
-   **Performance**: Background process must use < 5% CPU.
-   **Storage**: Automatic pruning of useless data (TTL policies).

---

## 5. Implementation Roadmap (Tasks)

This roadmap is designed to be executed sequentially in a new conversation.

### Phase 5A: The Browser Extension (The Eye)
- [ ] **Task 71: Extension Skeleton**: Create a basic Chrome Extension manifest and popup.
- [ ] **Task 72: Content Script & Communication**: Establish WebSocket connection between Extension and Mind-Q API.
- [ ] **Task 73: Page Content Extractor**: Implement `Readability.js` to strip ads/nav and get pure text.
- [ ] **Task 74: YouTube Transcript Grabber**: Logic to fetch XML captions from YouTube videos.
- [ ] **Task 75: Search Query Logger**: Detect google search URLs and log the `q=` parameter.

### Phase 5B: The Desktop Watcher (The Ear)
- [ ] **Task 76: OS Window Monitor**: Python script (pyobjc/pywin32) to track active window titles.
- [ ] **Task 77: Clipboard Listener**: Catch copy events and store text > 50 chars.
- [ ] **Task 78: Privacy Filters**: UI to manage Blocked Apps/Websites.

### Phase 5C: The Intelligent Filter (The Brain)
- [ ] **Task 79: Ingestion Queue API**: New Endpoint `/api/v1/observer/ingest` to receive signals.
- [ ] **Task 80: The "Judge" Agent**: A specialized Prompt for Llama3-8b to classify inputs (Keep/Discard).
- [ ] **Task 81: Automatic Tagging**: Generate tags for incoming content automatically.

### Phase 5D: User Experience (The Feedback)
- [ ] **Task 82: "Daily Timeline" UI**: A new Dashboard view showing "Your Day in Mind-Q".
- [ ] **Task 83: Context Sidebar**: A floating widget showing "Related to what you are looking at now".

---

## 6. Definitions & Tech Stack
-   **Extension**: TypeScript, Vite, Chrome API.
-   **Desktop**: Python (watchdog, pyobjc).
-   **Communication**: WebSockets (Real-time).
