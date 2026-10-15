import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";

import Predictor from "./Predictor";
import { predictValue, getClubs, getModelMetrics } from "../services/api";

vi.mock("../services/api", () => ({
  predictValue: vi.fn(),
  getClubs: vi.fn(),
  getModelMetrics: vi.fn(),
}));

function renderPage() {
  return render(
    <MemoryRouter>
      <Predictor />
    </MemoryRouter>
  );
}

beforeEach(() => {
  vi.clearAllMocks();
  getClubs.mockResolvedValue([{ id: 11, name: "Arsenal FC" }]);
  getModelMetrics.mockResolvedValue({
    model_name: "xgboost",
    validation: {},
    test: { MAE_eur: 4_708_641, RMSE_eur: 9_436_580, R2: 0.73, MAPE: 0.65 },
  });
  predictValue.mockResolvedValue({
    predicted_value_eur: 28_500_000,
    model_used: "xgboost",
    important_factors: ["appearances", "club_prestige_log", "goals"],
    disclaimer: "This is a statistical estimate...",
  });
});

describe("Predictor", () => {
  it("renders the form with sensible defaults", async () => {
    renderPage();
    expect(screen.getByRole("button", { name: /predict market value/i })).toBeInTheDocument();
    expect(screen.getByText(/goals\/90/i)).toBeInTheDocument();
    await screen.findByDisplayValue("League average");
  });

  it("submits the form and displays the predicted value", async () => {
    renderPage();
    await userEvent.click(screen.getByRole("button", { name: /predict market value/i }));

    expect(await screen.findByText("€28.5M")).toBeInTheDocument();
    expect(screen.getByText("xgboost")).toBeInTheDocument();
    expect(predictValue).toHaveBeenCalledWith(
      expect.objectContaining({ age: 24, sub_position: "Centre-Forward", foot: "right", league: "GB1" })
    );
  });

  it("shows the model's typical error range (MAE) alongside the result", async () => {
    renderPage();
    await userEvent.click(screen.getByRole("button", { name: /predict market value/i }));
    expect(await screen.findByText(/typical prediction error/i)).toBeInTheDocument();
    expect(screen.getByText(/€4.7M/)).toBeInTheDocument();
  });

  it("includes the disclaimer in the result card", async () => {
    renderPage();
    await userEvent.click(screen.getByRole("button", { name: /predict market value/i }));
    expect(await screen.findByText("This is a statistical estimate...")).toBeInTheDocument();
  });

  it("omits club_id from the payload when left as league average", async () => {
    renderPage();
    await userEvent.click(screen.getByRole("button", { name: /predict market value/i }));
    await waitFor(() => expect(predictValue).toHaveBeenCalled());
    const payload = predictValue.mock.calls[0][0];
    expect(payload).not.toHaveProperty("club_id");
    expect(payload).not.toHaveProperty("height_in_cm");
  });

  it("includes club_id in the payload once a club is selected", async () => {
    renderPage();
    const clubSelect = await screen.findByDisplayValue("League average");
    await userEvent.selectOptions(clubSelect, "Arsenal FC");
    await userEvent.click(screen.getByRole("button", { name: /predict market value/i }));

    await waitFor(() => expect(predictValue).toHaveBeenCalled());
    const payload = predictValue.mock.calls[0][0];
    expect(payload.club_id).toBe(11);
  });

  it("shows an error state when the API call fails", async () => {
    predictValue.mockRejectedValue({ message: "Request failed" });
    renderPage();
    await userEvent.click(screen.getByRole("button", { name: /predict market value/i }));
    expect(await screen.findByText("Request failed")).toBeInTheDocument();
  });

  it("updates goals/90 preview as goals are edited", async () => {
    renderPage();
    const goalsInput = screen.getByLabelText(/^goals$/i);
    await userEvent.clear(goalsInput);
    await userEvent.type(goalsInput, "20");
    // 20 goals / 2400 minutes * 90 = 0.75
    expect(await screen.findByText(/goals\/90: 0\.75/i)).toBeInTheDocument();
  });
});
