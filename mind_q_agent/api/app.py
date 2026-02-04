from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mind_q_agent.api.settings import settings
from mind_q_agent.api.routers import documents, search, graph, realtime, preferences, concepts, system

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.API_TITLE,
        version=settings.API_VERSION,
        description="Mind-Q Agent API Layer"
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(documents.router, prefix=settings.API_prefix)
    app.include_router(search.router, prefix=settings.API_prefix)
    app.include_router(graph.router, prefix=settings.API_prefix)
    app.include_router(realtime.router, prefix=settings.API_prefix)
    app.include_router(preferences.router, prefix=settings.API_prefix)
    app.include_router(concepts.router, prefix=settings.API_prefix)
    app.include_router(system.router, prefix=settings.API_prefix)

    @app.get("/health")
    async def health_check():
        return {"status": "ok", "version": settings.API_VERSION}

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("mind_q_agent.api.app:app", host="0.0.0.0", port=8000, reload=True)
