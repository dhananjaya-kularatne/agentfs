// Backend origin. Set VITE_API_BASE_URL at build time for deployed environments;
// falls back to the local dev server.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"

// Build an Error from a failed response, keeping the HTTP status and — for a 429
// from the rate limiter — the Retry-After hint so callers can tell the user how
// long to wait.
async function requestError(response, fallbackMessage) {
  let message = fallbackMessage
  try {
    const body = await response.json()
    if (body?.detail) message = body.detail
  } catch {
    // no JSON body on the response; keep the fallback message
  }
  const error = new Error(message)
  error.status = response.status
  const retryAfter = response.headers.get("Retry-After")
  if (retryAfter) error.retryAfter = Number(retryAfter)
  return error
}

export async function runTask(goal, clientId) {
  const response = await fetch(`${API_BASE_URL}/api/agent/task`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Client-Id": clientId,
    },
    body: JSON.stringify({ goal }),
  })
  if (!response.ok) throw await requestError(response, "Failed to start task")
  return response.json()
}

export async function confirmAction(sessionId, approved, clientId) {
  const response = await fetch(`${API_BASE_URL}/api/agent/task/${sessionId}/confirm`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Client-Id": clientId,
    },
    body: JSON.stringify({ approved }),
  })
  if (!response.ok) throw await requestError(response, "Failed to confirm action")
  return response.json()
}

export async function listSessions(clientId) {
  const response = await fetch(`${API_BASE_URL}/api/agent/sessions`, {
    headers: { "X-Client-Id": clientId },
  })
  if (!response.ok) throw new Error("Failed to fetch sessions")
  return response.json()
}

export async function getSessionDetail(sessionId, clientId) {
  const response = await fetch(`${API_BASE_URL}/api/agent/sessions/${sessionId}`, {
    headers: { "X-Client-Id": clientId },
  })
  if (!response.ok) throw new Error("Failed to fetch session")
  return response.json()
}

export async function deleteSession(sessionId, clientId) {
  const response = await fetch(`${API_BASE_URL}/api/agent/sessions/${sessionId}`, {
    method: "DELETE",
    headers: { "X-Client-Id": clientId },
  })
  if (!response.ok) throw new Error("Failed to delete session")
  return response.json()
}