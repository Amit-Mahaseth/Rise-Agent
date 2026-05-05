export type VoiceCampaign = {
  id: string;
  title: string;
  segment: string;
  description: string;
  languages: string[];
  status: "active" | "paused";
  touches_24h: number;
  hot_capture_rate: string;
};

export const VOICE_CAMPAIGNS: VoiceCampaign[] = [
  {
    id: "prime-outbound-pl",
    title: "Prime PL outbound",
    segment: "Web leads · ₹2–8L intent",
    description:
      "First-touch outbound with dynamic FAQ retrieval and multilingual handoff cues for RM desks.",
    languages: ["Hinglish", "English", "Hindi"],
    status: "active",
    touches_24h: 118,
    hot_capture_rate: "24%",
  },
  {
    id: "whatsapp-warm-recovery",
    title: "WhatsApp warm nurture",
    segment: "Warm · stalled applications",
    description:
      "Short voice notes + scripted WhatsApp payloads when the borrower pauses mid-funnel.",
    languages: ["English", "Tamil"],
    status: "active",
    touches_24h: 64,
    hot_capture_rate: "11%",
  },
  {
    id: "reengagement-cold-batch",
    title: "Cold re-activation",
    segment: "Dormant · 30–90 days",
    description:
      "Low-pressure recall window with reschedule preferences and objection handling from base scripts.",
    languages: ["Hindi", "Marathi", "Telugu"],
    status: "paused",
    touches_24h: 0,
    hot_capture_rate: "6%",
  },
];
