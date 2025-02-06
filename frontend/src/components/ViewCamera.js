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
      setIsDetecting((prevState) => !prevState);

      if (!isDetecting) {
        // Start detection for the selected camera by fetching from FastAPI backend
        setVideoSource(`http://127.0.0.1:8000/start_detection?camera_id=${cameraId}`);
      } else {
        // Stop detection and clear the video source
        setVideoSource('');
        await fetch(`http://127.0.0.1:8000/stop_detection?camera_id=${cameraId}`);
      }
    } catch (error) {
      setErrorMessage('Error: ' + error.message);
    }
  };

  useEffect(() => {
    if (isDetecting) {
      // Ensure the video source is set when detection starts
      setVideoSource(`http://127.0.0.1:8000/start_detection?camera_id=${cameraId}`);
    }

    // Clean up the video source if detection is stopped
    return () => {
      setVideoSource('');
    };
  }, [isDetecting, cameraId]);  // Add cameraId dependency

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
          <video
            id="cameraFeed"
            width="100%"
            height="auto"
            autoPlay
            muted
            playsInline
            style={{ display: isDetecting ? 'block' : 'none' }}
            src={videoSource}
          />
          {errorMessage && <div style={{ color: 'red' }}>{errorMessage}</div>}
          <div id="detectionMessage">
            {isDetecting ? 'Detection Running...' : 'Click "Start Detection" to begin.'}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ViewCamera;
