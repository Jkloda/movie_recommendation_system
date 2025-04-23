import { useState, useEffect } from "react";
import "../styles/SemanticSearchBar.css";
const API_KEY = process.env.REACT_APP_TMDB_API_KEY;
const TMDB_IMAGE_BASE_URL = process.env.REACT_APP_TMDB_IMAGE_BASE_URL;

export function SemanticSearchBar() {
  const [genre, setGenre] = useState(""); // State for the genre
  const [query, setQuery] = useState(""); // State for the query
  const [movies, setMovies] = useState([]); // State for the search results
  const [isLoading, setIsLoading] = useState(false); // State for loading status
  const [error, setError] = useState(null); // State for error handling
  const [formattedMovies, setFormattedMovies] = useState([]);
  const [posters, setPosters] = useState([]);
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
<<<<<<< HEAD
        splitArray = movies[0].split("]  [");
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
=======
        splitArray = movies[0].split(",");
        let formattedMovies = splitArray.map((movie) => {
          return movie.trim();
        });
        setFormattedMovies(formattedMovies);
        console.log(formattedMovies);
>>>>>>> f017095f298fb2367f5d5e0358293c38b11486bd
      }
    })();
  }, [movies]);

  useEffect(() => {
    async function fetchPosters() {
      let moviePosters = await Promise.all(
        formattedMovies.map(async (movie) => {
          let path = await fetchMoviePoster(movie);
          return path;
        })
      );
      setPosters(moviePosters);
    }
    fetchPosters();
  }, [formattedMovies]);

  const fetchMoviePoster = async (title) => {
    try {
      const res = await fetch(
        `https://api.themoviedb.org/3/search/movie?api_key=${API_KEY}&query=${title}`
      );
      const data = await res.json();
      return data.results?.[0]?.poster_path || null;
    } catch (error) {
      console.error("Error fetching poster:", error);
      return null;
    }
  };

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
        {formattedMovies.length > 0 ? (
          <div className="movie-results">
            {formattedMovies.map((movie, index) => {
              const poster = posters[index];
              if (poster === null) return null;
              let path = `https://image.tmdb.org/t/p/w500${poster}`;
              console.log(path);
              return (
                <div key={`movie_${index}`} className="movie-card">
                  <p>{movie}</p>
                  <img
                    src={posters[index] != null ? path : null}
                    alt={movie.title}
                    className="movie-img"
                  />
                </div>
              );
            })}
          </div>
        ) : isLoading ? (
          <p>Loading...</p>
        ) : (
          <p>No results found.</p>
        )}
      </div>
    </div>
  );
}
