import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import PlayerCard from "./PlayerCard";

const player = {
  id: 433177,
  name: "Bukayo Saka",
  club_name: "Arsenal FC",
  position: "Attack",
  age: 24.8,
  season: 2025,
  market_value_in_eur: 110_000_000,
};

function renderCard(props) {
  return render(
    <MemoryRouter>
      <PlayerCard player={{ ...player, ...props }} />
    </MemoryRouter>
  );
}

describe("PlayerCard", () => {
  it("renders player name, club, and formatted value", () => {
    renderCard();
    expect(screen.getByText("Bukayo Saka")).toBeInTheDocument();
    expect(screen.getByText("Arsenal FC")).toBeInTheDocument();
    expect(screen.getByText("€110.0M")).toBeInTheDocument();
  });

  it("links to the player's profile page", () => {
    renderCard();
    expect(screen.getByRole("link")).toHaveAttribute("href", "/players/433177");
  });

  it("falls back gracefully when club_name is missing", () => {
    renderCard({ club_name: null });
    expect(screen.getByText("Unknown club")).toBeInTheDocument();
  });

  it("translates the raw position code to a readable label", () => {
    renderCard({ position: "Midfield" });
    expect(screen.getByText("Midfielder")).toBeInTheDocument();
  });
});
