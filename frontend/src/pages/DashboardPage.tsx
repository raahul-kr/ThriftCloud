import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { fetchDashboard } from "../api/client";
import { MetricCard } from "../components/MetricCard";
import { ProvidersPanel } from "../components/ProvidersPanel";
import { RecommendationsPanel } from "../components/RecommendationsPanel";
import { RoadmapPanel } from "../components/RoadmapPanel";
import { ScoreDial } from "../components/ScoreDial";
import { TrendChart } from "../components/TrendChart";
import { useAuthStore } from "../store/authStore";
import type { DashboardSummary } from "../types/dashboard";

function formatMoney(value: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0
  }).format(value);
}

export function DashboardPage() {
  const navigate = useNavigate();
  const token = useAuthStore((state) => state.token);
  const user = useAuthStore((state) => state.user);
  const clearSession = useAuthStore((state) => state.clearSession);

  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) {
      navigate("/");
      return;
    }

    fetchDashboard(token)
      .then((result) => {
        setSummary(result);
        setError(null);
      })
      .catch((dashboardError) => {
        setError(dashboardError instanceof Error ? dashboardError.message : "Unable to load dashboard");
      })
      .finally(() => setLoading(false));
  }, [navigate, token]);

  if (loading) {
    return <div className="flex min-h-screen items-center justify-center text-slate-600">Loading dashboard...</div>;
  }

  if (!summary) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-slate-50 px-6 text-center">
        <p className="text-lg font-medium text-slate-800">{error ?? "No dashboard data available."}</p>
        <button
          className="rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white"
          onClick={() => {
            clearSession();
            navigate("/");
          }}
        >
          Back to login
        </button>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-[linear-gradient(180deg,_#f8fafc_0%,_#ecfeff_55%,_#ffffff_100%)] px-6 py-8">
      <div className="mx-auto max-w-7xl">
        <header className="rounded-[2rem] border border-white/70 bg-white/75 p-6 shadow-float backdrop-blur lg:p-8">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.32em] text-emerald-700">Control Center</p>
              <h1 className="mt-3 text-4xl font-semibold text-slate-900">Welcome back, {summary.viewer_name}</h1>
              <p className="mt-3 max-w-3xl text-slate-600">
                This first milestone already tells a strong capstone story: authentic local stack, seeded cloud cost
                signals, and a narrative around measurable optimization.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <div className="rounded-2xl bg-slate-100 px-4 py-3 text-sm text-slate-700">
                {user?.email} · {user?.role}
              </div>
              <button
                className="rounded-2xl border border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
                onClick={() => {
                  clearSession();
                  navigate("/");
                }}
              >
                Sign out
              </button>
            </div>
          </div>
        </header>

        <section className="mt-8 grid gap-5 md:grid-cols-3">
          <MetricCard
            label="Total Spend"
            value={formatMoney(summary.total_cost)}
            hint="Seeded 90-day local billing dataset"
            accent="bg-emerald-100 text-emerald-700"
            icon={<span className="text-xl">$</span>}
          />
          <MetricCard
            label="Monthly Change"
            value={`${summary.monthly_change_percentage.toFixed(1)}%`}
            hint="Compared with the previous visible month"
            accent="bg-amber-100 text-amber-700"
            icon={<span className="text-xl">%</span>}
          />
          <MetricCard
            label="Live Recommendations"
            value={String(summary.recommendations.length)}
            hint="High-confidence optimization opportunities"
            accent="bg-cyan-100 text-cyan-700"
            icon={<span className="text-xl">!</span>}
          />
        </section>

        <section className="mt-8 grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
          <ScoreDial score={summary.finops_score} wastePercentage={summary.waste_percentage} />
          <RoadmapPanel />
        </section>

        <section className="mt-8 grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
          <TrendChart data={summary.trend} />
          <ProvidersPanel providers={summary.providers} />
        </section>

        <section className="mt-8">
          <RecommendationsPanel recommendations={summary.recommendations} />
        </section>
      </div>
    </main>
  );
}

