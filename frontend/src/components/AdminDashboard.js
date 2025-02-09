import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import AddCamera from "./AddCamera";
import "../styles/AdminDashboard.css";

const AdminDashboard = () => {
  const [admin, setAdmin] = useState(null);
  const [activeTab, setActiveTab] = useState("welcome");
  const [cameras, setCameras] = useState([]); // Store cameras
  const navigate = useNavigate();

  useEffect(() => {
    const storedAdmin = localStorage.getItem("admin");
    if (storedAdmin) {
      setAdmin(JSON.parse(storedAdmin));
    } else {
      navigate("/login");
    }
  }, [navigate]);

  // Fetch cameras from FastAPI
  const fetchCameras = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/api/get-cameras/");
      const data = await response.json();

      if (response.ok) {
        setCameras(Array.isArray(data) ? data : data.cameras || []);
      } else {
        console.error("Error fetching cameras:", data.message);
      }
    } catch (error) {
      console.error("Failed to fetch cameras:", error);
    }
  };

  useEffect(() => {
    fetchCameras(); // Fetch cameras when the component mounts
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("admin");
    navigate("/");
  };

  const handleViewCamera = (cameraId) => {
    navigate(`/view-camera/${cameraId}`);
  };

  return (
    <div className="dashboard-container">
      <div className="sidebar">
        <h3>Admin Panel</h3>
        <button onClick={() => setActiveTab("add-camera")}>Add Camera</button>
        <button onClick={() => setActiveTab("view-camera")}>View Camera</button>
        <button onClick={() => setActiveTab("detection-logs")}>Detection Logs</button>
        <button onClick={handleLogout}>Logout</button>
      </div>

      <div className="content">
        {activeTab === "welcome" && <h2>Welcome Admin!</h2>}
        {activeTab === "add-camera" && <AddCamera setCameras={setCameras} />}
        {activeTab === "view-camera" && (
          <div>
            <h2>Available Cameras</h2>
            {cameras.length === 0 ? (
              <p>No cameras available.</p>
            ) : (
              <div className="camera-grid">
                {cameras.map((camera, index) => (
                  <div key={index} className="camera-card">
                    <div className="camera-icon">📷</div>
                    <h3>{camera.camera_name}</h3>
                    <p>📍 {camera.location}</p>
                    <button onClick={() => handleViewCamera(camera.camera_id)}>View Camera</button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
        {activeTab === "detection-logs" && <h2>Detection Logs Page</h2>}
      </div>
    </div>
  );
};

export default AdminDashboard;
