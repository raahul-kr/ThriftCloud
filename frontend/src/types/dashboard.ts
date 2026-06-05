export interface User {
  id: number;
  email: string;
  full_name: string;
  role: "admin" | "viewer";
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface ProviderSpend {
  provider: string;
  total_cost: number;
  resource_count: number;
}

export interface SpendPoint {
  label: string;
  total_cost: number;
}

export interface RecommendationItem {
  id: number;
  recommendation_key: string;
  rule_key: string;
  category: string;
  status: string;
  severity: string;
  title: string;
  provider: string;
  service_name?: string | null;
  region?: string | null;
  resource_count: number;
  estimated_monthly_savings: number;
  estimated_annual_savings: number;
  confidence: number;
  description: string;
  evidence: string[];
  next_steps: string[];
  assigned_owner?: string | null;
  detected_at: string;
  updated_at: string;
  acknowledged_at?: string | null;
}

export type RecommendationAction = "acknowledge" | "dismiss" | "assign_owner" | "resolve";

export interface RecommendationUpdateResponse {
  item: RecommendationItem;
  message: string;
}

export interface ForecastPoint {
  label: string;
  total_cost: number;
  kind: "actual" | "forecast" | string;
}

export interface SpendForecastResponse {
  history: ForecastPoint[];
  forecast: ForecastPoint[];
  projected_monthly_change_percentage: number;
  confidence: number;
  method: string;
  generated_at: string;
}

export interface SpendAnomaly {
  provider: string;
  label: string;
  observed_cost: number;
  baseline_cost: number;
  deviation_percentage: number;
  severity: string;
  summary: string;
}

export interface SpendAnomalyResponse {
  items: SpendAnomaly[];
  scanned_points: number;
  generated_at: string;
}

export interface DashboardSummary {
  viewer_name: string;
  total_cost: number;
  monthly_change_percentage: number;
  finops_score: number;
  waste_percentage: number;
  active_rule_count: number;
  triggered_rule_count: number;
  open_recommendation_count: number;
  potential_monthly_savings: number;
  potential_annual_savings: number;
  providers: ProviderSpend[];
  trend: SpendPoint[];
  recommendations: RecommendationItem[];
  updated_at: string;
}
