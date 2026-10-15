export function formatEur(value) {
  if (value == null || Number.isNaN(value)) return "—";
  if (Math.abs(value) >= 1_000_000) {
    return `€${(value / 1_000_000).toFixed(1)}M`;
  }
  if (Math.abs(value) >= 1_000) {
    return `€${(value / 1_000).toFixed(0)}K`;
  }
  return `€${value.toFixed(0)}`;
}

export function formatEurFull(value) {
  if (value == null || Number.isNaN(value)) return "—";
  return new Intl.NumberFormat("en-DE", { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(
    value
  );
}

export function formatPercent(value, digits = 0) {
  if (value == null || Number.isNaN(value)) return "—";
  return `${(value * 100).toFixed(digits)}%`;
}

export function formatDiff(predicted, actual) {
  if (predicted == null || actual == null) return null;
  const diff = predicted - actual;
  const pct = actual !== 0 ? (diff / actual) * 100 : 0;
  return { diff, pct, direction: diff >= 0 ? "above" : "below" };
}

export const LEAGUE_NAMES = {
  GB1: "Premier League",
  ES1: "La Liga",
  L1: "Bundesliga",
  IT1: "Serie A",
  FR1: "Ligue 1",
};

export const POSITION_NAMES = {
  Attack: "Attacker",
  Midfield: "Midfielder",
  Defender: "Defender",
  Goalkeeper: "Goalkeeper",
};
