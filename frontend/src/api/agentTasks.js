const API_BASE_URL = "http://127.0.0.1:8000"

export async function runTask(goal) {
  const response = await fetch(`${API_BASE_URL}/api/agent/task`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ goal }),
  })
  if (!response.ok) throw new Error("Failed to start task")
  return response.json()
}

export async function confirmAction(sessionId, approved) {
  const response = await fetch(`${API_BASE_URL}/api/agent/task/${sessionId}/confirm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ approved }),
  })
  if (!response.ok) throw new Error("Failed to confirm action")
  return response.json()
}

export async function listSessions() {
  const response = await fetch(`${API_BASE_URL}/api/agent/sessions`)
  if (!response.ok) throw new Error("Failed to fetch sessions")
  return response.json()
}

export async function getSessionDetail(sessionId) {
  const response = await fetch(`${API_BASE_URL}/api/agent/sessions/${sessionId}`)
  if (!response.ok) throw new Error("Failed to fetch session")
  return response.json()
}

export async function deleteSession(sessionId) {
  const response = await fetch(`${API_BASE_URL}/api/agent/sessions/${sessionId}`, {
    method: "DELETE",
  })
  if (!response.ok) throw new Error("Failed to delete session")
  return response.json()
}