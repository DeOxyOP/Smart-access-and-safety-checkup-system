import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const ResetPassword = () => {
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (newPassword !== confirmPassword) {
            setErrorMessage('Passwords do not match');
            return;
        }

        // Extract token from the URL query string
        const urlParams = new URLSearchParams(window.location.search);
        const token = urlParams.get('token');  // Get token from reset link

        if (!token) {
            setErrorMessage('Invalid or missing token. Please request a new reset link.');
            return;
        }

        try {
            const response = await fetch(`http://127.0.0.1:8000/api/admin/reset-password?token=${token}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ new_password: newPassword }),
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || "Something went wrong");
            }

            alert(data.message);  // Show success message
            navigate("/");   // Redirect to login after successful reset
        } catch (error) {
            setErrorMessage("Error: " + error.message);
        }
    };

    return (
        <div>
            <h2>Reset Your Password</h2>
            {errorMessage && <p style={{ color: "red" }}>{errorMessage}</p>}
            <form onSubmit={handleSubmit}>
                <input
                    type="password"
                    placeholder="New Password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    required
                />
                <input
                    type="password"
                    placeholder="Confirm New Password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                />
                <button type="submit">Reset Password</button>
            </form>
        </div>
    );
};

export default ResetPassword;
