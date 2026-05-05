export type FunnelMetrics = {
  total_leads: number;
  hot: number;
  warm: number;
  cold: number;
  hot_rate: number;
};

export type CallSummaryItem = {
  call_id: string;
  lead_id: string;
  customer_name: string;
  classification: string | null;
  language: string | null;
  intent: string | null;
  next_action: string | null;
  summary: string | null;
  duration_seconds: number;
};

export type RMTrackingItem = {
  rm_name: string;
  assigned_leads: number;
  hot_leads: number;
  warm_leads: number;
};

export type DashboardResponse = {
  funnel: FunnelMetrics;
  call_summaries: CallSummaryItem[];
  rm_tracking: RMTrackingItem[];
  language_distribution: Record<string, number>;
};

