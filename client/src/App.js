import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useState } from "react";
import { Login } from "./components/Login.js";
import { Registration } from "./components/Registration.js";
import { Searchbar } from "./searchbar.js";
import { Profile } from "./components/profile/Profile.js";
import { SemanticSearchBar } from "./components/SemanticSearchBar.js";
import { HomePage } from "./pages/HomePage.js";
import { PopularMovies } from "./components/PopularMovies.js";

const PrivateRoute = ({ isAuthenticated, children }) => {
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

export function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/login"
          element={<Login onLogin={() => setIsAuthenticated(true)} />}
        />
        <Route
          path="/SignUp"
          element={<Registration setIsAuthenticated={setIsAuthenticated} />}
        />
        <Route
          path="/Homepage"
          element={
            <PrivateRoute isAuthenticated={isAuthenticated}>
              <HomePage />
            </PrivateRoute>
          }
        />
        <Route
          path="/search"
          element={
            <PrivateRoute isAuthenticated={isAuthenticated}>
              <Searchbar />
            </PrivateRoute>
          }
        />{" "}
        <Route
          path="/popularmovies"
          element={
            <PrivateRoute isAuthenticated={isAuthenticated}>
              <PopularMovies />
            </PrivateRoute>
          }
        />
        <Route
          path="/semanticsearch"
          element={
            <PrivateRoute isAuthenticated={isAuthenticated}>
              <SemanticSearchBar />
            </PrivateRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <PrivateRoute isAuthenticated={isAuthenticated}>
              <Profile />
            </PrivateRoute>
          }
        />
        {/* Redirect all unknown paths to login */}
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    </BrowserRouter>
  );
}
