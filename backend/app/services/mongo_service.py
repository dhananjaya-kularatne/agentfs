from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

_client = AsyncIOMotorClient(settings.mongodb_uri)
_db = _client[settings.mongodb_db_name]

sessions_collection = _db["sessions"]


async def create_session(session_id: str, goal: str) -> dict:
    """Create a new agent session record."""
    record = {
        "_id": session_id,
        "goal": goal,
        "status": "running",
        "working_directory": settings.agent_working_directory,
        "created_at": datetime.now(timezone.utc),
        "completed_at": None,
        "steps": [],
        "messages": [],
        "pending_action": None,
        "final_answer": None,
        "total_steps": 0,
        "total_tool_calls": 0,
        "error": None,
    }
    await sessions_collection.insert_one(record)
    return record


async def get_session(session_id: str) -> dict | None:
    """Fetch a session by ID."""
    return await sessions_collection.find_one({"_id": session_id})


async def update_session(session_id: str, updates: dict) -> None:
    """Update fields on an existing session."""
    await sessions_collection.update_one({"_id": session_id}, {"$set": updates})