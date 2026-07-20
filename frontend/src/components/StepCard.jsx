function StepCard({ step, onApprove, onReject, isPending }) {
  const baseClasses = "rounded-lg border p-3 font-mono text-sm"

  if (step.type === "tool_call") {
    return (
      <div className={`${baseClasses} bg-neutral-900 border-neutral-700 text-neutral-200`}>
        <div className="text-blue-400">{step.tool}({JSON.stringify(step.input)})</div>
        <div className="text-neutral-400 mt-1">
          {step.output?.success
            ? `→ ${JSON.stringify(step.output.data).slice(0, 200)}`
            : `→ error: ${step.output?.error?.message}`}
        </div>
      </div>
    )
  }

  if (step.type === "confirmation_required") {
    return (
      <div className={`${baseClasses} bg-amber-950/30 border-amber-600 text-amber-200`}>
        <div>⚠ {step.tool}({JSON.stringify(step.input)}) requires approval</div>
        {isPending && (
          <div className="flex gap-2 mt-2 font-sans">
            <button
              onClick={onApprove}
              className="px-3 py-1 bg-amber-600 text-black rounded text-xs font-semibold"
            >
              Approve
            </button>
            <button
              onClick={onReject}
              className="px-3 py-1 bg-neutral-700 text-neutral-200 rounded text-xs font-semibold"
            >
              Reject
            </button>
          </div>
        )}
      </div>
    )
  }

  if (step.type === "confirmation_result") {
    return (
      <div className={`${baseClasses} bg-neutral-900 border-neutral-700 text-neutral-400`}>
        {step.approved ? "✓ Approved" : "✗ Rejected"} — {step.tool}
      </div>
    )
  }

  if (step.type === "final_answer") {
    return (
      <div className="rounded-lg border p-3 bg-green-950/30 border-green-600 text-green-200 font-sans text-sm">
        ✓ {step.content}
      </div>
    )
  }

  return null
}

export default StepCard