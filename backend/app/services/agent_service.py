import json
import uuid
from groq import Groq
from app.config import settings
from app.tools.tool_definitions import TOOL_DEFINITIONS
from app.tools.tool_registry import TOOL_REGISTRY, DESTRUCTIVE_TOOLS
from app.services.mongo_service import create_session, get_session, update_session

_client = Groq(api_key=settings.groq_api_key)

SYSTEM_PROMPT = (
    "You are a filesystem agent. You can explore, read, and modify files in a sandboxed "
    "working directory using the tools provided. Break the task into steps, "
    "use tools to gather the information you need, and give a final clear answer "
    "when you have enough information. Do not guess file contents you have not read. "
    "Destructive actions (write_file, move_file, delete_file) require human confirmation "
    "before they take effect."
)

MAX_ITERATIONS = 10


async def run_agent_task(goal: str) -> dict:
    """Start a new agent session and run the loop until it completes, pauses, or fails."""
    session_id = str(uuid.uuid4())
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": goal},
    ]

    await create_session(session_id, goal)
    return await _run_loop(session_id, messages, steps=[], seen_calls=set())


async def resume_agent_task(session_id: str, approved: bool) -> dict:
    """Resume a paused session after a human approves or rejects the pending action."""
    session = await get_session(session_id)
    if session is None:
        return {"status": "failed", "error": "Session not found."}
    if session["status"] != "pending_confirm":
        return {"status": "failed", "error": "Session is not awaiting confirmation."}

    messages = session["messages"]
    steps = session["steps"]
    seen_calls = {tuple(c) for c in session.get("seen_calls", [])}
    pending = session["pending_action"]

    if approved:
        tool_function = TOOL_REGISTRY[pending["tool"]]
        result = tool_function(**pending["input"])
    else:
        result = {"success": False, "error": {"type": "rejected_by_user", "message": "The user rejected this action."}}

    steps.append({
        "type": "confirmation_result",
        "tool": pending["tool"],
        "input": pending["input"],
        "approved": approved,
        "output": result,
    })

    messages.append({
        "role": "tool",
        "tool_call_id": pending["tool_call_id"],
        "content": json.dumps(result),
    })

    return await _run_loop(session_id, messages, steps, seen_calls)


async def _run_loop(session_id: str, messages: list, steps: list, seen_calls: set) -> dict:
    """Shared loop logic used by both starting and resuming a session."""
    for iteration in range(MAX_ITERATIONS):
        response = _client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
        )
        message = response.choices[0].message

        if not message.tool_calls:
            steps.append({"type": "final_answer", "content": message.content})
            await update_session(session_id, {
                "status": "completed",
                "final_answer": message.content,
                "steps": steps,
                "messages": messages + [{"role": "assistant", "content": message.content}],
                "total_tool_calls": len([s for s in steps if s["type"] in ("tool_call", "confirmation_result")]),
                "total_steps": len(steps),
            })
            return {"status": "completed", "final_answer": message.content, "pending_action": None, "steps": steps, "session_id": session_id, "error": None}

        assistant_message = {
            "role": "assistant",
            "content": message.content,
        }
        if message.tool_calls:
            assistant_message["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in message.tool_calls
            ]
        messages.append(assistant_message)

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            if tool_name in DESTRUCTIVE_TOOLS:
                pending_action = {
                    "tool": tool_name,
                    "input": tool_args,
                    "tool_call_id": tool_call.id,
                }
                steps.append({"type": "confirmation_required", "tool": tool_name, "input": tool_args})
                await update_session(session_id, {
                    "status": "pending_confirm",
                    "pending_action": pending_action,
                    "steps": steps,
                    "messages": messages,
                    "seen_calls": list(seen_calls),
                    "total_steps": len(steps),
                    "total_tool_calls": len([s for s in steps if s["type"] in ("tool_call", "confirmation_result")]),
                })
                return {"status": "pending_confirm", "final_answer": None, "pending_action": pending_action, "session_id": session_id, "steps": steps, "error": None}

            call_signature = (tool_name, json.dumps(tool_args, sort_keys=True))
            if call_signature in seen_calls:
                result = {"success": False, "error": {"type": "duplicate_call", "message": "You already called this exact tool with these exact arguments. Try a different approach."}}
            else:
                seen_calls.add(call_signature)
                tool_function = TOOL_REGISTRY.get(tool_name)
                result = tool_function(**tool_args) if tool_function else {"success": False, "error": {"type": "unknown_tool", "message": f"No such tool: {tool_name}"}}

            steps.append({"type": "tool_call", "tool": tool_name, "input": tool_args, "output": result})
            messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)})

    await update_session(session_id, {
        "status": "failed",
        "error": "Max iterations reached.",
        "steps": steps,
        "total_steps": len(steps),
        "total_tool_calls": len([s for s in steps if s["type"] in ("tool_call", "confirmation_result")]),
    })
    return {"status": "failed", "final_answer": None, "pending_action": None, "steps": steps, "error": "Max iterations reached.", "session_id": session_id}