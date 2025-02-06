// import React, { useState } from "react";
// import "../styles/AddCamera.css"; // Separate CSS for styling

// const AddCamera = ({ onClose }) => {
//   const [cameraName, setCameraName] = useState("");
//   const [rtspUrl, setRtspUrl] = useState("");
//   const [location, setLocation] = useState("");
//   const [message, setMessage] = useState(null);
//   const [error, setError] = useState(null);

//   const handleAddCamera = async (e) => {
//     e.preventDefault();
//     setMessage(null);
//     setError(null);

//     const cameraData = { camera_name: cameraName, rtsp_url: rtspUrl, location };

//     try {
//       const response = await fetch("http://127.0.0.1:8000/api/cameras/", {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//         },
//         body: JSON.stringify(cameraData),
//       });

//       const result = await response.json();

//       if (response.ok) {
//         setMessage(result.message);
//       } else {
//         setError(result.detail || "Failed to add camera.");
//       }
//     } catch (err) {
//       setError("Failed to connect to the server.");
//     }
//   };

//   return (
//     <div className="add-camera-container">
//       <h3>Add New Camera</h3>
//       <form onSubmit={handleAddCamera}>
//         <input
//           type="text"
//           placeholder="Camera Name"
//           value={cameraName}
//           onChange={(e) => setCameraName(e.target.value)}
//           required
//         />
//         <input
//           type="text"
//           placeholder="RTSP URL / IP Address"
//           value={rtspUrl}
//           onChange={(e) => setRtspUrl(e.target.value)}
//           required
//         />
//         <input
//           type="text"
//           placeholder="Location"
//           value={location}
//           onChange={(e) => setLocation(e.target.value)}
//           required
//         />
//         <button type="submit">Add Camera</button>
//       </form>

//       {message && <p className="success-message">{message}</p>}
//       {error && <p className="error-message">{error}</p>}

//       <button className="close-button" onClick={onClose}>
//         Close
//       </button>
//     </div>
//   );
// };

// export default AddCamera;



import React, { useState } from "react";
import "../styles/AddCamera.css"; // Separate CSS for styling

const AddCamera = ({ setCameras, onClose }) => {
  const [cameraName, setCameraName] = useState("");
  const [rtspUrl, setRtspUrl] = useState("");
  const [location, setLocation] = useState("");
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  const handleAddCamera = async (e) => {
    e.preventDefault();
    setMessage(null);
    setError(null);

    const cameraData = { camera_name: cameraName, rtsp_url: rtspUrl, location };

    try {
      const response = await fetch("http://127.0.0.1:8000/api/cameras/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(cameraData),
      });

      const result = await response.json();

      if (response.ok) {
        setMessage(result.message);

        // ✅ Fetch updated camera list after adding new camera
        const updatedCameras = await fetch("http://127.0.0.1:8000/api/get-cameras/").then((res) => res.json());
        setCameras(Array.isArray(updatedCameras) ? updatedCameras : updatedCameras.cameras || []);

        // Clear input fields
        setCameraName("");
        setRtspUrl("");
        setLocation("");
      } else {
        setError(result.detail || "Failed to add camera.");
      }
    } catch (err) {
      setError("Failed to connect to the server.");
    }
  };

  return (
    <div className="add-camera-container">
      <h3>Add New Camera</h3>
      <form onSubmit={handleAddCamera}>
        <input
          type="text"
          placeholder="Camera Name"
          value={cameraName}
          onChange={(e) => setCameraName(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="RTSP URL / IP Address"
          value={rtspUrl}
          onChange={(e) => setRtspUrl(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="Location"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          required
        />
        <button type="submit">Add Camera</button>
      </form>

      {message && <p className="success-message">{message}</p>}
      {error && <p className="error-message">{error}</p>}

      <button className="close-button" onClick={onClose}>
        Close
      </button>
    </div>
  );
};

export default AddCamera;
