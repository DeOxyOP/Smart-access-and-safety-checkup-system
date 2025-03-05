import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import AddCamera from "./AddCamera";
import "../styles/AdminDashboard.css";

const AdminDashboard = () => {
  const [admin, setAdmin] = useState(null);
  const [activeTab, setActiveTab] = useState("welcome");
  const [cameras, setCameras] = useState([]);
  const [detectionLogs, setDetectionLogs] = useState([]); 
  const navigate = useNavigate();

  useEffect(() => {
    const storedAdmin = localStorage.getItem("admin");
    if (storedAdmin) {
      setAdmin(JSON.parse(storedAdmin));
    } else {
      navigate("/login");
    }
  }, [navigate]);

  useEffect(() => {
    window.history.pushState(null, "", window.location.href);
    window.onpopstate = () => {
      window.history.pushState(null, "", window.location.href);
    };
  }, []);
  
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
// Fetch detection logs from FastAPI
const fetchDetectionLogs = async () => {
  try {
    const response = await fetch("http://127.0.0.1:8000/api/get-detection-logs/");
    const data = await response.json();

    if (response.ok) {
      setDetectionLogs(data.logs || []); 
    } else {
      console.error("Error fetching detection logs:", data.message);
    }
  } catch (error) {
    console.error("Failed to fetch detection logs:", error);
  }
};
  useEffect(() => {
    fetchCameras(); // Fetch cameras when the component mounts
  }, []);

  useEffect(() => {
    if (activeTab === "detection-logs") {
      fetchDetectionLogs();
    }
  }, [activeTab]);

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
        {activeTab === "detection-logs" && (
          <div>
            <h2>Detection Logs</h2>
            {detectionLogs.length === 0 ? (
              <p>No detection logs available.</p>
            ) : (
              <table className="logs-table" border={1}>
                <thead>
                  <tr>
                    <th>Log ID</th>
                    <th>Camera ID</th>
                    <th>Timestamp</th>
                    <th>Detected Gear</th>
                    <th>Confidence Score</th>
                    <th>Entry Allowance</th>
                  </tr>
                </thead>
                <tbody>
                  {detectionLogs.map((log) => (
                    <tr key={log.log_id}>
                      <td>{log.log_id}</td>
                      <td>{log.camera_id}</td>
                      <td>{new Date(log.timestamp).toLocaleString()}</td>
                      <td>{log.detected_gear}</td>
                      <td>{log.confidence_score}</td>
                      <td>{log.entry_allowance}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )} 
      </div>
    </div>
  );
};

export default AdminDashboard;
