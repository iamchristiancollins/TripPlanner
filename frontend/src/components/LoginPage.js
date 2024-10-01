// src/pages/LoginPage.js
import React, { useState } from "react";
import axios from "axios";

const LoginPage = ({ history }) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  // ... Handle form submission and authentication

  const handleSubmit = (e) => {
    e.preventDefault();
    axios
      .post("http://localhost:5001/api/auth/login", { username, password })
      .then((response) => {
        // Save token to localStorage or context
        localStorage.setItem("token", response.data.token);
        // Redirect to main page
        history.push("/main");
      })
      .catch((error) => {
        console.error("Error logging in:", error);
        // Handle error (e.g., display error message)
      });
  };

  return (
    <div>
      <h2>Sign In</h2>
      <form onSubmit={handleSubmit}>
        {/* Input fields for username and password */}
        <input
          type="text"
          name="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        {/* ... Other form fields */}
        <button type="submit">Sign in</button>
      </form>
    </div>
  );
};

export default LoginPage;
