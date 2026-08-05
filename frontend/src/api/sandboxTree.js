const API_BASE_URL = "http://127.0.0.1:8000"

export async function getSandboxTree(clientId) {
  const response = await fetch(`${API_BASE_URL}/api/sandbox/tree`, {
    headers: { "X-Client-Id": clientId },
  })
  if (!response.ok) throw new Error("Failed to fetch sandbox tree")
  return response.json()
}