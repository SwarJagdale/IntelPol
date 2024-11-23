import React, { useState, useRef } from 'react';
import axios from 'axios';
import styles from './UploadPage.module.css';

const UploadPage = () => {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      alert('Please select a file first!');
      return;
    }

    const uploadData = new FormData();
    uploadData.append('file', file);

    setStatus('');
    setLoading(true);

    try {
      const response = await axios.post('http://bdeminiproj.viewdns.net:8000/upload', uploadData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setStatus(`Upload successful: ${response.data.message}`);
    } catch (error) {
      console.error(error);
      setStatus('Upload failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className={styles.uploadPage}>
      <h1 className={styles.title}>Upload CSV</h1>
      <div className={styles.uploadContainer}>
        <div 
          className={styles.dropzone}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          {file ? (
            <p className={styles.fileSelected}>{file.name}</p>
          ) : (
            <p>Drag & Drop your CSV file here</p>
          )}
        </div>
        <div className={styles.buttonGroup}>
          <input
            ref={fileInputRef}
            id="file-upload"
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            className={styles.fileInput}
          />
          <button 
            onClick={() => fileInputRef.current.click()} 
            className={styles.chooseFileButton}
          >
            Choose File
          </button>
          <button 
            onClick={handleUpload} 
            className={styles.uploadButton} 
            disabled={!file || loading}
          >
            {loading ? 'Uploading...' : 'Upload'}
          </button>
        </div>
        {status && <p className={status.includes('failed') ? styles.errorStatus : styles.successStatus}>{status}</p>}
      </div>
      <div className={styles.instructions}>
        <h2>How to upload your CSV file:</h2>
        <ol>
          <li>Click on the "Choose File" button to select your CSV file, or drag and drop it into the designated area.</li>
          <li>Ensure your file is in CSV format and contains the required data fields.</li>
          <li>Once your file is selected, click the "Upload" button to begin the upload process.</li>
          <li>Wait for the upload to complete. You'll see a success message when it's done.</li>
        </ol>
        <p>Need help? Contact our support team for assistance.</p>
      </div>
    </div>
  );
};

export default UploadPage;

