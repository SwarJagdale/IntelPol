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

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    setStatus('');
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/submit', formData);
      setStatus(`Form submission successful: ${response.data.message}`);
    } catch (error) {
      console.error(error);
      setStatus('Form submission failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fields = [
    { name: 'Area', type: 'text', placeholder: 'Enter Area' },
    { name: 'Rpt Dist No', type: 'number', placeholder: 'Enter Report District Number' },
    { name: 'Part 1-2', type: 'text', placeholder: 'Enter Part 1-2' },
    { name: 'Crm Cd', type: 'number', placeholder: 'Enter Crime Code' },
    { name: 'Vict Age', type: 'number', placeholder: 'Enter Victim Age' },
    { name: 'Premis Cd', type: 'number', placeholder: 'Enter Premise Code' },
    { name: 'Weapon Used Cd', type: 'number', placeholder: 'Enter Weapon Used Code' },
    { name: 'Crm Cd 1', type: 'number', placeholder: 'Enter Crime Code 1' },
    { name: 'Crm Cd 2', type: 'number', placeholder: 'Enter Crime Code 2' },
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

