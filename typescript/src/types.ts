/**
 * Revtelic MCP & SDK Type Definitions
 *
 */

export interface RevtelicConfig {
  apiBase?: string;
  apiKey?: string;
}

export interface AnalyzeDealArgs {
  transcript: string;
  name?: string;
}

export interface DealRisk {
  type: string;
  severity: "critical" | "high" | "medium" | "low";
  description: string;
  evidence?: string;
  mitigation?: string;
}

export interface Stakeholder {
  name: string;
  role?: string;
  sentiment?: "champion" | "supporter" | "neutral" | "blocker" | "unknown";
  influence?: "high" | "medium" | "low";
  is_economic_buyer?: boolean;
}

export interface NextAction {
  action: string;
  rationale?: string;
  owner?: string;
  deadline?: string;
}

export interface DealAnalysis {
  deal_id?: string;
  id?: string;
  name?: string;
  health_score: number;
  status?: "healthy" | "slipping" | "critical" | "stalled";
  brutal_truth: string;
  strengths?: string[];
  risks: DealRisk[] | string[];
  stakeholders?: Stakeholder[];
  qualification_gaps?: string[];
  next_best_action?: NextAction | string;
  one_pager_url?: string;
  claim_and_save_url?: string;
  onboarding_message?: string;
  raw?: Record<string, any>;
}

export interface DealboardSummary {
  id: string;
  name: string;
  slug?: string;
  health_score?: number;
  stage?: string;
  created_at?: string;
  updated_at?: string;
}
