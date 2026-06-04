interface ScoreDialProps {
  score: number;
  wastePercentage: number;
}

export function ScoreDial({ score, wastePercentage }: ScoreDialProps) {
  const circumference = 2 * Math.PI * 54;
  const progress = circumference - (score / 100) * circumference;

  return (
    <section className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-float">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.24em] text-slate-500">FinOps Score</p>
          <p className="mt-2 max-w-xs text-sm text-slate-500">
            Weighted from waste exposure, idle resources, and provider coverage.
          </p>
        </div>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-slate-600">
          Waste {wastePercentage.toFixed(1)}%
        </span>
      </div>

      <div className="mt-6 flex items-center gap-8">
        <svg viewBox="0 0 140 140" className="h-40 w-40">
          <circle cx="70" cy="70" r="54" fill="none" stroke="#e2e8f0" strokeWidth="12" />
          <circle
            cx="70"
            cy="70"
            r="54"
            fill="none"
            stroke="#10b981"
            strokeWidth="12"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={progress}
            transform="rotate(-90 70 70)"
          />
          <text x="50%" y="50%" dominantBaseline="middle" textAnchor="middle" className="fill-slate-900 text-3xl font-bold">
            {score}
          </text>
        </svg>

        <div className="space-y-4 text-sm text-slate-600">
          <p>
            A capstone-ready story starts here: we can already explain spend, quantify waste, and point to high-value
            actions.
          </p>
          <p>
            Next iterations can plug in forecasting, anomaly detection, and AI-generated explanations without changing
            the overall shell.
          </p>
        </div>
      </div>
    </section>
  );
}

