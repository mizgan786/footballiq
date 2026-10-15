import { describe, it, expect } from "vitest";
import { formatEur, formatEurFull, formatPercent, formatDiff } from "../utils/format";

describe("formatEur", () => {
  it("formats millions with one decimal", () => {
    expect(formatEur(110_000_000)).toBe("€110.0M");
    expect(formatEur(3_500_000)).toBe("€3.5M");
  });

  it("formats thousands with no decimal", () => {
    expect(formatEur(25_000)).toBe("€25K");
  });

  it("formats small values as plain euros", () => {
    expect(formatEur(500)).toBe("€500");
  });

  it("handles null/undefined/NaN gracefully", () => {
    expect(formatEur(null)).toBe("—");
    expect(formatEur(undefined)).toBe("—");
    expect(formatEur(NaN)).toBe("—");
  });
});

describe("formatEurFull", () => {
  it("formats as a full currency string", () => {
    const result = formatEurFull(1_000_000);
    expect(result).toContain("1");
    expect(result).toMatch(/€/);
  });

  it("handles null gracefully", () => {
    expect(formatEurFull(null)).toBe("—");
  });
});

describe("formatPercent", () => {
  it("converts a fraction to a percentage string", () => {
    expect(formatPercent(0.283)).toBe("28%");
    expect(formatPercent(0.283, 1)).toBe("28.3%");
  });

  it("handles negative fractions", () => {
    expect(formatPercent(-0.44, 1)).toBe("-44.0%");
  });

  it("handles null gracefully", () => {
    expect(formatPercent(null)).toBe("—");
  });
});

describe("formatDiff", () => {
  it("computes direction 'above' when predicted exceeds actual", () => {
    const result = formatDiff(120, 100);
    expect(result.direction).toBe("above");
    expect(result.diff).toBe(20);
    expect(result.pct).toBeCloseTo(20);
  });

  it("computes direction 'below' when predicted is under actual", () => {
    const result = formatDiff(80, 100);
    expect(result.direction).toBe("below");
    expect(result.diff).toBe(-20);
  });

  it("returns null when either input is missing", () => {
    expect(formatDiff(null, 100)).toBeNull();
    expect(formatDiff(100, null)).toBeNull();
  });

  it("does not divide by zero when actual is 0", () => {
    const result = formatDiff(50, 0);
    expect(result.pct).toBe(0);
  });
});
