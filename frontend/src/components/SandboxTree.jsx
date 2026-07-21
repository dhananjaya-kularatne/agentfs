function TreeNode({ node, depth = 0 }) {
  const isDirectory = node.type === "directory"
  return (
    <div style={{ paddingLeft: `${depth * 12}px` }}>
      <div className="text-sm font-mono text-neutral-300 py-0.5">
        {isDirectory ? "📁" : "📄"} {node.name}
      </div>
      {isDirectory && node.children?.map((child, i) => (
        <TreeNode key={i} node={child} depth={depth + 1} />
      ))}
    </div>
  )
}

function SandboxTree({ tree, onRefresh }) {
  return (
    <div className="w-64 border-l border-neutral-800 p-4">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-sm font-mono text-neutral-400">sandbox/</h2>
        <button
          onClick={onRefresh}
          className="text-xs text-neutral-500 hover:text-neutral-300"
        >
          ↻ refresh
        </button>
      </div>
      {tree ? <TreeNode node={tree} /> : <p className="text-xs text-neutral-600">Loading...</p>}
    </div>
  )
}

export default SandboxTree