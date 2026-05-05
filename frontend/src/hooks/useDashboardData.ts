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
      lead_status: "completed",
      lead_score: 86,
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
      lead_status: "completed",
      lead_score: 58,
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
      lead_status: "completed",
      lead_score: 34,
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
  const [liveTranscript, setLiveTranscript] = useState<Record<string, string[]>>({});
  const [tuningDebug, setTuningDebug] = useState<Record<string, unknown> | null>(null);

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

  useEffect(() => {
    const wsBase = (import.meta.env.VITE_WS_BASE_URL ?? "ws://localhost:8000").replace(/\/$/, "");
    const socket = new WebSocket(`${wsBase}/api/v1/calls/dashboard`);

    socket.onopen = () => setOfflineMode(false);
    socket.onerror = () => setOfflineMode(true);
    socket.onmessage = (message) => {
      try {
        const parsed = JSON.parse(message.data) as {
          event: string;
          payload: Record<string, unknown>;
        };
        const payload = parsed.payload;

        if (parsed.event === "transcript_update") {
          const callId = String(payload.call_id ?? "");
          const text = String(payload.text ?? "");
          if (!callId || !text) {
            return;
          }
          setLiveTranscript((prev) => ({
            ...prev,
            [callId]: [...(prev[callId] ?? []), text].slice(-30),
          }));
        }

        if (parsed.event === "lead_scored") {
          const leadId = String(payload.lead_id ?? "");
          const score = Number(payload.score ?? 0);
          const category = String(payload.category ?? "");
          setData((prev) => ({
            ...prev,
            funnel: {
              ...prev.funnel,
              hot: category === "HOT" ? prev.funnel.hot + 1 : prev.funnel.hot,
              warm: category === "WARM" ? prev.funnel.warm + 1 : prev.funnel.warm,
              cold: category === "COLD" ? prev.funnel.cold + 1 : prev.funnel.cold,
            },
            call_summaries: prev.call_summaries.map((item) =>
              item.lead_id === leadId
                ? { ...item, lead_score: score, classification: category, lead_status: "scored" }
                : item,
            ),
          }));
        }

        if (parsed.event === "lead_routed") {
          const leadId = String(payload.lead_id ?? "");
          const route = String(payload.route ?? "");

          let leadStatus = "completed";
          if (route === "rm_queue") leadStatus = "assigned";
          if (route === "whatsapp") leadStatus = "followup_sent";
          if (route === "nurture_30_days") leadStatus = "nurture_scheduled";

          setData((prev) => ({
            ...prev,
            call_summaries: prev.call_summaries.map((item) =>
              item.lead_id === leadId ? { ...item, lead_status: leadStatus } : item,
            ),
          }));
        }

        if (parsed.event === "tuning_debug") {
          setTuningDebug(payload);
        }
      } catch {
        setOfflineMode(true);
      }
    };

    return () => socket.close();
  }, []);

  return { data, offlineMode, liveTranscript, tuningDebug };
}
