// Radar caps: our dataset has goals/assists/minutes/market value, not
// passing/defensive-actions/chance-creation (not present in this data source) -
// so the radar compares the dimensions we actually have, normalized to 0-100
// against sensible ceilings observed in the training data.
export const RADAR_CAPS = {
  Goals: 25,
  Assists: 20,
  Appearances: 38,
  "Goals/90": 1.0,
  "Assists/90": 0.7,
  "Market Value": 200, // in millions
};

export function buildRadarData(a, b) {
  const s = (p) => p.latest_season;
  const pct = (val, cap) => Math.min(100, Math.round((val / cap) * 100));
  return [
    { metric: "Goals", a: pct(s(a).goals, RADAR_CAPS.Goals), b: pct(s(b).goals, RADAR_CAPS.Goals) },
    { metric: "Assists", a: pct(s(a).assists, RADAR_CAPS.Assists), b: pct(s(b).assists, RADAR_CAPS.Assists) },
    {
      metric: "Appearances",
      a: pct(s(a).appearances, RADAR_CAPS.Appearances),
      b: pct(s(b).appearances, RADAR_CAPS.Appearances),
    },
    {
      metric: "Goals/90",
      a: pct(s(a).goals_per_90, RADAR_CAPS["Goals/90"]),
      b: pct(s(b).goals_per_90, RADAR_CAPS["Goals/90"]),
    },
    {
      metric: "Assists/90",
      a: pct(s(a).assists_per_90, RADAR_CAPS["Assists/90"]),
      b: pct(s(b).assists_per_90, RADAR_CAPS["Assists/90"]),
    },
    {
      metric: "Market Value",
      a: pct(s(a).market_value_in_eur / 1_000_000, RADAR_CAPS["Market Value"]),
      b: pct(s(b).market_value_in_eur / 1_000_000, RADAR_CAPS["Market Value"]),
    },
  ];
}
