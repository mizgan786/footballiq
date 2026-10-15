import { describe, it, expect } from "vitest";
import { buildRadarData } from "./radar";

function makePlayer(overrides) {
  return {
    latest_season: {
      goals: 10, assists: 5, appearances: 30,
      goals_per_90: 0.3, assists_per_90: 0.15,
      market_value_in_eur: 50_000_000,
      ...overrides,
    },
  };
}

describe("buildRadarData", () => {
  it("produces one entry per metric, six total", () => {
    const data = buildRadarData(makePlayer(), makePlayer());
    expect(data).toHaveLength(6);
    expect(data.map((d) => d.metric)).toEqual([
      "Goals", "Assists", "Appearances", "Goals/90", "Assists/90", "Market Value",
    ]);
  });

  it("normalizes values to 0-100 against fixed caps", () => {
    const a = makePlayer({ goals: 25 }); // cap is 25 -> should be exactly 100
    const b = makePlayer({ goals: 0 });
    const data = buildRadarData(a, b);
    const goalsRow = data.find((d) => d.metric === "Goals");
    expect(goalsRow.a).toBe(100);
    expect(goalsRow.b).toBe(0);
  });

  it("clamps values above the cap at 100 rather than exceeding it", () => {
    const a = makePlayer({ market_value_in_eur: 400_000_000 }); // way above the 200M cap
    const data = buildRadarData(a, makePlayer());
    const valueRow = data.find((d) => d.metric === "Market Value");
    expect(valueRow.a).toBe(100);
  });

  it("computes a mid-range percentage correctly", () => {
    const a = makePlayer({ assists: 10 }); // cap is 20 -> 50%
    const data = buildRadarData(a, makePlayer());
    const assistsRow = data.find((d) => d.metric === "Assists");
    expect(assistsRow.a).toBe(50);
  });
});
