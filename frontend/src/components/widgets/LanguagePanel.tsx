type LanguagePanelProps = {
  languages: Record<string, number>;
};

export function LanguagePanel({ languages }: LanguagePanelProps) {
  const entries = Object.entries(languages);

  return (
    <section className="panel">
      <div className="panel-heading">
        <h2>Language Detection</h2>
        <span>Real-time language distribution</span>
      </div>
      <div className="language-grid">
        {entries.map(([language, count]) => (
          <article className="language-card" key={language}>
            <span>{language}</span>
            <strong>{count}</strong>
          </article>
        ))}
      </div>
    </section>
  );
}

