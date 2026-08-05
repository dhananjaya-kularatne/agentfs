const API_BASE_URL = "http://127.0.0.1:8000"

export async function runTask(goal, clientId) {
  const response = await fetch(`${API_BASE_URL}/api/agent/task`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Client-Id": clientId,
    },
    body: JSON.stringify({ goal }),
  })
  if (!response.ok) throw new Error("Failed to start task")
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
  if (!response.ok) throw new Error("Failed to confirm action")
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