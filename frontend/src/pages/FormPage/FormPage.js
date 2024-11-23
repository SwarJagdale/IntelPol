import React, { useState } from 'react';
import axios from 'axios';
import styles from './FormPage.module.css';

const FormPage = () => {
  const [formData, setFormData] = useState({});
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const generateCSV = (data) => {
    const headers = Object.keys(data);
    const values = Object.values(data);
    
    // Combine headers and values into a CSV format
    const csvContent = [
      headers.join(','), // Header row
      values.join(','),  // Data row
    ].join('\n');

    return csvContent;
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();

    setStatus('');
    setLoading(true);

    // Convert formData to CSV
    const csvData = generateCSV(formData);

    // Prepare FormData object to send the CSV
    const uploadData = new FormData();
    const csvBlob = new Blob([csvData], { type: 'text/csv' });
    uploadData.append('file', csvBlob, 'formData.csv'); // Append the CSV file

    try {
      const response = await axios.post('http://localhost:8000/upload', uploadData, {
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

  const fields = [
    { name: 'Date Rptd', type: 'text', placeholder: 'Enter Date Rptd' },
    { name: 'Date Occ', type: 'text', placeholder: 'Enter Date Occ' },
    { name: 'Time Occ', type: 'text', placeholder: 'Enter Time Occ' },
    { name: 'Area', type: 'number', placeholder: 'Enter Area' },
    { name: 'Area Name', type: 'text', placeholder: 'Enter Area Name' },
    { name: 'Rpt Dist No', type: 'number', placeholder: 'Enter Report District Number' },
    { name: 'Part 1-2', type: 'number', placeholder: 'Enter Part 1-2' },
    { name: 'Crm Cd', type: 'number', placeholder: 'Enter Crime Code' },
    { name: 'Crm Cd Desc', type: 'text', placeholder: 'Enter Crime Code Description' },
    { name: 'Mo Codes', type: 'text', placeholder: 'Enter Mo Codes' },
    { name: 'Vict Age', type: 'number', placeholder: 'Enter Victim Age' },
    { name: 'Vict Sex', type: 'text', placeholder: 'Enter Victim Sex' },
    { name: 'Vict Descent', type: 'text', placeholder: 'Enter Victim Descent' },
    { name: 'Premis Cd', type: 'number', placeholder: 'Enter Premise Code' },
    { name: 'Premis Desc', type: 'text', placeholder: 'Enter Premise Description' },
    { name: 'Weapon Used Cd', type: 'text', placeholder: 'Enter Weapon Used Code' },
    { name: 'Weapon Desc', type: 'text', placeholder: 'Enter Weapon Description' },
    { name: 'Status', type: 'text', placeholder: 'Enter Status' },
    { name: 'Status Desc', type: 'text', placeholder: 'Enter Status Description' },
    { name: 'Crm Cd 1', type: 'number', placeholder: 'Enter Crime Code 1' },
    { name: 'Crm Cd 2', type: 'number', placeholder: 'Enter Crime Code 2' },
    { name: 'Location', type: 'text', placeholder: 'Enter Location' },
    { name: 'Cross Street', type: 'text', placeholder: 'Enter Cross Street' },
    { name: 'Lat', type: 'number', step: 'any', placeholder: 'Enter Latitude' },
    { name: 'Lon', type: 'number', step: 'any', placeholder: 'Enter Longitude' },
  ];


  return (
    <div className={styles.formPage}>
      <h1 className={styles.title}>Data Input Form</h1>
      <form onSubmit={handleFormSubmit} className={styles.form}>
        {fields.map((field) => (
          <div key={field.name} className={styles.formGroup}>
            <label htmlFor={field.name}>{field.name}</label>
            <input
              type={field.type}
              id={field.name}
              name={field.name}
              placeholder={field.placeholder}
              onChange={handleFormChange}
              className={styles.input}
              required
              step={field.step}
            />
          </div>
        ))}
        <button type="submit" className={styles.submitButton} disabled={loading}>
          {loading ? 'Submitting...' : 'Submit'}
        </button>
      </form>
      {status && <p className={status.includes('failed') ? styles.errorStatus : styles.successStatus}>{status}</p>}
      <div className={styles.instructions}>
        <h2>Form Filling Instructions:</h2>
        <ul>
          <li>All fields are required. Please ensure you fill out each field accurately.</li>
          <li>For numerical fields, enter whole numbers unless specified otherwise (e.g., latitude and longitude).</li>
          <li>If you're unsure about any field, refer to the placeholder text for guidance.</li>
          <li>After filling out all fields, click the "Submit" button to send your data.</li>
        </ul>
      </div>
    </div>
  );
};

export default FormPage;
