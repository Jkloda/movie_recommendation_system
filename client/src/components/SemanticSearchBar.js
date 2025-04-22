import { useState, useEffect } from "react";
import "../styles/SemanticSearchBar.css";

export function SemanticSearchBar() {
  const [genre, setGenre] = useState(""); // State for the genre
  const [query, setQuery] = useState(""); // State for the query
  const [movies, setMovies] = useState([]); // State for the search results
  const [isLoading, setIsLoading] = useState(false); // State for loading status
  const [error, setError] = useState(null); // State for error handling
  const [formattedMovies, setFormattedMovies] = useState([]);

  // Handle form submission
  const handleSearch = async (event) => {
    event.preventDefault();

    if (!genre && !query) {
      setError("Please provide a genre or query.");
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      const response = await fetch("https://127.0.0.1:443/api/search", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          genre: genre,
          search: query,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.message || data.error || "Failed to fetch results"
        );
      }

      setMovies(data.movies || "");
    } catch (err) {
      setError(err.message);
      setMovies([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    (async function formatMovies() {
      let splitArray;
      let moviesArray;
      if (movies.length > 0) {
        splitArray = movies.split("]  [");
        let lastIndex = splitArray.length - 1;

        splitArray[0] = await splitArray[0].slice(1, splitArray[0].length - 1);

        splitArray[lastIndex] = await splitArray[lastIndex].slice(
          splitArray[lastIndex][0],
          splitArray[lastIndex].length - 1
        );
        moviesArray = await splitArray.map((movie) => {
          return movie.split("§ ");
        });
        setFormattedMovies(moviesArray);
        console.log(moviesArray);
      }
      console.log(splitArray);
    })();
  }, [movies]);

  return (
    <div className="semantic-search-container">
      <form onSubmit={handleSearch} role="search">
        <label htmlFor="genre-search">Search by Genre</label>
        <input
          id="genre-search"
          type="text"
          value={genre}
          onChange={(e) => setGenre(e.target.value)}
          placeholder="Enter genre (e.g., Action, Comedy)"
          aria-label="Genre search"
        />

        <label htmlFor="query-search">Search by Plot/Description</label>
        <input
          id="query-search"
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter plot, keywords, or description"
          aria-label="Query search"
        />

        <button type="submit" disabled={isLoading}>
          {isLoading ? "Searching..." : "Search"}
        </button>
      </form>

      {error && <div className="error-message">{error}</div>}

      <div className="search-results">
        {movies && typeof movies === "string" ? (
          <p>{movies}</p>
        ) : (
          <p>No results found.</p>
        )}
      </div>
    </div>
  );
}
