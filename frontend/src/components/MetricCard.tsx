import type { ReactNode } from "react";

interface MetricCardProps {
  label: string;
  value: string;
  hint: string;
  accent: string;
  icon: ReactNode;
}

export function MetricCard({ label, value, hint, accent, icon }: MetricCardProps) {
  return (
    <article className="rounded-3xl border border-white/60 bg-white/75 p-5 shadow-float backdrop-blur">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.24em] text-slate-500">{label}</p>
          <p className="mt-3 text-3xl font-semibold text-slate-900">{value}</p>
          <p className="mt-2 text-sm text-slate-500">{hint}</p>
        </div>
        <div className={`flex h-12 w-12 items-center justify-center rounded-2xl ${accent}`}>
          {icon}
        </div>
      </div>
    </article>
  );
}

