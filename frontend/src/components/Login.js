import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/styles.css"; 

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [isForgotPassword, setIsForgotPassword] = useState(false); 
  const [resetEmail, setResetEmail] = useState(""); 
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch("http://127.0.0.1:8000/api/admin/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Something went wrong");
      }

      // Store the admin information in localStorage
      localStorage.setItem("admin", JSON.stringify({ email })); 
      // alert(data.message); // Show the success message

      // Navigate to the dashboard
      navigate("/admin-dashboard");
    } catch (error) {
      setErrorMessage("Login failed: " + error.message);
    }
  };

  const handleForgotPasswordSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/admin/forgot-password",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: resetEmail }),
        }
      );
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Something went wrong");
      }
      alert(data.message); 
      setIsForgotPassword(false); 
    } catch (error) {
      setErrorMessage("Error: " + error.message);
    }
  };

  return (
    <div>
      <h2>Admin Login</h2>
      {errorMessage && <p style={{ color: "red" }}>{errorMessage}</p>}

      {isForgotPassword ? (
        <form onSubmit={handleForgotPasswordSubmit}>
          <input
            type="email"
            value={resetEmail}
            onChange={(e) => setResetEmail(e.target.value)}
            placeholder="Enter your email"
            required
          />
          <button type="submit">Submit</button>
          <button type="button" onClick={() => setIsForgotPassword(false)}>
            Back to Login
          </button>
        </form>
      ) : (
        <form onSubmit={handleSubmit}>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email"
            required
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            required
          />
          <button type="submit">Login</button>
          <p>
            <button type="button" onClick={() => setIsForgotPassword(true)}>
              Forgot Password?
            </button>
          </p>
        </form>
      )}
    </div>
  );
};

export default Login;




