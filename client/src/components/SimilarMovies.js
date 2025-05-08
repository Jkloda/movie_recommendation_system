import React, { useEffect, useState, useRef } from "react";
import "../styles/SimilarMovies.css";
const API_KEY = process.env.REACT_APP_TMDB_API_KEY;

export const SimilarMovies = () => {
  const [favourites, setFavourites] = useState([]);
  const [similarMovies, setSimilarMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [posters, setPosters] = useState();
  const scrollRef = useRef(null);

  const scroll = (direction) => {
    const { current } = scrollRef;
    if (current) {
      const scrollAmount = 300;
      current.scrollBy({
        left: direction === "left" ? -scrollAmount : scrollAmount,
        behavior: "smooth",
      });
    }
  };

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

  return (
    <div className="similar-movies-container">
      <h2 className="similar-movies-header">
        Sugessted for you based on favourites
      </h2>
      {loading && <p className="loading-message">Loading similar movies...</p>}
      {error && <p className="error-message">Error: {error}</p>}
      {!loading && similarMovies.length === 0 && (
        <p className="empty-message">
          Add your favourite movies to see suggestions based on your
          favourites.
        </p>
      )}
      {!loading && similarMovies.length > 0 && posters && (
        <div className="similar-movies-wrapper">
          <button className="scroll-button left" onClick={() => scroll("left")}>
            &#8249;
          </button>
          <ul className="movie-list" ref={scrollRef}>
            {similarMovies.map((movie, index) => {
              const poster = posters[index];
              if (poster === null) return null;
              let path = `https://image.tmdb.org/t/p/w500${poster}`;
              return (
                <li className="movie-card" key={movie.id}>
                  <img src={path} alt={movie.title} className="movie-img" />
                  <p className="movie-title">{movie.title}</p>
                </li>
              );
            })}
          </ul>
          <button
            className="scroll-button right"
            onClick={() => scroll("right")}
          >
            &#8250;
          </button>
        </div>
      )}
    </div>
  );
};