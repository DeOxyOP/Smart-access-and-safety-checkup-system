import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/styles.css"; // Import a CSS file for styling

const ForgotPassword = () => {
    const [email, setEmail] = useState("");
    const [errorMessage, setErrorMessage] = useState("");
    const [successMessage, setSuccessMessage] = useState("");
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Validate email format
        if (!email.includes("@")) {
            setErrorMessage("Please enter a valid email address.");
            return;
        }

        try {
            const response = await fetch("http://127.0.0.1:8000/api/admin/forgot-password", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ email }),
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || "Something went wrong");
            }

            setSuccessMessage(data.message); // Display success message
            setErrorMessage(""); // Clear error message if successful
            setTimeout(() => {
                navigate("/login"); // Redirect to login after success
            }, 3000);
        } catch (error) {
            setErrorMessage(error.message || "Something went wrong!");
        }
    };

    return (
        <div>
            <h2>Forgot Password</h2>
            {errorMessage && <p style={{ color: "red" }}>{errorMessage}</p>}
            {successMessage && <p style={{ color: "green" }}>{successMessage}</p>}

            <form onSubmit={handleSubmit}>
                <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Enter your email"
                    required
                />
                <button type="submit">Submit</button>
            </form>
        </div>
    );
};

export default ForgotPassword;
