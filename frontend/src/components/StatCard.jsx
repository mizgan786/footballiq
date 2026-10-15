export default function StatCard({ label, value, sublabel, accent = "text" }) {
  const accentClass = {
    text: "text-[var(--color-text)]",
    amber: "text-[var(--color-amber)]",
    blue: "text-[var(--color-blue)]",
  }[accent];

  return (
    <div className="border border-[var(--color-border)] rounded p-4 bg-[var(--color-panel)]">
      <div className="text-sm text-[var(--color-text-muted)]">{label}</div>
      <div className={`font-display text-3xl mt-1 ${accentClass}`}>{value}</div>
      {sublabel && <div className="text-xs text-[var(--color-text-faint)] mt-1">{sublabel}</div>}
    </div>
  );
}
