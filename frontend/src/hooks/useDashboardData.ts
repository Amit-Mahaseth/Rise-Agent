import { useEffect, useState } from "react";

import { fetchDashboardSummary } from "../api/client";
import type { DashboardResponse } from "../types/dashboard";

export const FALLBACK_DASHBOARD: DashboardResponse = {
  funnel: {
    total_leads: 42,
    hot: 11,
    warm: 18,
    cold: 13,
    hot_rate: 26.19,
  },
  call_summaries: [
    {
      call_id: "call-demo-1",
      lead_id: "LD-1001",
      customer_name: "Priya Sharma",
      classification: "HOT",
      language: "Hinglish",
      intent: "high",
      next_action: "handoff_to_rm",
      summary: "Asked for eligibility and documents, requested same-day RM callback.",
      duration_seconds: 221,
    },
    {
      call_id: "call-demo-2",
      lead_id: "LD-1002",
      customer_name: "Arjun Rao",
      classification: "WARM",
      language: "English",
      intent: "medium",
      next_action: "send_whatsapp_followup",
      summary: "Interested but wanted details over WhatsApp before proceeding.",
      duration_seconds: 138,
    },
    {
      call_id: "call-demo-3",
      lead_id: "LD-1003",
      customer_name: "Neha Gupta",
      classification: "COLD",
      language: "Hindi",
      intent: "low",
      next_action: "schedule_reengagement",
      summary: "Price-sensitive; deferred decision after rate discussion.",
      duration_seconds: 94,
    },
  ],
  rm_tracking: [
    { rm_name: "RM North Desk", assigned_leads: 8, hot_leads: 4, warm_leads: 3 },
    { rm_name: "RM Prime Desk", assigned_leads: 6, hot_leads: 2, warm_leads: 3 },
  ],
  language_distribution: {
    Hinglish: 12,
    English: 10,
    Hindi: 8,
    Marathi: 5,
    Tamil: 3,
    Telugu: 2,
    Gujarati: 1,
    Bengali: 1,
  },
};

export function useDashboardData() {
  const [data, setData] = useState<DashboardResponse>(FALLBACK_DASHBOARD);
  const [offlineMode, setOfflineMode] = useState(true);

  useEffect(() => {
    let active = true;

    fetchDashboardSummary()
      .then((response) => {
        if (!active) {
          return;
        }
        setData(response);
        setOfflineMode(false);
      })
      .catch(() => {
        if (active) {
          setOfflineMode(true);
        }
      });

    return () => {
      active = false;
    };
  }, []);

  return { data, offlineMode };
}
