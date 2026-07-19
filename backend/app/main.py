from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import agent

app = FastAPI(title="AgentFS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agent.router)


@app.get("/health")
def health_check():
    """Check whether the server is alive and config loaded correctly."""
    return {
        "status": "AgentFS API is running",
        "working_directory": settings.agent_working_directory
    }