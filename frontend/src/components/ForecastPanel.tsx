import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { SpendForecastResponse } from "../types/dashboard";

interface ForecastPanelProps {
  forecast: SpendForecastResponse;
}

export function ForecastPanel({ forecast }: ForecastPanelProps) {
  const chartData = [...forecast.history, ...forecast.forecast];

  return (
    <section className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-float">
      <div className="mb-5 flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.24em] text-slate-500">Forecasting</p>
          <h3 className="mt-2 text-xl font-semibold text-slate-900">Projected spend trajectory</h3>
        </div>
        <div className="flex flex-wrap gap-2 text-xs font-semibold uppercase tracking-[0.14em]">
          <span className="rounded-full bg-cyan-50 px-3 py-1 text-cyan-700">
            {(forecast.confidence * 100).toFixed(0)}% confidence
          </span>
          <span className="rounded-full bg-slate-100 px-3 py-1 text-slate-600">{forecast.method.replace(/_/g, " ")}</span>
        </div>
      </div>

      <div className="mb-4 grid gap-3 sm:grid-cols-2">
        <div className="rounded-2xl bg-slate-50 px-4 py-3">
          <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Projected monthly change</p>
          <p className="mt-1 text-2xl font-semibold text-slate-900">
            {forecast.projected_monthly_change_percentage.toFixed(1)}%
          </p>
        </div>
        <div className="rounded-2xl bg-slate-50 px-4 py-3">
          <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Forecast horizon</p>
          <p className="mt-1 text-2xl font-semibold text-slate-900">{forecast.forecast.length} months</p>
        </div>
      </div>

      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid stroke="#e2e8f0" strokeDasharray="3 3" />
            <XAxis dataKey="label" tick={{ fill: "#64748b", fontSize: 12 }} />
            <YAxis tick={{ fill: "#64748b", fontSize: 12 }} />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="total_cost"
              name="Spend"
              stroke="#0ea5e9"
              strokeWidth={3}
              dot={{ r: 4 }}
              connectNulls
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
