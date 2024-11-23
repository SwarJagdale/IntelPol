// import React, { useState } from 'react';
// import axios from 'axios';
// import { Line } from 'react-chartjs-2';
// import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
// import './App.css';

// // Registering Chart.js components
// ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

// function App() {
//     const [file, setFile] = useState(null);
//     const [status, setStatus] = useState('');
//     const [forecast, setForecast] = useState(null);
//     const [formData, setFormData] = useState({});
//     const [inputMode, setInputMode] = useState('upload'); // 'upload' or 'form'

//     const handleFileChange = (e) => {
//         setFile(e.target.files[0]);
//     };

// const handleUpload = async () => {
//     if (!file) {
//         alert('Please select a file first!');
//         return;
//     }

//     const uploadData = new FormData();
//     uploadData.append('file', file);

//     setStatus('Uploading...');

//     try {
//         const response = await axios.post('http://localhost:8000/upload', uploadData, {
//             headers: {
//                 'Content-Type': 'multipart/form-data',
//             },
//         });
//         setStatus(`Upload successful: ${response.data.message}`);
//     } catch (error) {
//         console.error(error);
//         setStatus('Upload failed.');
//     }
// };

//     const handleFormChange = (e) => {
//         const { name, value } = e.target;
//         setFormData((prevData) => ({
//             ...prevData,
//             [name]: value,
//         }));
//     };

//     const handleFormSubmit = async (e) => {
//         e.preventDefault();
//         setStatus('Submitting form data...');
//         try {
//             const response = await axios.post('http://localhost:8000/submit', formData);
//             setStatus(`Form submission successful: ${response.data.message}`);
//         } catch (error) {
//             console.error(error);
//             setStatus('Form submission failed.');
//         }
//     };

//     const handleForecast = async () => {
//         setStatus('Generating forecast...');
//         try {
//             const response = await axios.post('http://localhost:8000/forecast', { future_steps: 10 });
//             const { history, forecast } = response.data;

//             const historyData = history.slice(-100).map((value, index) => ({
//                 x: index + 1,
//                 y: value,
//             }));

//             const forecastData = forecast.map((value, index) => ({
//                 x: historyData.length + index + 1,
//                 y: value,
//             }));

//             setForecast({
//                 history: historyData,
//                 forecast: forecastData,
//             });

//             setStatus('Forecast generated successfully!');
//         } catch (error) {
//             console.error(error);
//             setStatus('Forecast generation failed.');
//         }
//     };

//     const getChartData = () => {
//         if (!forecast) return {};
//         const historyData = forecast.history;
//         const forecastData = forecast.forecast;

//         return {
//             labels: [...historyData.map((p) => p.x), ...forecastData.map((p) => p.x)],
//             datasets: [
//                 {
//                     label: 'History',
//                     data: historyData,
//                     borderColor: 'rgba(75, 192, 192, 1)',
//                     borderWidth: 2,
//                     fill: false,
//                 },
//                 {
//                     label: 'Forecast',
//                     data: forecastData,
//                     borderColor: 'rgba(255, 99, 132, 1)',
//                     borderDash: [5, 5],
//                     borderWidth: 2,
//                     fill: false,
//                 },
//             ],
//         };
//     };

//     return (
//         <div style={{ padding: '50px' }}>
//             {/* Navbar */}
//             <div className="navbar">
//                 <div className="logo">PyPDF</div>
//                 <div className="nav-links">
//                     <a href="#">Home</a>
//                     <a href="#">Grafana</a>
//                     <a href="#">Forecasting</a>
//                 </div>
//             </div>

//             <h1 className="title">PyPDF</h1>

//             {/* Input Mode Toggle */}
//             <div className="input-mode-toggle">
//                 <button
//                     className={inputMode === 'upload' ? 'active' : ''}
//                     onClick={() => setInputMode('upload')}
//                 >
//                     Upload CSV
//                 </button>
//                 <button
//                     className={inputMode === 'form' ? 'active' : ''}
//                     onClick={() => setInputMode('form')}
//                 >
//                     Fill Form
//                 </button>
//             </div>

//             {inputMode === 'upload' ? (
//                 // File Upload Section
//                 <div className="upload-section">
//                     <h2 className="section-title">Upload CSV</h2>
//                     <label htmlFor="file-upload" className="custom-file-upload">
//                         Choose File
//                     </label>
//                     <input
//                         id="file-upload"
//                         type="file"
//                         accept=".csv"
//                         onChange={handleFileChange}
//                         style={{ display: 'none' }}
//                     />
//                     <p className="file-status">{file ? `Selected file: ${file.name}` : 'No file chosen'}</p>
//                     <button onClick={handleUpload}>Upload</button>
//                     <p>{status}</p>
//                 </div>
//             ) : (
//                 // Form Input Section
//                 <div className="form-section">
//                     <h2 className="section-title">Fill Form</h2>
//                     <div className="form-scrollable">
//                         <form onSubmit={handleFormSubmit}>
//                             {['Area', 'Rpt Dist No', 'Part 1-2', 'Crm Cd', 'Vict Age', 'Premis Cd', 'Weapon Used Cd', 'Crm Cd 1', 'Crm Cd 2', 'Lat', 'Lon'].map((field) => (
//                                 <div key={field}>
//                                     <label htmlFor={field}>{field}</label>
//                                     <input
//                                         type="text"
//                                         id={field}
//                                         name={field}
//                                         placeholder={`Enter ${field}`}
//                                         onChange={handleFormChange}
//                                     />
//                                 </div>
//                             ))}
//                             <button type="submit">Submit</button>
//                         </form>
//                     </div>
//                 </div>
//             )}

//             {/* Grafana Dashboard Section */}
//             <div className="grafana-section">
//                 <h2 className="section-title">Grafana Dashboard</h2>
//                 <iframe
//                     src="http://localhost:3001/d/ee2z0zjgfzh1cc/bde-mini-project?from=2020-01-01T00:00:00.000Z&to=2024-09-28T00:00:00.000Z&timezone=browser&kiosk"
//                     style={{ width: '100%', height: '500px', border: 'none' }}
//                     title="Grafana Dashboard"
//                 ></iframe>
//             </div>

//             {/* Forecast Section */}
//             <div className="forecast-section">
//                 <h2 className="section-title">Forecast</h2>
//                 <button onClick={handleForecast}>Run Forecast</button>
//                 {forecast && (
//                     <div>
//                         <h3>Forecast Visualization:</h3>
//                         <Line data={getChartData()} />
//                     </div>
//                 )}
//             </div>
//         </div>
//     );
// }

// export default App;




import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Navbar from './components/Navbar/Navbar';
import LandingPage from './pages/LandingPage/LandingPage';
import UploadPage from './pages/UploadPage/UploadPage';
import FormPage from './pages/FormPage/FormPage';
import GrafanaPage from './pages/GrafanaPage/GrafanaPage';
import ForecastPage from './pages/ForecastPage/ForecastPage';
import SignUp from './components/Auth/SignUp';
import Login from './components/Auth/Login';
import styles from './App.module.css';

const App = () => {
  return (
    <Router>
      <div className={styles.app}>
        <Navbar />
        <main className={styles.mainContent}>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/form" element={<FormPage />} />
            <Route path="/grafana" element={<GrafanaPage />} />
            <Route path="/forecast" element={<ForecastPage />} />
            <Route path="/signup" element={<SignUp />} />
            <Route path="/login" element={<Login />} />
          </Routes>
        </main>
        <footer className={styles.footer}>
          <p>&copy; 2023 PyPDF. All rights reserved.</p>
        </footer>
      </div>
    </Router>
  );
};

export default App;



