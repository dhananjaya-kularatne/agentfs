# AgentFS

An autonomous filesystem agent that explores, reads, and modifies files in a sandboxed working directory using natural-language instructions. Every destructive action (writing, moving, or deleting a file) pauses for explicit human approval before it takes effect.

## Overview

AgentFS demonstrates a core pattern in agentic AI systems: giving a language model the ability to take real, consequential actions, while keeping a human explicitly in the loop for anything irreversible. The agent works through a task one tool call at a time, and every step — each tool call, its result, and every confirmation decision — is recorded and shown as a readable trace rather than collapsed into a single opaque answer.

The project's primary focus is safety architecture rather than agent capability for its own sake. Path traversal protection, a strictly bounded sandbox, and a pause-for-confirmation gate on destructive operations are treated as first-class requirements, not afterthoughts, and are backed by an automated security test suite.

## Architecture

```
User (browser)
      |
      v
React frontend (Vite + Tailwind)
      |  task / confirm
      v
FastAPI backend
      |
      +-- Groq LLM           reasons about the task, requests tool calls (model set by GROQ_MODEL)
      +-- Tool registry      read-only + destructive filesystem tools
      +-- Path/ID validator  blocks traversal, absolute paths, null bytes; checks client IDs
      +-- Rate limiter       per-client cap on agent task calls
      +-- MongoDB            persists full session history, per client
      +-- Per-client sandbox isolated working directory per browser
```

**Task flow:** a natural-language goal is sent to the LLM along with a list of available tools. The LLM requests tools one at a time — read-only tools (listing, reading, searching files) execute immediately; destructive tools (write, move, delete) are intercepted before execution, and the session pauses in a `pending_confirm` state. The pending action, described in plain language, is shown to the user with approve/reject controls. Only on approval does the tool actually run. This repeats until the LLM has enough information to produce a final answer, or the iteration limit (10 tool-calling rounds) is reached.

## Tech stack

| Layer | Technology | Notes |
|---|---|---|
| Frontend | React, Vite, Tailwind CSS | |
| Backend | FastAPI | Async Python web framework |
| LLM | Groq API (model set by `GROQ_MODEL`, default `openai/gpt-oss-120b`) | Direct tool-calling, no agent framework |
| Structured storage | MongoDB (Motor, async driver) | Full session and step history |
| Testing | pytest | 63 tests covering path safety, client-ID safety, resource limits, and all tools |

No agent framework (e.g. LangChain) is used. The tool-calling loop, path validation, and confirmation gate are implemented directly against Groq's native tool-calling API, so every stage of the reasoning loop is visible and independently testable rather than hidden behind a framework abstraction.

## Features

- **Autonomous multi-step reasoning.** The agent breaks a task into steps, calling tools as needed and reading their results before deciding what to do next, rather than following a fixed script.
- **Human-in-the-loop safety gate.** Destructive actions (`write_file`, `move_file`, `delete_file`, `delete_directory`) cannot execute without explicit user approval. This is enforced in the tool-calling loop itself, not left to the model's judgment.
- **Sandboxed filesystem access.** Every path is validated against a strict working-directory boundary before any operation touches disk. Traversal attempts (`../`), absolute paths outside the sandbox, and null-byte injection are all explicitly blocked and covered by tests.
- **Stuck-loop detection.** If the agent requests the exact same tool call with the exact same arguments more than once, the duplicate is blocked and the agent is nudged to try a different approach, preventing infinite retry loops.
- **Step-by-step trace.** Every tool call, its result, each confirmation decision, and the final answer are recorded as an ordered trace and rendered in the UI as human-readable descriptions rather than raw JSON. The trace is returned in batches — each time the agent pauses for approval, and when it finishes — not streamed token by token.
- **Full session persistence.** Every task's complete history, including every tool call and confirmation decision, is saved to MongoDB and can be revisited later.
- **Per-client isolation.** Each browser is assigned a private identifier on first visit, used to scope both the sandbox filesystem and the session history. Two visitors to the same deployment never see or affect each other's files or task history.
- **Responsive layout.** The document/file tree sidebar collapses into a toggleable overlay on narrow viewports.

## Security design

Path safety is the single most important property of this system, since the agent is granted the ability to modify and delete files. It is implemented as one function, `validate_path`, called by every filesystem tool before any operation touches disk:

- Relative paths are resolved against the sandbox root and checked with `Path.is_relative_to()` — any path that resolves outside the sandbox, however constructed, is rejected.
- Absolute paths pointing outside the sandbox are rejected the same way, since resolution happens regardless of how the input path is written.
- Null bytes in a path are explicitly rejected. This check was added after a dedicated security test revealed that Windows does not reject null-byte paths at the OS layer the way some other platforms do — an assumption that initially seemed safe but was found to be incorrect through testing, not by inspection.
- URL-encoded traversal sequences (`%2e%2e`) are treated as literal, harmless filenames rather than decoded, since paths reach this function as plain strings rather than raw HTTP path segments; this is documented and tested explicitly rather than left ambiguous.

This logic is covered by dedicated tests in `test_path_validator.py` and `test_filesystem_tools.py`, exercising both the happy path and every attack category above.

The sandbox *root* is as much attacker-controlled input as any tool path: it is built from the `X-Client-Id` header, joined to the base sandbox directory as a folder name. `validate_client_id` (in `path_validator.py`) is applied before that join — the ID must be 8–128 characters of `[A-Za-z0-9_-]`, with no path separators, `..`, or null bytes — and `get_client_working_directory` then re-resolves the result and asserts it is strictly inside the base. Without this, a header like `../../../..` or `C:/Windows/Temp` would relocate the sandbox root itself and every path check downstream would pass relative to an attacker-chosen directory. Covered by `test_client_id_validator.py`.

### Resource limits

The agent's tool calls are shaped by task text and by file contents it reads, so every tool that could be driven into unbounded work has an explicit ceiling (`app/tools/limits.py`): 1 MiB per file read or write, 1000 search results, directory-tree depth clamped to 8 and capped at 5000 visited nodes. Responses that hit a cap are flagged with `"truncated": true`. The unauthenticated agent endpoints are additionally rate-limited per client (default 20 calls / 60 s) so an open endpoint cannot drain the deployment's LLM quota.

## Setup

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
cp .env.example .env
```

`.env` requires:

```
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=agentfs
AGENT_WORKING_DIRECTORY=./sandbox
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
RATE_LIMIT_MAX_TASKS=20
RATE_LIMIT_WINDOW_SECONDS=60
```

Only `GROQ_API_KEY` is mandatory. `GROQ_MODEL` must be a Groq model your key can access that supports tool calling (list them with `curl -H "Authorization: Bearer $GROQ_API_KEY" https://api.groq.com/openai/v1/models`); `ALLOWED_ORIGINS` (comma-separated) and the two `RATE_LIMIT_*` values have sensible defaults and can be omitted for local development.

Run the server:

```bash
uvicorn app.main:app --reload
```

Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173` and expects the backend to be available at `http://127.0.0.1:8000`.

### Tests

```bash
cd backend
pytest -v
```

63 tests cover path validation (traversal, absolute paths, null bytes, encoded sequences), client-ID validation (traversal, absolute, empty), resource limits, the rate limiter, error-message disclosure, and all read-only and destructive tools, using an isolated temporary directory per test so no test run touches the real sandbox.

## API reference

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/agent/task` | Start a new agent task |
| POST | `/api/agent/task/{session_id}/confirm` | Approve or reject a pending destructive action |
| GET | `/api/agent/sessions` | List sessions belonging to the requesting client |
| GET | `/api/agent/sessions/{session_id}` | Get full detail for one session |
| DELETE | `/api/agent/sessions/{session_id}` | Delete a session |
| GET | `/api/sandbox/tree` | Get the requesting client's sandbox directory tree |

All endpoints require an `X-Client-Id` header, used to scope sandbox and session data to the requesting browser. It is validated to a safe path-segment shape before use; a malformed value returns `400`. The agent endpoints also return `429` (with `Retry-After`) when a client exceeds its rate-limit budget.

## Known limitations

- **The agent operates on a sandboxed demo directory, not real files.** This is a deliberate design choice: granting an autonomous agent unrestricted access to a real filesystem, especially in a publicly deployed environment, would remove the safety boundary this project is built around. The sandbox is seeded with a few sample files on first visit per client.
- **The iteration cap (10 tool-calling rounds) can cause a task to fail without a clear answer** if a goal genuinely requires more steps than that to resolve. This is a deliberate safeguard against runaway loops, at the cost of occasionally cutting off a legitimately long task.
- **Client identity is a browser-generated identifier stored in local storage, not an authenticated account.** Clearing browser storage or switching browsers creates a new, unrelated identity with a fresh sandbox. The identifier's *shape* is validated so it cannot be used to escape the sandbox or reach another client's data by traversal, but it is still an unauthenticated bearer value: anyone who obtains another client's ID can act as that client. This is sufficient for isolating casual visitors from each other but is not a substitute for real authentication.

## Project structure

```
agentfs/
├── backend/
│   ├── app/
│   │   ├── models/       # Pydantic request/response models
│   │   ├── routers/      # FastAPI route handlers (agent, sandbox)
│   │   ├── services/     # Agent loop, MongoDB persistence, rate limiter
│   │   └── tools/        # Path/client-ID validation, filesystem tools, resource limits, tool registry
│   └── tests/
└── frontend/
    └── src/
        ├── api/           # Backend request wrappers
        ├── hooks/         # Client ID persistence
        ├── components/    # StepCard, SandboxTree, SessionsSidebar
        └── pages/         # TaskPage
```