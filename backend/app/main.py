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
    # Retry-After is not a CORS-safelisted response header, so the browser hides
    # it from JS unless it is explicitly exposed. The frontend reads it to tell
    # the user how long to wait after a 429.
    expose_headers=["Retry-After"],
)


@app.exception_handler(ClientIdValidationError)
async def client_id_validation_error_handler(_request: Request, exc: ClientIdValidationError):
    """A malformed X-Client-Id is a bad request, not a server error."""
    return JSONResponse(status_code=400, content={"detail": str(exc)})


app.include_router(agent.router)
app.include_router(sandbox.router)

@app.get("/health")
def health_check():
    """Liveness check. Deliberately exposes no configuration or path details."""
    return {"status": "AgentFS API is running"}