import { ReactNode } from "react";

type FeatureRowProps = {
  id?: string;
  eyebrow?: string;
  title: string;
  body: string;
  bullets?: string[];
  reverse?: boolean;
  visual: ReactNode;
  className?: string;
};

export function FeatureRow({ id, eyebrow, title, body, bullets, reverse, visual, className = "" }: FeatureRowProps) {
  return (
    <section className={`landing-section ${className}`.trim()} id={id}>
      <div className={`landing-feature ${reverse ? "landing-feature--reverse" : ""}`}>
        <div className="landing-feature__text">
          {eyebrow ? <p className="landing-section__eyebrow">{eyebrow}</p> : null}
          <h2 className="landing-section__h2">{title}</h2>
          <p className="landing-section__body">{body}</p>
          {bullets && bullets.length > 0 ? (
            <ul className="icon-list">
              {bullets.map((text) => (
                <li key={text} className="icon-list__item">
                  <span className="icon-list__check" aria-hidden>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                      <circle cx="12" cy="12" r="10" fill="var(--primary-soft)" />
                      <path
                        d="M8 12.5 10.5 15 16 9"
                        stroke="var(--primary)"
                        strokeWidth="1.8"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                  </span>
                  {text}
                </li>
              ))}
            </ul>
          ) : null}
        </div>
        <div className="landing-feature__visual">{visual}</div>
      </div>
    </section>
  );
}
