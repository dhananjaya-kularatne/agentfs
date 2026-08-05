import { useState, useEffect } from "react"

// Key used to store the client ID in the browser's localStorage.
const STORAGE_KEY = "agentfs_client_id"

// Generates a random client identifier. Not cryptographically significant — just needs to be unique per browser to scope sandbox and session data.
function generateClientId() {
  return crypto.randomUUID()
}

// Custom hook that provides a persistent client ID for this browser.
// Generated once on first visit and reused on every subsequent visit, so this browser's sandbox and session history stay consistent over time.
export function useClientId() {
  const [clientId, setClientId] = useState(null)

  useEffect(() => {
    let stored = localStorage.getItem(STORAGE_KEY)
    if (!stored) {
      stored = generateClientId()
      localStorage.setItem(STORAGE_KEY, stored)
    }
    setClientId(stored)
  }, [])

  return clientId
}