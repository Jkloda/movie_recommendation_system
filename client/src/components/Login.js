import React, { useState } from "react";
import { Link } from "react-router-dom";
import { loginUser } from "./LoginService";
import "./Login.css";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    await loginUser({ email, password });
  };

  return (
    <div className="login-container">
      <h1 className="login-title">Login</h1>
      <form className="login-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <input
            type="email"
            name="email"
            placeholder="Email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
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
  );
};

export default Login;
