import React, { useState, useEffect, useRef } from "react";
import "../styles/PopularMovies.css";

export const PopularMovies = () => {
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const imageBaseUrl = process.env.REACT_APP_TMDB_IMAGE_BASE_URL;

  const scrollRef = useRef(null);

  useEffect(() => {
    const fetchMovies = async () => {
      try {
        const response = await fetch(
          "https://127.0.0.1:443/api/top-popular-movies",
          {
            method: "GET",
            credentials: "include",
          }
        );

        if (!response.ok) {
          throw new Error("Network response was not ok");
        }

        const data = await response.json();
        setMovies(data.top_10_popular_movies);
      } catch (err) {
        setError("Failed to fetch top movies.");
      } finally {
        setLoading(false);
      }
    };

    fetchMovies();
  }, []);

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

  if (loading) return <div className="movies-container">Loading...</div>;
  if (error) return <div className="movies-container">{error}</div>;

  return (
    <div className="movies-container">
      <h2 className="movies-header">Top Popular Movies</h2>

      <div className="movies-wrapper">
        <button className="scroll-button left" onClick={() => scroll("left")}>
          &#8249;
        </button>

        <ul className="movie-list" ref={scrollRef}>
          {movies.map(({ title, poster_path }, index) => (
            <div className="movie-card" key={index}>
              <img
                src={`${imageBaseUrl}${poster_path}`}
                alt={title}
                className="movie-img"
              />
              <p className="movie-title">{title}</p>
            </div>
          ))}
        </ul>

        <button className="scroll-button right" onClick={() => scroll("right")}>
          &#8250;
        </button>
      </div>
    </div>
  );
};
