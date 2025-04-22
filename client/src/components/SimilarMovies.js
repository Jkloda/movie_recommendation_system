import { useEffect, useState } from "react";

export const SimilarMovies = () => {
  const [favourites, setFavourites] = useState([]);
  const [similarMovies, setSimilarMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchFavourites = async () => {
      try {
        const response = await fetch(
          "https://127.0.0.1:443/api/get-favourites",
          {
            method: "GET",
            credentials: "include",
          }
        );

        if (!response.ok) {
          throw new Error("Failed to fetch favourites");
        }

        const json = await response.json();
        setFavourites(json.movies);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchFavourites();
  }, []);

  // Step 2: Fetch similar movies
  useEffect(() => {
    const fetchSimilar = async () => {
      if (favourites.length === 0) return;

      try {
        const response = await fetch(
          "https://127.0.0.1:443/api/get-similar-movies",
          {
            method: "POST",
            credentials: "include",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ movie_id: favourites[0].id }),
          }
        );

        if (!response.ok) {
          throw new Error("Failed to fetch similar movies");
        }

        const json = await response.json();
        setSimilarMovies(json.similar_movies);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchSimilar();
  }, [favourites]);

  // Render
  return (
    <div style={{ marginTop: "30px" }}>
      <h2>Movies for you based on your favourites</h2>
      {loading && <p>Loading similar movies...</p>}
      {error && <p style={{ color: "red" }}>Error: {error}</p>}
      {!loading && similarMovies.length === 0 && (
        <p>
          Add your favourite movies to see suggestions based on your favourites.
        </p>
      )}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(150px, 1fr))",
          gap: "15px",
        }}
      >
        {similarMovies.map((movie) => (
          <div
            key={movie.id}
            style={{
              padding: "10px",
              border: "1px solid #ccc",
              borderRadius: "8px",
            }}
          >
            <p>{movie.title}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
