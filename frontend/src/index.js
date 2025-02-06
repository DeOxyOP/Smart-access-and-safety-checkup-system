import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./components/Login";
import AdminDashboard from "./components/AdminDashboard";
import AddCamera from "./components/AddCamera";
import ViewCamera from "./components/ViewCamera";
import DetectionLogs from "./components/DetectionLogs";
import ForgotPassword from "./components/ForgotPassword";
import ResetPassword from "./components/ResetPassword"; // Ensure this is imported too

import "./styles/styles.css";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
    <React.StrictMode>
        <Router>
            <Routes>
                <Route path="/" element={<Login />} />
                <Route path="/admin-dashboard" element={<AdminDashboard />} />
                <Route path="/add-camera" element={<AddCamera />} />
                <Route path="/view-camera/:cameraId" element={<ViewCamera />} />  {/* Dynamic route */}
                <Route path="/detection-logs" element={<DetectionLogs />} />
                <Route path="/forgot-password" element={<ForgotPassword />} />
                <Route path="/reset-password" element={<ResetPassword />} />
            </Routes>
        </Router>
    </React.StrictMode>
);
