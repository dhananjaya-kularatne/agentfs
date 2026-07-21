const TOOL_DESCRIPTIONS = {
  get_directory_tree: (input) => `Exploring the folder structure of "${input.path}"`,
  list_directory: (input) => `Listing files in "${input.path}"`,
  read_file: (input) => `Reading the file "${input.path}"`,
  search_files: (input) => `Searching for files matching "${input.pattern}"`,
  get_file_info: (input) => `Checking details of "${input.path}"`,
  write_file: (input) => `Create/overwrite the file "${input.path}"`,
  move_file: (input) => `Move "${input.src}" to "${input.dest}"`,
  delete_file: (input) => `Permanently delete "${input.path}"`,
  delete_directory: (input) => `Permanently delete the folder "${input.path}" and everything inside it`,
}

function describeTool(tool, input) {
  const describe = TOOL_DESCRIPTIONS[tool]
  return describe ? describe(input) : `${tool}(${JSON.stringify(input)})`
}

function describeResult(tool, output) {
  if (!output?.success) {
    return `Failed: ${output?.error?.message || "unknown error"}`
  }
  const data = output.data
  if (tool === "list_directory" && Array.isArray(data)) {
    return `Found ${data.length} item${data.length === 1 ? "" : "s"}: ${data.map((d) => d.name).join(", ")}`
  }
  if (tool === "read_file" && typeof data === "string") {
    const preview = data.length > 120 ? data.slice(0, 120) + "..." : data
    return `"${preview}"`
  }
  if (tool === "search_files" && Array.isArray(data)) {
    return data.length ? `Found: ${data.join(", ")}` : "No matching files found"
  }
  if (tool === "get_file_info" && data) {
    return `${data.type}, ${data.size_bytes} bytes`
  }
  if (tool === "get_directory_tree") {
    return "Retrieved folder structure"
  }
  if (tool === "delete_directory" && data) {
    return `Deleted ${data.files_removed} file${data.files_removed === 1 ? "" : "s"} and ${data.folders_removed} folder${data.folders_removed === 1 ? "" : "s"}`
  }
  return "Done"
}

function StepCard({ step, onApprove, onReject, isPending }) {
  const baseClasses = "rounded-lg border p-3 text-sm"

  if (step.type === "tool_call") {
    return (
      <div className={`${baseClasses} bg-neutral-900 border-neutral-700 text-neutral-200`}>
        <div className="text-blue-400">🔍 {describeTool(step.tool, step.input)}</div>
        <div className="text-neutral-500 mt-1 text-xs">
          → {describeResult(step.tool, step.output)}
        </div>
      </div>
    )
  }

  if (step.type === "confirmation_required") {
    return (
      <div className={`${baseClasses} bg-amber-950/30 border-amber-600 text-amber-100`}>
        <div className="font-semibold mb-1">⚠ Approval needed</div>
        <div className="text-amber-200">{describeTool(step.tool, step.input)}</div>
        {step.tool === "write_file" && (
          <div className="text-amber-300/70 text-xs mt-1">
            content: "{step.input.content}"
          </div>
        )}
        <div className="text-amber-400/60 text-xs mt-2">
          This action will modify the filesystem and cannot be undone automatically.
        </div>
        {isPending && (
          <div className="flex gap-2 mt-3">
            <button
              onClick={onApprove}
              className="px-3 py-1.5 bg-amber-600 hover:bg-amber-500 text-black rounded text-xs font-semibold"
            >
              Approve
            </button>
            <button
              onClick={onReject}
              className="px-3 py-1.5 bg-neutral-700 hover:bg-neutral-600 text-neutral-200 rounded text-xs font-semibold"
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
        {step.approved ? "✓ You approved this action" : "✗ You rejected this action"} — {describeTool(step.tool, step.input)}
      </div>
    )
  }

  if (step.type === "final_answer") {
    return (
      <div className="rounded-lg border p-3 bg-green-950/30 border-green-600 text-green-200 text-sm">
        ✓ {step.content}
      </div>
    )
  }

  return null
}

export default StepCard