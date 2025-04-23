import { useEffect, useState } from "react";

const API_KEY = process.env.REACT_APP_TMDB_API_KEY;
export const SimilarMovies = () => {
  const [favourites, setFavourites] = useState([]);
  const [similarMovies, setSimilarMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [posters, setPosters] = useState();

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

  useEffect(() => {
    async function fetchPosters() {
      const moviePosters = await Promise.all(
        similarMovies.map(async (movie) => {
          let path = await fetchMoviePoster(movie.title);
          return path;
        })
      );
      return moviePosters;
    }
    async function beginFetching() {
      let poster = await fetchPosters();
      setPosters(poster);
    }
    beginFetching();
  }, [similarMovies]);

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
        {posters
          ? similarMovies.map((movie, index) => {
              const poster = posters[index];
              console.log("poster ", poster);
              if (poster === null) return null;
              let path = `https://image.tmdb.org/t/p/w500${poster}`;
              return (
                <div
                  key={movie.id}
                  style={{
                    padding: "10px",
                    border: "1px solid #ccc",
                    borderRadius: "8px",
                  }}
                >
                  <p>{movie.title}</p>
                  <img src={path} alt={movie.title} className="movie-img" />
                </div>
              );
            })
          : null}
      </div>
    </div>
  );
};
