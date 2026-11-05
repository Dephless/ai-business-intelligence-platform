
export interface Metric {
  field: string;
  count: number;
  total: number;
  average: number;
  minimum: number;
  maximum: number;
}

export interface Recommendation {
  title: string;
  description: string;
  priority: "low" | "medium" | "high";
  rationale: string;
  confidence: number;
}

export interface AnalysisResult {
  summary: string;
  record_count: number;
  numeric_metrics: Metric[];
  recommendations: Recommendation[];
  llm_enhanced: boolean;
}

export interface Analysis {
  id: number;
  dataset_name: string;
  record_count: number;
  result: AnalysisResult;
  created_at: string;
}

export interface User {
  id: number;
  email: string;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}
