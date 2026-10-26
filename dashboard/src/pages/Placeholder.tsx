type PlaceholderProps = { title: string };

export function Placeholder({ title }: PlaceholderProps) {
  return (
    <section className="placeholder-card" aria-labelledby="placeholder-title">
      <p className="eyebrow">COMING IN A LATER MILESTONE</p>
      <h2 id="placeholder-title">{title}</h2>
      <p className="muted">This protected page is reserved for the Ceravox voice workflow.</p>
    </section>
  );
}
