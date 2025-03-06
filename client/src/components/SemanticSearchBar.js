import { useState } from "react";

const SearchBar = ({ items, onSearch }) => {
  const [queryText, setQueryText] = useState("");
  const [searchCategory, setSearchCategory] = useState("name");

  const handleSearchResult = (event) => {
    try {
      const query = event.target.value.toLowerCase();
      setQueryText(query);

      const filteredItems = items.filter((item) => {
        switch (searchCategory) {
          case "name":
            return item.name.toLowerCase().includes(query);
          case "genre":
            return item.genres.some((genre) =>
              genre.toLowerCase().includes(query)
            );
          default:
            throw new Error("Invalid search category");
        }
      });

      onSearch(filteredItems);
    } catch (error) {
      console.error("No result", error);
    }
  };

  return (
    <div className="search-bar">
      <div className="search-controls">
        <select
          value={searchCategory}
          onChange={(e) => setSearchCategory(e.target.value)}
          className="search-select"
        >
          <option value="name">Name</option>
          <option value="genre">Genre</option>
        </select>
        <input
          type="text"
          placeholder={`Search by ${searchCategory}...`}
          value={queryText}
          onChange={handleSearchResult}
          className="search-input"
        />
      </div>
    </div>
  );
};

// Mockdata:
const SemanticSearchBar = () => {
  const [filteredMovies, setFilteredMovies] = useState([]);

  const Mockmovies = [
    { id: 1, name: "Inception", genres: ["Action", "Sci-Fi"] },
    { id: 2, name: "The Dark Knight", genres: ["Action", "Drama"] },
    { id: 3, name: "Interstellar", genres: ["Adventure", "Sci-Fi"] },
  ];

  return (
    <div>
      <h1>Movie Search</h1>
      <SearchBar items={Mockmovies} onSearch={setFilteredMovies} />

      <div className="results">
        {filteredMovies.map((movie) => (
          <div key={movie.id} className="movie-card">
            <h3>{movie.name}</h3>
            <p>Genres: {movie.genres.join(", ")}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
export default SemanticSearchBar;
