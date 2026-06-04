import type { ProviderSpend } from "../types/dashboard";

interface ProvidersPanelProps {
  providers: ProviderSpend[];
}

export function ProvidersPanel({ providers }: ProvidersPanelProps) {
  const total = providers.reduce((sum, provider) => sum + provider.total_cost, 0);

  return (
    <section className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-float">
      <p className="text-sm font-medium uppercase tracking-[0.24em] text-slate-500">Provider Breakdown</p>
      <div className="mt-5 space-y-5">
        {providers.map((provider) => {
          const ratio = total ? (provider.total_cost / total) * 100 : 0;
          return (
            <div key={provider.provider}>
              <div className="mb-2 flex items-center justify-between text-sm text-slate-600">
                <span className="font-semibold text-slate-900">{provider.provider}</span>
                <span>
                  ${provider.total_cost.toFixed(2)} · {provider.resource_count} records
                </span>
              </div>
              <div className="h-3 rounded-full bg-slate-100">
                <div className="h-3 rounded-full bg-gradient-to-r from-emerald-500 to-cyan-500" style={{ width: `${ratio}%` }} />
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

