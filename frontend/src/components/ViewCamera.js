import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';  // Import useParams
import '../styles/ViewCamera.css';

const ViewCamera = () => {
  const { cameraId } = useParams();  // Capture the cameraId from the URL
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

  return (
    <div className="dashboard-container">
      {/* Sidebar */}
      <div className="sidebar">
        <h3>Camera View</h3>
        <button onClick={toggleDetection}>
          {isDetecting ? 'Stop Detection' : 'Start Detection'}
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
