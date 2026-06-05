import type { SpendAnomalyResponse } from "../types/dashboard";

interface AnomalyPanelProps {
  anomalies: SpendAnomalyResponse;
}

const severityAccent: Record<string, string> = {
  high: "bg-rose-100 text-rose-700",
  medium: "bg-amber-100 text-amber-700",
  low: "bg-slate-100 text-slate-700"
};

export function AnomalyPanel({ anomalies }: AnomalyPanelProps) {
  return (
    <section className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-float">
      <div className="mb-5 flex items-center justify-between">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.24em] text-slate-500">Anomaly Detection</p>
          <h3 className="mt-2 text-xl font-semibold text-slate-900">Spend spikes by provider</h3>
        </div>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-slate-600">
          {anomalies.scanned_points} providers scanned
        </span>
      </div>

      {anomalies.items.length === 0 ? (
        <p className="rounded-2xl bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
          No provider-level spend spikes detected in the latest billing window.
        </p>
      ) : (
        <div className="space-y-3">
          {anomalies.items.map((item) => (
            <article key={`${item.provider}-${item.label}`} className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex flex-wrap items-center gap-2">
                  <p className="text-sm font-semibold text-slate-900">{item.provider}</p>
                  <span className="rounded-full bg-white px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-slate-500">
                    {item.label}
                  </span>
                  <span
                    className={`rounded-full px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] ${
                      severityAccent[item.severity] ?? severityAccent.low
                    }`}
                  >
                    {item.severity}
                  </span>
                </div>
                <p className="text-sm font-semibold text-rose-700">+{item.deviation_percentage.toFixed(1)}%</p>
              </div>
              <p className="mt-2 text-sm text-slate-600">{item.summary}</p>
              <p className="mt-2 text-xs text-slate-500">
                Baseline ${item.baseline_cost.toFixed(2)} to observed ${item.observed_cost.toFixed(2)}
              </p>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
