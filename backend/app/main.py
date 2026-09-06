from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.routers import agent, sandbox
from app.tools.path_validator import ClientIdValidationError

app = FastAPI(title="AgentFS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-Client-Id"],
)


@app.exception_handler(ClientIdValidationError)
async def client_id_validation_error_handler(request: Request, exc: ClientIdValidationError):
    """A malformed X-Client-Id is a bad request, not a server error."""
    return JSONResponse(status_code=400, content={"detail": str(exc)})


app.include_router(agent.router)
app.include_router(sandbox.router)

@app.get("/health")
def health_check():
    """Check whether the server is alive and config loaded correctly."""
    return {
        "status": "AgentFS API is running",
        "base_sandbox_directory": settings.agent_working_directory
    }