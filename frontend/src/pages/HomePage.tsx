import { AttuneHero } from "../components/landing/AttuneHero";
import { FeatureChatMockup } from "../components/landing/FeatureChatMockup";
import { FeatureRow } from "../components/landing/FeatureRow";
import { LandingShell } from "../components/landing/LandingShell";
import { PlatformCards } from "../components/landing/PlatformCards";
import { WhyChooseSection } from "../components/landing/WhyChooseSection";
import { useDashboardData } from "../hooks/useDashboardData";

export function HomePage() {
  const { offlineMode } = useDashboardData();

  return (
    <LandingShell offlineMode={offlineMode}>
      <AttuneHero />

      <FeatureRow
        id="engage"
        title="A better way to engage borrowers & applicants"
        body="Give every lead a consistent first conversation: disclosures, eligibility, and next steps—without burning desk time on cold outreach."
        bullets={[
          "Live language detection with retrieval-backed answers from your playbooks.",
          "Hot/Warm/Cold scoring so sales sees intent before the callback.",
          "WhatsApp and RM routing triggered from the same voice session.",
        ]}
        visual={<FeatureChatMockup />}
      />

      <WhyChooseSection />

      <PlatformCards />

      <section className="landing-section landing-cta-band" id="company">
        <div className="landing-cta-band__inner">
          <h2 className="landing-section__h2 landing-section__h2--center">Ready to hear RiseAgent on your funnel?</h2>
          <p className="landing-section__sub landing-section__sub--center">
            Book a walkthrough with your scripts and we will map queue → voice → desk handoff.
          </p>
          <button type="button" className="btn btn--primary btn--lg">
            Book a demo
          </button>
        </div>
      </section>

      <section className="landing-section landing-section--muted" id="resources">
        <div className="landing-resources">
          <h2 className="landing-section__h2">Resources</h2>
          <p className="landing-section__body">
            Architecture notes, API references, and desk playbooks ship with the repo. Operators can jump into the
            live console to inspect funnel and call intelligence.
          </p>
        </div>
      </section>
    </LandingShell>
  );
}
