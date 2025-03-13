import React, { useState } from "react";
import axios from "axios";

export const SemanticSearchBar = () => {
  const [query, setQuery] = useState("");
  const [searchType, setSearchType] = useState("name");
  const [results, setResults] = useState([]);
  const [error, setError] = useState("");

  // Handle user input changes
  const handleChange = (e) => {
    setQuery(e.target.value);
  };

  // Handle search type selection change
  const handleSearchTypeChange = async (e) => {
    setSearchType(e.target.value);
  };

  const handleSearch = async (e) => {
    e.preventDefault();

    if (!query) {
      return;
    }

    try {
      let response;

      if (searchType === "genre") {
        // Send request as genre
        response = await axios.post(
          "https://127.0.0.1:443/api/search/",
          JSON.stringify({
            genre: query,
          })
        );
      } else {
        //Send request as search query
        response = await axios.post(
          "https://127.0.0.1:443/api/search/",
          JSON.stringify({
            search: query,
          })
        );
      }

      setResults(response.data.results);
      setError("");
    } catch (err) {
      console.error("Search error:", err);
      setError("Failed to fetch results.");
    }
  };

  return (
    <div>
      <form onSubmit={handleSearch}>
        <div>
          <label htmlFor="search-type">Search By: </label>
          <select
            id="search-type"
            value={searchType}
            onChange={handleSearchTypeChange}
          >
            <option value="name">Name</option>
            <option value="genre">Genre</option>
          </select>
        </div>

        <input
          type="text"
          value={query}
          onChange={handleChange}
          placeholder={`Search by ${searchType === "genre" ? "genre" : "name"}`}
        />
        <button type="submit">Search</button>
      </form>

      {error && <p>{error}</p>}

      <div>
        <h3>Results:</h3>
        {results.length > 0 ? (
          <ul>
            {results.map((result) => (
              <li key={result.id}>
                {result.title} - {result.genre}
              </li>
            ))}
          </ul>
        ) : (
          <p>No results found.</p>
        )}
      </div>
    </div>
  );
};
