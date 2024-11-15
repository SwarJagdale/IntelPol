import React, { useState } from 'react';
import axios from 'axios';

function App() {
    const [file, setFile] = useState(null);
    const [status, setStatus] = useState('');
    const [forecast, setForecast] = useState(null);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleUpload = async () => {
        if (!file) {
            alert('Please select a file first!');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        setStatus('Uploading...');

    try {
      const response = await axios.post('http://localhost:8000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setStatus(`Upload successful: ${response.data.message}`);
    } catch (error) {
      console.error(error);
      setStatus('Upload failed.');
    }
  };

  return (
    <div style={{ padding: '50px' }}>
      <h2>Upload PDF</h2>
      <input type="file" accept=".csv" onChange={handleFileChange} />
      <br /><br />
      <button onClick={handleUpload}>Upload</button>
      <p>{status}</p>
    </div>
  );
}

export default App;