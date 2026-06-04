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
  title: string;
  provider: string;
  estimated_savings: number;
  confidence: number;
  description: string;
}

export interface DashboardSummary {
  viewer_name: string;
  total_cost: number;
  monthly_change_percentage: number;
  finops_score: number;
  waste_percentage: number;
  providers: ProviderSpend[];
  trend: SpendPoint[];
  recommendations: RecommendationItem[];
  updated_at: string;
}

