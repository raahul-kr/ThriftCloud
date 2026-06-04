import type { RecommendationItem } from "../types/dashboard";

interface RecommendationsPanelProps {
  recommendations: RecommendationItem[];
}

export function RecommendationsPanel({ recommendations }: RecommendationsPanelProps) {
  return (
    <section className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-float">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.24em] text-slate-500">Recommendations</p>
          <h3 className="mt-2 text-xl font-semibold text-slate-900">Highest-confidence savings moves</h3>
        </div>
      </div>

      <div className="mt-5 space-y-4">
        {recommendations.map((item) => (
          <article key={`${item.provider}-${item.title}`} className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">{item.provider}</p>
                <h4 className="mt-1 text-lg font-semibold text-slate-900">{item.title}</h4>
                <p className="mt-2 text-sm text-slate-600">{item.description}</p>
              </div>
              <div className="text-right">
                <p className="text-sm font-semibold text-emerald-700">${item.estimated_savings.toFixed(2)}</p>
                <p className="mt-1 text-xs uppercase tracking-[0.16em] text-slate-500">
                  Confidence {(item.confidence * 100).toFixed(0)}%
                </p>
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

