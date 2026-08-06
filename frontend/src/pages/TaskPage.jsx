import { useState, useEffect } from "react"
import { runTask, confirmAction, listSessions, getSessionDetail, deleteSession } from "../api/agentTasks"
import { getSandboxTree } from "../api/sandboxTree"
import { useClientId } from "../hooks/useClientId"
import StepCard from "../components/StepCard"
import SandboxTree from "../components/SandboxTree"
import SessionsSidebar from "../components/SessionsSidebar"

// Example prompts shown to first-time visitors, giving a quick sense of what the agent can do without requiring them to think of a task themselves.
// Clicking one fills the input rather than auto-running it, so the visitor still deliberately triggers the action themselves.
const EXAMPLE_PROMPTS = [
  { label: "🔍 Explore", text: "List all the files in this directory" },
  { label: "📖 Read", text: "What's in test.txt?" },
  { label: "✍️ Create", text: "Create a file called notes.txt with the content 'Hello from AgentFS'" },
  { label: "🗑️ Delete", text: "Delete the reports folder" },
]

function TaskPage() {
  const clientId = useClientId()
  const [goal, setGoal] = useState("")
  const [steps, setSteps] = useState([])
  const [sessionId, setSessionId] = useState(null)
  const [status, setStatus] = useState(null)
  const [isRunning, setIsRunning] = useState(false)
  const [tree, setTree] = useState(null)
  const [sessions, setSessions] = useState([])

  useEffect(() => {
    if (!clientId) return
    refreshTree()
    refreshSessions()
  }, [clientId])

  async function refreshTree() {
    try {
      const result = await getSandboxTree(clientId)
      setTree(result.data)
    } catch (err) {
      console.error("Failed to load sandbox tree", err)
    }
  }

  async function refreshSessions() {
    try {
      const result = await listSessions(clientId)
      setSessions(result.sessions)
    } catch (err) {
      console.error("Failed to load sessions", err)
    }
  }

  async function handleRunTask() {
    if (!goal.trim() || !clientId) return
    setIsRunning(true)
    setSteps([])
    setStatus(null)
    try {
      const result = await runTask(goal, clientId)
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
    if (!sessionId || !clientId) return
    setIsRunning(true)
    try {
      const result = await confirmAction(sessionId, approved, clientId)
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
      const session = await getSessionDetail(id, clientId)
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
      await deleteSession(id, clientId)
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
    <div className="min-h-screen bg-neutral-950 text-neutral-100 flex flex-col md:flex-row">
      <SessionsSidebar
        sessions={sessions}
        activeSessionId={sessionId}
        onSelectSession={handleSelectSession}
        onDeleteSession={handleDeleteSession}
      />

      <div className="flex-1 p-6 md:p-8 relative overflow-hidden">
        {/* Subtle glow accent behind the header, purely decorative */}
        <div className="absolute -top-24 left-1/4 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-2xl">🤖</span>
            <h1 className="text-xl font-mono font-semibold tracking-tight">AgentFS</h1>
          </div>
          <p className="text-sm text-neutral-500 mb-6">
            An autonomous agent that explores, reads, and safely modifies files — with human approval required for anything destructive.
          </p>

          <div className="flex gap-2 mb-4">
            <input
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleRunTask()}
              placeholder="Describe a task for the agent..."
              disabled={isRunning}
              className="flex-1 bg-neutral-900 border border-neutral-800 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-blue-600/50 transition-colors"
            />
            <button
              onClick={handleRunTask}
              disabled={isRunning || !goal.trim()}
              className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-semibold disabled:opacity-40 disabled:hover:bg-blue-600 transition-colors"
            >
              {isRunning ? "Running..." : "Run"}
            </button>
          </div>

          {/* Example prompts — only shown before any task has run this session */}
          {steps.length === 0 && (
            <div className="mb-6">
              <p className="text-xs text-neutral-600 mb-2 font-mono">Try asking it to:</p>
              <div className="flex flex-wrap gap-2">
                {EXAMPLE_PROMPTS.map((example) => (
                  <button
                    key={example.text}
                    onClick={() => setGoal(example.text)}
                    disabled={isRunning}
                    className="text-xs bg-neutral-900 border border-neutral-800 rounded-full px-3 py-1.5 text-neutral-400 hover:text-neutral-100 hover:border-neutral-600 transition-colors disabled:opacity-40"
                  >
                    {example.label} — {example.text}
                  </button>
                ))}
              </div>
            </div>
          )}

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
      </div>

      <SandboxTree tree={tree} onRefresh={refreshTree} />
    </div>
  )
}

export default TaskPage