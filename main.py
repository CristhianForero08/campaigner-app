from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from campaigner_core.api.routes import router as api_router
from campaigner_core.orchestrator.registry import registry
from campaigner_core.config.settings import settings

app = FastAPI(
    title="Campaigner AI Platform",
    description="Enterprise Direct Marketing Orchestration",
    version="0.1.0"
)

# Wire up routes
app.include_router(api_router, prefix="/api/v1")

# Mount Frontend (Must be after API routes to avoid conflict if mounting root)
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")

@app.on_event("startup")
async def startup_event():
    print("Initializing Platform...")
    # Load Agents
    registry.load_agents_from_config()
    print(f"Loaded Agents: {list(registry.list_agents().keys())}")

@app.get("/health")
async def health_check():
    return {"status": "ok", "agents_loaded": len(registry.list_agents())}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
