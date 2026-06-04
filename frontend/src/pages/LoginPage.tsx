import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";

import { login } from "../api/client";
import { useAuthStore } from "../store/authStore";

export function LoginPage() {
  const navigate = useNavigate();
  const setSession = useAuthStore((state) => state.setSession);
  const [email, setEmail] = useState("admin@thriftcloud.dev");
  const [password, setPassword] = useState("demo12345");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      const response = await login(email, password);
      setSession(response.access_token, response.user);
      navigate("/dashboard");
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Unable to sign in.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(16,185,129,0.28),_transparent_28%),linear-gradient(135deg,_#f8fafc,_#ecfeff_45%,_#fff7ed)] px-6 py-12">
      <div className="mx-auto grid max-w-6xl gap-10 lg:grid-cols-[1.1fr_0.9fr]">
        <section className="rounded-[2rem] border border-white/70 bg-white/75 p-8 shadow-float backdrop-blur lg:p-12">
          <p className="text-sm font-semibold uppercase tracking-[0.32em] text-emerald-700">ThriftCloud</p>
          <h1 className="mt-5 max-w-xl text-5xl font-semibold leading-tight text-slate-900">
            FinOps intelligence built to feel like a real capstone, not a class demo.
          </h1>
          <p className="mt-6 max-w-2xl text-lg text-slate-600">
            Start with local-first data, explain spend with confidence, and grow into forecasting, anomaly detection,
            and AI-guided optimization.
          </p>
          <div className="mt-10 grid gap-4 md:grid-cols-3">
            {[
              "JWT auth and seeded demo accounts",
              "Multi-cloud billing summary and recommendations",
              "Architecture ready for ML and AI expansion"
            ].map((item) => (
              <div key={item} className="rounded-3xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
                {item}
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-float">
          <p className="text-sm font-semibold uppercase tracking-[0.28em] text-slate-500">Sign in</p>
          <h2 className="mt-3 text-3xl font-semibold text-slate-900">Open the live demo workspace</h2>
          <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
            <label className="block">
              <span className="mb-2 block text-sm font-medium text-slate-700">Email</span>
              <input
                className="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none transition focus:border-emerald-400"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
              />
            </label>
            <label className="block">
              <span className="mb-2 block text-sm font-medium text-slate-700">Password</span>
              <input
                type="password"
                className="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none transition focus:border-emerald-400"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
              />
            </label>
            {error ? <p className="text-sm text-rose-600">{error}</p> : null}
            <button
              type="submit"
              className="w-full rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold uppercase tracking-[0.18em] text-white transition hover:bg-slate-800"
              disabled={submitting}
            >
              {submitting ? "Signing in..." : "Launch dashboard"}
            </button>
          </form>
          <div className="mt-6 rounded-3xl bg-emerald-50 p-4 text-sm text-emerald-800">
            Demo credentials are prefilled from the seeded local database.
          </div>
        </section>
      </div>
    </main>
  );
}
