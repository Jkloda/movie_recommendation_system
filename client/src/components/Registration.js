import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./Registration.css";

export const Registration = function ({ setIsAuthenticated }) {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [dataInput, setDataInput] = useState(null);
  const [errors, setErrors] = useState({}); // To store form validation errors

  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();

    // Basic validation
    let formErrors = {};
    if (!fullName) formErrors.fullName = "Full name is required";
    if (!email) formErrors.email = "Email is required";
    else if (!/\S+@\S+\.\S+/.test(email)) formErrors.email = "Email is invalid";
    if (!password) formErrors.password = "Password is required";

    if (Object.keys(formErrors).length > 0) {
      setErrors(formErrors);
      return;
    }

    // If no errors, save data
    const info = { fullName, email, password };
    setDataInput(info);

    // Reset the form fields after submission
    setFullName("");
    setEmail("");
    setPassword("");
    setErrors({});

    // Set user as authenticated after successful registration
    setIsAuthenticated(true);

    navigate("/Homepage");
  };

  const handleFullNameChange = (e) => {
    setFullName(e.target.value);
  };

  const handleEmailChange = (e) => {
    setEmail(e.target.value);
  };

  const handlePasswordChange = (e) => {
    setPassword(e.target.value);
  };

  return (
    <div className="signup-container">
      <h2>Sign Up</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="fullName">Full Name</label>
          <input
            type="text"
            name="fullName"
            id="fullName"
            value={fullName}
            onChange={handleFullNameChange}
            required
          />
          {errors.fullName && <p className="error">{errors.fullName}</p>}
        </div>

        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input
            type="email"
            name="email"
            id="email"
            value={email}
            onChange={handleEmailChange}
            required
          />
          {errors.email && <p className="error">{errors.email}</p>}
        </div>

        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            type="password"
            name="password"
            id="password"
            value={password}
            onChange={handlePasswordChange}
            required
          />
          {errors.password && <p className="error">{errors.password}</p>}
        </div>

        <button type="submit">Sign up</button>
      </form>
      <footer>
        Already a member?{" "}
        <Link to="/Login" id="signup-link">
          Log in
        </Link>
        <div>
          <h1>Movie Finder</h1>
        </div>
      </footer>
    </div>
  );
};
