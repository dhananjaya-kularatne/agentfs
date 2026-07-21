function SessionsSidebar({ sessions, activeSessionId, onSelectSession, onDeleteSession }) {
  const statusColor = {
    completed: "text-green-400",
    pending_confirm: "text-amber-400",
    failed: "text-red-400",
    running: "text-blue-400",
  }

  return (
    <div className="w-full md:w-56 border-r border-neutral-800 p-4">
      <h2 className="text-sm font-mono text-neutral-400 mb-3">Sessions</h2>
      <div className="flex flex-col gap-1">
        {sessions.map((s) => (
          <div
            key={s._id}
            className={`group flex items-start justify-between text-left text-xs px-2 py-2 rounded ${
              s._id === activeSessionId ? "bg-neutral-800" : "hover:bg-neutral-900"
            }`}
          >
            <button onClick={() => onSelectSession(s._id)} className="flex-1 text-left truncate">
              <div className={statusColor[s.status] || "text-neutral-400"}>● {s.status}</div>
              <div className="text-neutral-300 truncate">{s.goal}</div>
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation()
                onDeleteSession(s._id)
              }}
              className="opacity-0 group-hover:opacity-100 text-neutral-600 hover:text-red-400 ml-2 text-sm"
              title="Delete session"
            >
              ✕
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}

export default SessionsSidebar