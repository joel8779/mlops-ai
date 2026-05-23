const segments = [
  { label: "Semantic", value: 38, color: "bg-signal" },
  { label: "Skills", value: 24, color: "bg-accent" },
  { label: "Experience", value: 14, color: "bg-slate-700" },
  { label: "ATS", value: 11, color: "bg-emerald-600" }
];

export function RankingVisualization() {
  return (
    <div className="rounded-md border border-slate-200 bg-white p-4">
      <h2 className="text-sm font-semibold">AI ranking composition</h2>
      <div className="mt-4 flex h-3 overflow-hidden rounded-full bg-slate-100">
        {segments.map((segment) => (
          <div key={segment.label} className={segment.color} style={{ width: `${segment.value}%` }} />
        ))}
      </div>
      <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
        {segments.map((segment) => (
          <div key={segment.label} className="flex items-center justify-between">
            <span>{segment.label}</span>
            <span className="font-medium">{segment.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
