const API_BASE_URL = "http://127.0.0.1:8000"

export async function getSandboxTree() {
  const response = await fetch(`${API_BASE_URL}/api/sandbox/tree`)
  if (!response.ok) throw new Error("Failed to fetch sandbox tree")
  return response.json()
}