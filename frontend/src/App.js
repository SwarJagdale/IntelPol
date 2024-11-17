import React, { useState } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import './App.css';

// Registering Chart.js components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

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

    const handleForecast = async () => {
        setStatus('Generating forecast...');
        try {
            const response = await axios.post('http://localhost:8000/forecast', { future_steps: 10 });
            const { history, forecast } = response.data;

            const historyData = history.slice(-100).map((value, index) => ({
                x: index + 1,
                y: value,
            }));

            const forecastData = forecast.map((value, index) => ({
                x: historyData.length + index + 1,
                y: value,
            }));

            setForecast({
                history: historyData,
                forecast: forecastData,
            });

            setStatus('Forecast generated successfully!');
        } catch (error) {
            console.error(error);
            setStatus('Forecast generation failed.');
        }
    };

    const getChartData = () => {
        if (!forecast) return {};
        const historyData = forecast.history;
        const forecastData = forecast.forecast;

        return {
            labels: [...historyData.map((p) => p.x), ...forecastData.map((p) => p.x)],
            datasets: [
                {
                    label: 'History',
                    data: historyData,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 2,
                    fill: false,
                },
                {
                    label: 'Forecast',
                    data: forecastData,
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderDash: [5, 5],
                    borderWidth: 2,
                    fill: false,
                },
            ],
        };
    };

    return (
        <div style={{ padding: '50px' }}>
            {/* Navbar */}
            <div className="navbar">
                <div className="logo">PyPDF</div>
                <div className="nav-links">
                    <a href="#">Home</a>
                    <a href="#">Grafana</a>
                    <a href="#">Forecasting</a>
                </div>
            </div>

            <h1 className="title">PyPDF</h1>

            {/* File Upload Section */}
            <div className="upload-section">
                <h2 className="section-title">Upload CSV</h2>
                <label htmlFor="file-upload" className="custom-file-upload">
                    Choose File
                </label>
                <input 
                    id="file-upload" 
                    type="file" 
                    accept=".csv" 
                    onChange={handleFileChange} 
                    style={{ display: 'none' }} 
                />
                <p className="file-status">{file ? `Selected file: ${file.name}` : 'No file chosen'}</p>
                <button onClick={handleUpload}>Upload</button>
                <p>{status}</p>
            </div>


            {/* Grafana Dashboard Section */}
            <div className="grafana-section">
                <h2 className="section-title">Grafana Dashboard</h2>
                <iframe
                    src="http://localhost:3001/d/ee2z0zjgfzh1cc/bde-mini-project?from=2020-01-01T00:00:00.000Z&to=2024-09-28T00:00:00.000Z&timezone=browser&kiosk"
                    style={{ width: '100%', height: '500px', border: 'none' }}
                    title="Grafana Dashboard"
                ></iframe>
            </div>

            {/* Forecast Section */}
            <div className="forecast-section">
                <h2 className="section-title">Forecast</h2>
                <button onClick={handleForecast}>Run Forecast</button>
                {forecast && (
                    <div>
                        <h3>Forecast Visualization:</h3>
                        <Line
                            data={getChartData()}
                            options={{
                                responsive: true,
                                plugins: {
                                    title: {
                                        display: true,
                                        text: 'History vs Forecast',
                                    },
                                    tooltip: {
                                        enabled: false, // Disable tooltips
                                    },
                                },
                                scales: {
                                    x: {
                                        title: {
                                            display: false, // Hide X-axis title
                                        },
                                        ticks: {
                                            display: true, // Display X-axis ticks
                                        },
                                    },
                                    y: {
                                        title: {
                                            display: false, // Hide Y-axis title
                                        },
                                        ticks: {
                                            display: true, // Display Y-axis ticks
                                        },
                                    },
                                },
                            }}
                        />
                    </div>
                )}
            </div>
        </div>
    );
}

export default App;
