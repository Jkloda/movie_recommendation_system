import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./Login.css";

export function Login({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [result, setResult] = useState("");
  const [show, setShow] = useState(true);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const url = "https://127.0.0.1:443/login";
    let response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      const errorDetails = await response.json();
      throw new Error(errorDetails.message || "Failed to login");
    }

    const jsonRes = await response.json();
    setResult(jsonRes);
    setShow(!show);
    onLogin?.(); // call it if it exists

    // Redirect to /search
    setTimeout(() => navigate("/homepage"), 1000);
  };

  return (
    <>
      <div
        style={{
          display: show ? "block" : "none",
        }}
      >
        <div className="login-container">
          <h1 className="login-title">Login</h1>
          <form className="login-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <input
                type="text"
                name="email"
                placeholder="Username"
                id="email"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="input-field"
              />
            </div>
            <div className="form-group">
              <input
                type="password"
                name="password"
                placeholder="Password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="input-field"
              />
            </div>
            <button type="submit" className="login-button">
              Login
            </button>
          </form>

          <h3>Or</h3>

          <a className="button" href="https://127.0.0.1:443/google-login">
            Google Login
          </a>
          <footer className="login-footer">
            <p>
              Not a member?{" "}
              <Link to="/SignUp" className="signup-link">
                Sign up
              </Link>
            </p>
            <p>
              Forgot your password?{" "}
              <Link to="/reset" className="reset-link">
                Reset
              </Link>
            </p>
          </footer>
        </div>
      </div>
    </>
  );
}
