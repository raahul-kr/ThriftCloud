import { useState } from "react";

import { updateRecommendation } from "../api/client";
import type { RecommendationAction, RecommendationItem } from "../types/dashboard";

interface RecommendationsPanelProps {
  recommendations: RecommendationItem[];
  token: string;
  isAdmin: boolean;
  onRecommendationUpdated: () => Promise<void>;
}

const severityAccent: Record<string, string> = {
  critical: "bg-rose-100 text-rose-700",
  high: "bg-amber-100 text-amber-700",
  medium: "bg-cyan-100 text-cyan-700",
  low: "bg-slate-100 text-slate-700"
};

const actionButtonClass =
  "rounded-2xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold uppercase tracking-[0.12em] text-slate-700 transition hover:border-slate-300 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50";

export function RecommendationsPanel({
  recommendations,
  token,
  isAdmin,
  onRecommendationUpdated
}: RecommendationsPanelProps) {
  const [pendingId, setPendingId] = useState<number | null>(null);
  const [ownerDrafts, setOwnerDrafts] = useState<Record<number, string>>({});
  const [feedback, setFeedback] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function runAction(recommendationId: number, action: RecommendationAction, assignedOwner?: string) {
    setPendingId(recommendationId);
    setError(null);
    setFeedback(null);

    try {
      const response = await updateRecommendation(token, recommendationId, action, assignedOwner);
      setFeedback(response.message);
      await onRecommendationUpdated();
    } catch (actionError) {
      setError(actionError instanceof Error ? actionError.message : "Unable to update recommendation");
    } finally {
      setPendingId(null);
    }
  }

  return (
    <section className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-float">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.24em] text-slate-500">Recommendations</p>
          <h3 className="mt-2 text-xl font-semibold text-slate-900">Highest-confidence savings moves</h3>
        </div>
      </div>

      {feedback ? <p className="mt-4 rounded-2xl bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{feedback}</p> : null}
      {error ? <p className="mt-4 rounded-2xl bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</p> : null}

      <div className="mt-5 space-y-4">
        {recommendations.map((item) => {
          const isPending = pendingId === item.id;
          const ownerDraft = ownerDrafts[item.id] ?? item.assigned_owner ?? "";

          return (
            <article key={item.recommendation_key} className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">{item.provider}</p>
                    <span
                      className={`rounded-full px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] ${
                        severityAccent[item.severity] ?? severityAccent.low
                      }`}
                    >
                      {item.severity}
                    </span>
                    <span className="rounded-full bg-white px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-slate-500">
                      {item.category.split("_").join(" ")}
                    </span>
                    {item.acknowledged_at ? (
                      <span className="rounded-full bg-emerald-100 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-emerald-700">
                        Acknowledged
                      </span>
                    ) : null}
                  </div>
                  <h4 className="mt-1 text-lg font-semibold text-slate-900">{item.title}</h4>
                  <p className="mt-2 text-sm text-slate-600">{item.description}</p>
                  <div className="mt-3 flex flex-wrap gap-2 text-xs text-slate-500">
                    <span className="rounded-full bg-white px-3 py-1">{item.resource_count} records in scope</span>
                    {item.service_name ? <span className="rounded-full bg-white px-3 py-1">{item.service_name}</span> : null}
                    {item.region ? <span className="rounded-full bg-white px-3 py-1">{item.region}</span> : null}
                    {item.assigned_owner ? (
                      <span className="rounded-full bg-white px-3 py-1">Owner: {item.assigned_owner}</span>
                    ) : null}
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-semibold text-emerald-700">${item.estimated_monthly_savings.toFixed(2)}/mo</p>
                  <p className="mt-1 text-xs text-slate-500">${item.estimated_annual_savings.toFixed(2)} annualized</p>
                  <p className="mt-1 text-xs uppercase tracking-[0.16em] text-slate-500">
                    Confidence {(item.confidence * 100).toFixed(0)}%
                  </p>
                </div>
              </div>

              <div className="mt-4 grid gap-4 lg:grid-cols-2">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Evidence</p>
                  <ul className="mt-2 space-y-2 text-sm text-slate-600">
                    {item.evidence.map((entry) => (
                      <li key={entry} className="rounded-2xl bg-white px-3 py-2">
                        {entry}
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Next steps</p>
                  <ul className="mt-2 space-y-2 text-sm text-slate-600">
                    {item.next_steps.map((step) => (
                      <li key={step} className="rounded-2xl bg-white px-3 py-2">
                        {step}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="mt-4 flex flex-wrap items-center gap-2 border-t border-slate-200 pt-4">
                <button
                  className={actionButtonClass}
                  disabled={isPending || Boolean(item.acknowledged_at)}
                  onClick={() => runAction(item.id, "acknowledge")}
                >
                  Acknowledge
                </button>
                <button
                  className={actionButtonClass}
                  disabled={isPending}
                  onClick={() => runAction(item.id, "resolve")}
                >
                  Resolve
                </button>
                <button
                  className={actionButtonClass}
                  disabled={isPending}
                  onClick={() => runAction(item.id, "dismiss")}
                >
                  Dismiss
                </button>
                {isAdmin ? (
                  <>
                    <input
                      className="min-w-[180px] rounded-2xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700"
                      placeholder="Assign owner"
                      value={ownerDraft}
                      onChange={(event) =>
                        setOwnerDrafts((current) => ({
                          ...current,
                          [item.id]: event.target.value
                        }))
                      }
                    />
                    <button
                      className={actionButtonClass}
                      disabled={isPending || !ownerDraft.trim()}
                      onClick={() => runAction(item.id, "assign_owner", ownerDraft.trim())}
                    >
                      Assign owner
                    </button>
                  </>
                ) : null}
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}
