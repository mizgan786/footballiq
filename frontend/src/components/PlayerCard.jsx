import { Link } from "react-router-dom";
import { formatEur, POSITION_NAMES } from "../utils/format";

export default function PlayerCard({ player }) {
  return (
    <Link
      to={`/players/${player.id}`}
      className="block border border-[var(--color-border)] rounded p-4 bg-[var(--color-panel)] hover:border-[var(--color-border-strong)] transition-colors"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="font-medium truncate">{player.name}</div>
          <div className="text-sm text-[var(--color-text-muted)] truncate">
            {player.club_name || "Unknown club"}
          </div>
        </div>
        <span className="shrink-0 text-xs px-2 py-1 rounded border border-[var(--color-border-strong)] text-[var(--color-text-muted)]">
          {POSITION_NAMES[player.position] || player.position || "—"}
        </span>
      </div>
      <div className="flex items-end justify-between mt-4">
        <div className="text-xs text-[var(--color-text-faint)]">
          Age {player.age != null ? player.age.toFixed(1) : "—"} · {player.season}
        </div>
        <div className="font-display text-xl text-[var(--color-amber)]">
          {formatEur(player.market_value_in_eur)}
        </div>
      </div>
    </Link>
  );
}
