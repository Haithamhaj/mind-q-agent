# Frontend Integration Guide

This guide explains how to connect the React Frontend (built externally, e.g., via Google AI Studio) with the Mind-Q Backend.

## Option 1: Development Mode (Recommended for Editing)
Run both servers side-by-side. This allows "Hot Reloading" (changes appear instantly).

1. **Place Code**: Put the React code in `mind-q-agent/frontend/`.
2. **Configure Proxy**: Ensure `frontend/vite.config.ts` has the proxy setup (see below).
3. **Run Backend**: `uvicorn mind_q_agent.api.app:app --port 8000`
4. **Run Frontend**: `cd frontend && npm run dev`
5. **Access**: Go to `http://localhost:5173`. The UI will talk to port 8000 automatically.

### vite.config.ts Proxy Setup
```typescript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
```

---

## Option 2: Production Mode (Single App)
Merge the UI into the Python application. This is how the final "Mind-Q App" will work.

1. **Build UI**: Run `npm run build` in the frontend folder. This creates a `dist/` folder.
2. **Mount in FastAPI**: We update `app.py` to serve these files.

```python
from fastapi.staticfiles import StaticFiles

# Mount static files (HTML/JS/CSS)
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")
```

3. **Run**: User runs `python mind_q_agent/api/app.py` and visits `http://localhost:8000`. They see the UI immediately.

---

## 🚀 Recommended Workflow
1. Create a `frontend` folder in your project now.
2. Copy the code you get from Google AI Studio into that folder.
3. We configure **Option 1** first to test it.
4. Once satisfied, we implement **Option 2** for the final release.
