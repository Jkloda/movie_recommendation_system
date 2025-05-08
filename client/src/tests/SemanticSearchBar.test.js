import React from 'react';
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { SemanticSearchBar } from "../components/SemanticSearchBar";
import "@testing-library/jest-dom";

global.fetch = jest.fn();

describe("SemanticSearchBar", () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test("renders search bar and input field", () => {
    render(<SemanticSearchBar />);
    expect(screen.getByLabelText(/Search by Genre/i)).toBeInTheDocument();
  });

  test('shows error message when both inputs are empty and form is submitted', async () => {
    render(<SemanticSearchBar />);
    fireEvent.click(screen.getByRole('button', { name: /Search/i }));
    expect(await screen.findByText(/Please provide a genre or query/i)).toBeInTheDocument();
  });
  
  test("display movie titles", async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ movies: ["Inception"] }),
    });

    render(<SemanticSearchBar />);

    fireEvent.change(screen.getByLabelText(/Plot\/Description/i), {
      target: { value: "sci-fi action" },
    });

    fireEvent.click(screen.getByRole("button", { name: /search/i }));

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(1);
    });

    expect(screen.getByText("Inception")).toBeInTheDocument();
  });
});