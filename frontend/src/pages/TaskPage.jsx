import { useState, useEffect } from "react"
import { runTask, confirmAction, listSessions, getSessionDetail, deleteSession } from "../api/agentTasks"
import { getSandboxTree } from "../api/sandboxTree"
import StepCard from "../components/StepCard"
import SandboxTree from "../components/SandboxTree"
import SessionsSidebar from "../components/SessionsSidebar"

function TaskPage() {
  const [goal, setGoal] = useState("")
  const [steps, setSteps] = useState([])
  const [sessionId, setSessionId] = useState(null)
  const [status, setStatus] = useState(null)
  const [isRunning, setIsRunning] = useState(false)
  const [tree, setTree] = useState(null)
  const [sessions, setSessions] = useState([])

  useEffect(() => {
    refreshTree()
    refreshSessions()
  }, [])

  async function refreshTree() {
    try {
      const result = await getSandboxTree()
      setTree(result.data)
    } catch (err) {
      console.error("Failed to load sandbox tree", err)
    }
  }

  async function refreshSessions() {
    try {
      const result = await listSessions()
      setSessions(result.sessions)
    } catch (err) {
      console.error("Failed to load sessions", err)
    }
  }

  async function handleRunTask() {
    if (!goal.trim()) return
    setIsRunning(true)
    setSteps([])
    setStatus(null)
    try {
      const result = await runTask(goal)
      setSessionId(result.session_id)
      setSteps(result.steps)
      setStatus(result.status)
      if (result.status === "completed") {
        await refreshTree()
        await refreshSessions()
      }
    } catch (err) {
      setStatus("failed")
    } finally {
      setIsRunning(false)
    }
  }

  async function handleConfirm(approved) {
    if (!sessionId) return
    setIsRunning(true)
    try {
      const result = await confirmAction(sessionId, approved)
      setSteps(result.steps)
      setStatus(result.status)
      if (result.status === "completed") {
        await refreshTree()
        await refreshSessions()
      }
    } catch (err) {
      setStatus("failed")
    } finally {
      setIsRunning(false)
    }
  }

  async function handleSelectSession(id) {
    try {
      const session = await getSessionDetail(id)
      setSessionId(session._id)
      setSteps(session.steps)
      setStatus(session.status)
      setGoal(session.goal)
    } catch (err) {
      console.error("Failed to load session", err)
    }
  }

  async function handleDeleteSession(id) {
  try {
    await deleteSession(id)
    if (id === sessionId) {
      setSessionId(null)
      setSteps([])
      setStatus(null)
      setGoal("")
    }
    await refreshSessions()
  } catch (err) {
    console.error("Failed to delete session", err)
  }
}

  return (
    <div className="min-h-screen bg-black text-neutral-100 flex">
      <SessionsSidebar
        sessions={sessions}
        activeSessionId={sessionId}
        onSelectSession={handleSelectSession}
        onDeleteSession={handleDeleteSession}
      />

      <div className="flex-1 p-6">
        <h1 className="text-xl font-mono mb-4">AgentFS</h1>

        <div className="flex gap-2 mb-6">
          <input
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            placeholder="Describe a task for the agent..."
            disabled={isRunning}
            className="flex-1 bg-neutral-900 border border-neutral-700 rounded px-3 py-2 text-sm"
          />
          <button
            onClick={handleRunTask}
            disabled={isRunning}
            className="px-4 py-2 bg-blue-600 rounded text-sm font-semibold disabled:opacity-50"
          >
            {isRunning ? "Running..." : "Run"}
          </button>
        </div>

        <div className="flex flex-col gap-2 max-w-2xl">
          {steps.map((step, i) => (
            <StepCard
              key={i}
              step={step}
              isPending={status === "pending_confirm" && i === steps.length - 1}
              onApprove={() => handleConfirm(true)}
              onReject={() => handleConfirm(false)}
            />
          ))}
        </div>
      </div>

      <SandboxTree tree={tree} onRefresh={refreshTree} />
    </div>
  )
}

export default TaskPage