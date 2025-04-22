import { useState, useEffect, useRef } from "react";
import heart_selected from "./assets/heart_selected.png";
import heart_deselected from "./assets/heart_deselected.png";
import "./styles/Searchbar.css";

const API_KEY = process.env.REACT_APP_TMDB_API_KEY;
const TMDB_IMAGE_BASE_URL = process.env.REACT_APP_TMDB_IMAGE_BASE_URL;

export function Searchbar() {
  const [formData, setFormData] = useState("");
  const [movies, setMovies] = useState([]);
  const [limit, setLimit] = useState(0);
  const [favourites, setFavourites] = useState([]);
  const [likeButton, setLikeButton] = useState([]);
  const [movieUpdate, setMovieUpdate] = useState(true);
  const scrollRef = useRef(null);
  useEffect(() => {
    if (movies && favourites.length > 0) {
      const unpacked = favourites.map((fav) => fav.id || fav);
      setFavourites(unpacked);
    }
  }, [movies]);

  useEffect(() => {
    const favStates = movies.map((movie) => favourites.includes(movie.id));
    setLikeButton(favStates);
  }, [favourites, movies]);

  const handleChange = (e) => {
    setFormData(e.target.value);
    setMovies([]);
    setLimit(0);
  };

  const handleClick = (title, index) => {
    const url = likeButton[index]
      ? "https://127.0.0.1:443/api/delete-favourite"
      : "https://127.0.0.1:443/api/add-favourite";

    fetch(url, {
      method: likeButton[index] ? "DELETE" : "POST",
      body: JSON.stringify({ title }),
      headers: { "Content-Type": "application/json" },
      credentials: "include",
    });

    setLikeButton((prev) => {
      const updated = [...prev];
      updated[index] = !updated[index];
      return updated;
    });
  };

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

  const handleSubmit = async (e) => {
    e.preventDefault();
    const uri = encodeURI(
      `https://127.0.0.1:443/api/get-movies?limit=${limit}&query=${formData}`
    );

    try {
      const res = await fetch(uri, {
        method: "GET",
        credentials: "include",
        headers: { "Content-Type": "html/text" },
      });
      const json = await res.json();
      setLimit(json.limit);
      setMovies(json.movies);
      setFavourites(json.favourites || []);
      setMovieUpdate((prev) => !prev);
    } catch {
      alert("Something went wrong. Please refresh or login.");
    }
  };

  useEffect(() => {
    const fetchPosters = async () => {
      const updated = await Promise.all(
        movies.map(async (movie) => {
          const poster = await fetchMoviePoster(movie.title);
          return { ...movie, poster_path: poster };
        })
      );
      setMovies(updated);
    };

    if (movies.length > 0) fetchPosters();
  }, [movieUpdate]);

  const scroll = (direction) => {
    const scrollAmount = 300;
    if (direction === "left") {
      scrollRef.current.scrollLeft -= scrollAmount;
    } else {
      scrollRef.current.scrollLeft += scrollAmount;
    }
  };

  return (
    <div className="search-container">
      <form onSubmit={handleSubmit}>
        <h1 className="search-title">Add movie to your favourites</h1>
        <input
          className="search-input"
          placeholder="Search for movies"
          type="text"
          onChange={handleChange}
          name="searchTerms"
          value={formData}
        />
      </form>

      {movies.length > 0 && (
        <div className="scroll-wrapper">
          <button className="scroll-btn left" onClick={() => scroll("left")}>
            ◀
          </button>

          <div className="movie-row-container" ref={scrollRef}>
            {movies.map((movie, index) => {
              const posterUrl = movie.poster_path
                ? `${TMDB_IMAGE_BASE_URL}${movie.poster_path}`
                : null;

              return (
                <div key={`mov-${index}`} className="movie-card">
                  {posterUrl ? (
                    <img
                      src={posterUrl}
                      alt={movie.title}
                      className="movie-img"
                    />
                  ) : (
                    <p>No poster available</p>
                  )}
                  <h4 className="movie-title">{movie.title}</h4>
                  <div
                    onClick={() => handleClick(movie.title, index)}
                    className="heart-icon"
                  >
                    <img
                      src={
                        likeButton[index] ? heart_selected : heart_deselected
                      }
                      width={25}
                      alt="heart icon"
                    />
                  </div>
                </div>
              );
            })}
          </div>

          <button className="scroll-btn right" onClick={() => scroll("right")}>
            ▶
          </button>
        </div>
      )}
    </div>
  );
}
