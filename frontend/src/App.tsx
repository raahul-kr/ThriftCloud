import { lazy, Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { useAuthStore } from "./store/authStore";

const LoginPage = lazy(() =>
  import("./pages/LoginPage").then((module) => ({ default: module.LoginPage }))
);
const DashboardPage = lazy(() =>
  import("./pages/DashboardPage").then((module) => ({ default: module.DashboardPage }))
);

function ProtectedRoute() {
  const token = useAuthStore((state) => state.token);
  return token ? <DashboardPage /> : <Navigate to="/" replace />;
}

export default function App() {
  return (
    <Suspense fallback={<div className="flex min-h-screen items-center justify-center text-slate-600">Loading...</div>}>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/dashboard" element={<ProtectedRoute />} />
      </Routes>
    </Suspense>
  );
}
