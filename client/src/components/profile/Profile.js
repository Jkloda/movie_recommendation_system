import { useEffect, useState, useRef } from "react";

const API_KEY = process.env.REACT_APP_TMDB_API_KEY;

export const Profile = () => {
  const [username, setUsername] = useState();
  const [email, setEmail] = useState();
  const [favourites, setFavourites] = useState();
  const [posters, setPosters] = useState();
  const scrollRef = useRef(null);
  const [filter, setFilter] = useState([]);

  const fetchMoviePoster = async ({ title }) => {
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
    (async function get_favourites() {
      const response = await fetch("https://127.0.0.1:443/api/get-favourites", {
        method: "GET",
        credentials: "include",
      });
      const jsonResponse = await response.json();
      setFavourites(jsonResponse.movies);
    })();
    (async function get_account() {
      const response = await fetch("https://127.0.0.1:443/api/get-account", {
        method: "GET",
        credentials: "include",
      });
      const jsonResponse = await response.json();
      setUsername(jsonResponse.account[1]);
      setEmail(jsonResponse.account[0]);
    })();
  }, []);

  useEffect(() => {
    if (favourites) {
      async function fetchPosters() {
        const moviePosters = await Promise.all(
          favourites.map(async (movie) => {
            let path = await fetchMoviePoster(movie);
            return path;
          })
        );
        return moviePosters;
      }
      async function beginFetching() {
        let posters = await fetchPosters();
        setPosters(posters);
      }
      beginFetching();
      let filterArray = Array(favourites.length);
      filterArray = filterArray.fill(false);
      setFilter(filterArray);
    }
  }, [favourites]);

  return (
    <>
      {
        <div>
          <div
            style={{
              display: "grid",
              gridTemplateRows: "1fr 1fr",
              margin: "2rem auto",
              textAlign: "center",
              gap: "2rem",
            }}
          >
            <h2>Username: {username ? username : null}</h2>
            <h2>Email: {email ? email : null}</h2>
          </div>
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              alignItems: "center",
              gap: "0rem",
            }}
          >
            <div
              style={{
                marginTop: "5rem",
              }}
            >
              <h2>Favourited movies</h2>
            </div>
            <div
              className="movies-wrapper"
              style={{
                height: "400px",
                width: "1200px",
                margin: "0 auto",
              }}
            >
              <button
                className="scroll-button left"
                onClick={() => scroll("left")}
                alignSelf="center"
              >
                &#8249;
              </button>

              <ul
                className="movie-list"
                ref={scrollRef}
                style={{
                  overflowY: "hidden",
                  overflowX: "hidden",
                }}
              >
                {posters
                  ? posters.map((poster, index) => {
                      return (
                        <div
                          style={{
                            transition: "filter 0.3s ease-in-out",
                            filter: filter[index]
                              ? "grayscale(100%)"
                              : "grayscale(0%)",
                          }}
                          onMouseEnter={() => {
                            let newFilterArray = [...filter];
                            newFilterArray[index] = true;
                            setFilter(newFilterArray);
                          }}
                          onMouseLeave={() => {
                            let newFilterArray = [...filter];
                            newFilterArray[index] = false;
                            setFilter(newFilterArray);
                          }}
                          onClick={() => {
                            let newFavouritesArray = [...favourites];
                            let newFilterArray = [...filter];
                            let newPostersArray = [...posters];
                            newPostersArray.splice(index, 1);
                            newFavouritesArray.splice(index, 1);
                            newFilterArray.splice(index, 1);
                            setFavourites(newFavouritesArray);
                            setFilter(newFilterArray);
                            fetch(
                              "https://127.0.0.1:443/api/delete-favourite",
                              {
                                method: "DELETE",
                                credentials: "include",
                                headers: {
                                  "Content-Type": "application/json",
                                },
                                body: JSON.stringify({
                                  title: favourites[index].title,
                                }),
                              }
                            );
                          }}
                          key={`movie_${index}`}
                        >
                          <img
                            src={`https://image.tmdb.org/t/p/w500${poster}`}
                            className="movie-img"
                            style={{
                              width: "200px",
                            }}
                          />
                        </div>
                      );
                    })
                  : null}
              </ul>

              <button
                className="scroll-button right"
                onClick={() => scroll("right")}
              >
                &#8250;
              </button>
            </div>
          </div>
        </div>
      }
    </>
  );
};
