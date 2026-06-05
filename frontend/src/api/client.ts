import type {
  AuthResponse,
  DashboardSummary,
  RecommendationAction,
  RecommendationUpdateResponse,
  SpendAnomalyResponse,
  SpendForecastResponse
} from "../types/dashboard";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {})
    },
    ...options
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail ?? "Request failed");
  }

  return response.json() as Promise<T>;
}

export function login(email: string, password: string): Promise<AuthResponse> {
  return request<AuthResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password })
  });
}

export function fetchDashboard(token: string): Promise<DashboardSummary> {
  return request<DashboardSummary>("/dashboard/summary", {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
}

export function fetchSpendForecast(token: string): Promise<SpendForecastResponse> {
  return request<SpendForecastResponse>("/dashboard/forecast", {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
}

export function fetchSpendAnomalies(token: string): Promise<SpendAnomalyResponse> {
  return request<SpendAnomalyResponse>("/dashboard/anomalies", {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
}

export function updateRecommendation(
  token: string,
  recommendationId: number,
  action: RecommendationAction,
  assignedOwner?: string
): Promise<RecommendationUpdateResponse> {
  return request<RecommendationUpdateResponse>(`/dashboard/recommendations/${recommendationId}`, {
    method: "PATCH",
    headers: {
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({
      action,
      assigned_owner: assignedOwner
    })
  });
}

