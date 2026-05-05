import { useState } from "react";

import { FeatureHraMockup } from "./FeatureHraMockup";

const items = [
  {
    id: "deterministic",
    title: "Deterministic by design",
    body: "Orchestration graphs keep disclosures and disclosures-first flows repeatable—no surprise branching that breaks compliance.",
    icon: IconFlow,
  },
  {
    id: "healthcare",
    title: "Built for regulated conversations",
    body: "Retrieval is grounded in your playbooks and FAQs; every turn can be traced back to source material for audits.",
    icon: IconShield,
  },
  {
    id: "human",
    title: "Human-like engagement",
    body: "Empathic pacing, barge-in friendly turn-taking, and language detection so borrowers stay in-channel.",
    icon: IconVoice,
  },
  {
    id: "outcomes",
    title: "Outcomes you can measure",
    body: "Hot/Warm/Cold scoring, RM routing, and funnel analytics in one console tied to call transcripts.",
    icon: IconChart,
  },
] as const;

export function WhyChooseSection() {
  const [openId, setOpenId] = useState<string>(items[0].id);

  return (
    <section className="landing-section landing-section--soft" id="solutions">
      <div className="landing-why">
        <div className="landing-why__visual">
          <FeatureHraMockup />
        </div>
        <div className="landing-why__content">
          <p className="landing-section__label">The RiseAgent standard</p>
          <h2 className="landing-section__h2">Why organizations choose RiseAgent</h2>
          <div className="accordion">
            {items.map((item) => {
              const open = openId === item.id;
              const ItemIcon = item.icon;
              return (
                <div key={item.id} className={`accordion__item ${open ? "accordion__item--open" : ""}`}>
                  <button
                    type="button"
                    className="accordion__trigger"
                    onClick={() => setOpenId(open ? "" : item.id)}
                    aria-expanded={open}
                  >
                    <span className="accordion__icon">
                      <ItemIcon />
                    </span>
                    <span className="accordion__title">{item.title}</span>
                    <span className="accordion__plus" aria-hidden>
                      {open ? "−" : "+"}
                    </span>
                  </button>
                  {open ? <p className="accordion__body">{item.body}</p> : null}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}

function IconFlow() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
      <circle cx="6" cy="6" r="2.5" />
      <circle cx="18" cy="6" r="2.5" />
      <circle cx="12" cy="18" r="2.5" />
      <path d="M8 7.5h8M12 8.5v7M8 18h8" strokeLinecap="round" />
    </svg>
  );
}

function IconShield() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
      <path d="M12 3 5 6v6c0 5 4.5 8 7 9 2.5-1 7-4 7-9V6l-7-3Z" strokeLinejoin="round" />
    </svg>
  );
}

function IconVoice() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
      <path d="M12 14a3 3 0 0 0 3-3V7a3 3 0 0 0-6 0v4a3 3 0 0 0 3 3Z" />
      <path d="M19 11a7 7 0 0 1-14 0M12 18v3M8 21h8" strokeLinecap="round" />
    </svg>
  );
}

function IconChart() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
      <path d="M4 20V10M10 20V4M16 20v-6M22 20V14" strokeLinecap="round" />
    </svg>
  );
}
