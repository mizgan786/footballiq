import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { LoadingState, ErrorState, EmptyState } from "./StatusStates";

describe("LoadingState", () => {
  it("renders default label", () => {
    render(<LoadingState />);
    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("renders a custom label", () => {
    render(<LoadingState label="Searching players..." />);
    expect(screen.getByText("Searching players...")).toBeInTheDocument();
  });
});

describe("ErrorState", () => {
  it("renders the error message", () => {
    render(<ErrorState message="Network request failed" />);
    expect(screen.getByText("Network request failed")).toBeInTheDocument();
  });

  it("shows a retry button only when onRetry is provided, and calls it on click", async () => {
    const onRetry = vi.fn();
    render(<ErrorState message="failed" onRetry={onRetry} />);
    const button = screen.getByRole("button", { name: /try again/i });
    await userEvent.click(button);
    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it("omits the retry button when onRetry is not provided", () => {
    render(<ErrorState message="failed" />);
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });
});

describe("EmptyState", () => {
  it("renders title and optional hint", () => {
    render(<EmptyState title="No players match" hint="Try widening the filters" />);
    expect(screen.getByText("No players match")).toBeInTheDocument();
    expect(screen.getByText("Try widening the filters")).toBeInTheDocument();
  });
});
