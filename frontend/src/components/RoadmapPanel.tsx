const roadmapItems = [
  "Phase 1: auth, demo data, dashboard shell",
  "Phase 2: rule engine, score API, provider adapters",
  "Phase 3: forecast, anomalies, RAG, copilot chat",
  "Phase 4: PDF reports, observability, demo polish"
];

export function RoadmapPanel() {
  return (
    <section className="rounded-[2rem] border border-emerald-200 bg-gradient-to-br from-emerald-50 to-cyan-50 p-6 shadow-float">
      <p className="text-sm font-medium uppercase tracking-[0.24em] text-emerald-700">30-Day Roadmap</p>
      <h3 className="mt-2 text-xl font-semibold text-slate-900">Built directly from your capstone plan</h3>
      <div className="mt-5 space-y-3">
        {roadmapItems.map((item) => (
          <div key={item} className="rounded-2xl bg-white/80 px-4 py-3 text-sm text-slate-700">
            {item}
          </div>
        ))}
      </div>
    </section>
  );
}

