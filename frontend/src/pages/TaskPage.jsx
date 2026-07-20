import { useState } from "react"
import { runTask, confirmAction } from "../api/agentTasks"
import StepCard from "../components/StepCard"

function TaskPage() {
  const [goal, setGoal] = useState("")
  const [steps, setSteps] = useState([])
  const [sessionId, setSessionId] = useState(null)
  const [status, setStatus] = useState(null)
  const [isRunning, setIsRunning] = useState(false)

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
    } catch (err) {
      setStatus("failed")
    } finally {
      setIsRunning(false)
    }
  }

  return (
    <div className="min-h-screen bg-black text-neutral-100 p-6">
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
  )
}

export default TaskPage