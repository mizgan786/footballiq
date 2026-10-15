import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import StatCard from "./StatCard";

describe("StatCard", () => {
  it("renders label and value", () => {
    render(<StatCard label="Model R²" value="0.73" />);
    expect(screen.getByText("Model R²")).toBeInTheDocument();
    expect(screen.getByText("0.73")).toBeInTheDocument();
  });

  it("renders sublabel when provided", () => {
    render(<StatCard label="Highest valued" value="Haaland" sublabel="€180.0M" />);
    expect(screen.getByText("€180.0M")).toBeInTheDocument();
  });

  it("omits sublabel when not provided", () => {
    render(<StatCard label="Players" value="10,153" />);
    expect(screen.getByText("Players")).toBeInTheDocument();
    expect(screen.getByText("10,153")).toBeInTheDocument();
    expect(screen.queryByText(/€/)).not.toBeInTheDocument();
  });
});
