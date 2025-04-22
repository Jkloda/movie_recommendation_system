import React from "react";
import { Navbar } from "../components/Navbar.js";
import { SemanticSearchBar } from "../components/SemanticSearchBar.js";
import { PopularMovies } from "../components/PopularMovies.js";
import { SimilarMovies } from "../components/SimilarMovies.js";
export function HomePage() {
  return (
    <>
      <Navbar />
      <SemanticSearchBar />
      <SimilarMovies />
      <div>
        <PopularMovies />
      </div>
    </>
  );
}
