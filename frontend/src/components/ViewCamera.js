import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';  // Import useParams
import '../styles/ViewCamera.css';

const ViewCamera = () => {
  const { cameraId } = useParams();  // Capture the cameraId from the URL
  const navigate = useNavigate();
  const [isDetecting, setIsDetecting] = useState(false);
  const [videoSource, setVideoSource] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  const toggleDetection = async () => {
    try {
      if (!isDetecting) {
        // ✅ Start detection for the selected camera
        setVideoSource(''); // Force UI update before setting new source
        setIsDetecting(true);
        setTimeout(() => {
          setVideoSource(`http://127.0.0.1:8000/start_detection?camera_id=${cameraId}`);
        }, 200); // Small delay to force UI refresh
      } else {
        // ✅ Stop detection and clear the video source
        setIsDetecting(false);
        await fetch(`http://127.0.0.1:8000/stop_detection?camera_id=${cameraId}`);
        setVideoSource('');
      }
    } catch (error) {
      setErrorMessage('Error: ' + error.message);
    }
  };

  const deleteCamera = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/cameras/${cameraId}/`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete camera');
      }

      // After successful deletion, navigate away (e.g., back to the camera list page)
      alert("Camera deleted successfully!");
      navigate('/admin-dashboard'); // Assuming '/cameras' is your camera list route
    } catch (error) {
      setErrorMessage('Error: ' + error.message);
    }
  };

  return (
    <div className="dashboard-container">
      {/* Sidebar */}
      <div className="sidebar">
        <h3>Camera View</h3>
        <button onClick={toggleDetection}>
          {isDetecting ? 'Stop Detection' : 'Start Detection'}
        </button>
        <button onClick={deleteCamera} style={{ marginTop: '10px' }}>
        Delete Camera
        </button>
                {/* Back Button */}
                <button onClick={() => navigate('/admin-dashboard')} style={{ marginTop: '10px' }}>
          Back to Dashboard
        </button>
      </div>

      {/* Content area */}
      <div className="content">
        <h2>Live Camera Feed</h2>
        <div className="camera-container">
          {videoSource && isDetecting ? (
            <img
              id="cameraFeed"
              width="100%"
              height="auto"
              alt="Camera Stream"
              src={videoSource}
            />
          ) : (
            <p>{isDetecting ? "Starting detection..." : "Click 'Start Detection' to begin."}</p>
          )}
          {errorMessage && <div style={{ color: 'red' }}>{errorMessage}</div>}
        </div>
      </div>
    </div>
  );
};

export default ViewCamera;
