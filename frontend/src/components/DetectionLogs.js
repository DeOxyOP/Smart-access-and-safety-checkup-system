import React, { useState, useEffect } from "react";

const DetectionLogs = () => {
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/get-detection-logs/")
      .then(response => response.json())
      .then(data => {
        if (data.logs) {
          setLogs(data.logs);
        } else {
          setLogs([]);
        }
      })
      .catch(error => setError(error.message));
  }, []);

  const formatIST = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString("en-IN", { timeZone: "Asia/Kolkata" }); // ✅ Convert to IST
  };

  return (
    <div>
      <h2>Detection Logs</h2>

      {error && <p style={{ color: "red" }}>Error: {error}</p>}

      {logs.length === 0 ? (
        <p>No detection logs available.</p>
      ) : (
        <table border="1">
          <thead>
            <tr>
              <th>Camera ID</th>
              <th>Detected Gear</th>
              <th>Confidence Score</th>
              <th>Entry Allowance</th>
              <th>Timestamp (IST)</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log, index) => (
              <tr key={index}>
                <td>{log.camera_id}</td>
                <td>{log.detected_gear}</td>
                <td>{log.confidence_score.toFixed(2)}</td>
                <td>{log.entry_allowance}</td>
                <td>{formatIST(log.timestamp)}</td> {/* ✅ Convert to IST */}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default DetectionLogs;