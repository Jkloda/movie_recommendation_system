import { render, screen, fireEvent } from "@testing-library/react";
import SemanticSearchBar from "../components/SemanticSearchBar";
import "@testing-library/jest-dom";

describe("SemanticSearchBar", () => {
  test("renders search bar and input field", () => {
    render(<SemanticSearchBar />);

    expect(screen.getByPlaceholderText(/search by/i)).toBeInTheDocument();
  });

  test("filters movies based on name", () => {
    render(<SemanticSearchBar />);

    const input = screen.getByPlaceholderText(/search by name/i);
    fireEvent.change(input, { target: { value: "Inception" } });

    expect(screen.getByText("Inception")).toBeInTheDocument();
    expect(screen.queryByText("The Dark Knight")).not.toBeInTheDocument();
  });

  test("filters movies based on genre", () => {
    render(<SemanticSearchBar />);

    const select = screen.getByRole("combobox");
    fireEvent.change(select, { target: { value: "genre" } });

    const input = screen.getByPlaceholderText(/search by genre/i);
    fireEvent.change(input, { target: { value: "Sci-Fi" } });

    expect(screen.getByText("Inception")).toBeInTheDocument();
    expect(screen.getByText("Interstellar")).toBeInTheDocument();
    expect(screen.queryByText("The Dark Knight")).not.toBeInTheDocument();
  });
});
