import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";

import PlayerSearch from "./PlayerSearch";
import { listPlayers, getClubs } from "../services/api";

vi.mock("../services/api", () => ({
  listPlayers: vi.fn(),
  getClubs: vi.fn(),
}));

const SAKA = {
  id: 433177, name: "Bukayo Saka", club_name: "Arsenal FC", position: "Attack",
  age: 24.8, season: 2025, market_value_in_eur: 110_000_000,
};
const HAALAND = {
  id: 418560, name: "Erling Haaland", club_name: "Manchester City", position: "Attack",
  age: 25.1, season: 2025, market_value_in_eur: 180_000_000,
};

function renderPage() {
  return render(
    <MemoryRouter>
      <PlayerSearch />
    </MemoryRouter>
  );
}

beforeEach(() => {
  vi.clearAllMocks();
  getClubs.mockResolvedValue([{ id: 11, name: "Arsenal FC" }, { id: 281, name: "Manchester City" }]);
  listPlayers.mockResolvedValue([SAKA, HAALAND]);
});

describe("PlayerSearch", () => {
  it("loads and renders players on mount", async () => {
    renderPage();
    expect(await screen.findByText("Bukayo Saka")).toBeInTheDocument();
    expect(screen.getByText("Erling Haaland")).toBeInTheDocument();
    expect(listPlayers).toHaveBeenCalledWith(
      expect.objectContaining({ sort_by: "market_value_in_eur", order: "desc" })
    );
  });

  it("shows a loading state before results arrive", async () => {
    listPlayers.mockReturnValue(new Promise(() => {})); // never resolves
    renderPage();
    expect(screen.getByText(/searching players/i)).toBeInTheDocument();
    await screen.findByText("Arsenal FC", {}, { timeout: 100 }).catch(() => {}); // let getClubs settle quietly
  });

  it("shows an empty state when no players match", async () => {
    listPlayers.mockResolvedValue([]);
    renderPage();
    expect(await screen.findByText(/no players match these filters/i)).toBeInTheDocument();
  });

  it("shows an error state when the request fails, with a working retry", async () => {
    listPlayers.mockRejectedValueOnce(new Error("Network error"));
    renderPage();
    expect(await screen.findByText("Network error")).toBeInTheDocument();

    listPlayers.mockResolvedValueOnce([SAKA]);
    await userEvent.click(screen.getByRole("button", { name: /try again/i }));
    expect(await screen.findByText("Bukayo Saka")).toBeInTheDocument();
  });

  it("debounces name search and sends the query to the API", async () => {
    renderPage();
    await screen.findByText("Bukayo Saka");
    listPlayers.mockClear();

    const input = screen.getByPlaceholderText(/search by name/i);
    await userEvent.type(input, "Saka");

    // should not fire on every keystroke - shouldn't have called yet immediately
    expect(listPlayers).not.toHaveBeenCalled();

    await waitFor(() => expect(listPlayers).toHaveBeenCalledWith(expect.objectContaining({ name: "Saka" })), {
      timeout: 2000,
    });
  });

  it("sends the selected position filter to the API", async () => {
    renderPage();
    await screen.findByText("Bukayo Saka");
    listPlayers.mockClear();

    const select = screen.getByDisplayValue("All positions");
    await userEvent.selectOptions(select, "Attack");

    await waitFor(() => expect(listPlayers).toHaveBeenCalledWith(expect.objectContaining({ position: "Attack" })));
  });

  it("toggles sort order when the direction button is clicked", async () => {
    renderPage();
    await screen.findByText("Bukayo Saka");
    listPlayers.mockClear();

    await userEvent.click(screen.getByTitle("Descending"));

    await waitFor(() => expect(listPlayers).toHaveBeenCalledWith(expect.objectContaining({ order: "asc" })));
  });
});
