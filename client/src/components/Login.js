import React, { useState } from "react";
import { Link } from "react-router-dom";
import { loginUser } from "./LoginService";
import "./Login.css";

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [result, setResult] = useState("");
  const [show, setShow] = useState(true);

  const handleSubmit = async (e) => {
    e.preventDefault();
    let loginResult = await loginUser({ username, password });
    setShow(!setShow);
    setResult(loginResult);
  };

  return (
      <>
          <div style={{
            display: show?"block":"none"
          }}>
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
              <br/>
              <h3>Or</h3>
              <br/>
              <a class="button" href="https://127.0.0.1:443/google-login">Google Login</a>
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
          <div style={{
            display: show?"none":"block"
          }}
            className="success"
          >
            <h3
              style={{
                display: "grid",
                justifyContent: "center",
                alignContent: "center"
              }}
            >{result.message}</h3>
            <h2
              style={{
                display: "grid",
                justifyContent: "center",
                alignContent: "center"
              }}
            >{result.username}</h2>
          </div>
      </>
  );
};

export default Login;
