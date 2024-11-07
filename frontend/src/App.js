import React, { useState } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2'; // Import Line chart from react-chartjs-2
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';

// Register Chart.js components
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
            const response = await axios.post('http://localhost:8000/forecast', {
                future_steps: 10 // Include any parameters needed for the forecast
            });
            setForecast(response.data.complete_curve);
            setStatus('Forecast generated successfully!');
        } catch (error) {
            console.error(error);
            setStatus('Forecast generation failed.');
        }
    };

    // Prepare chart data
    // Prepare chart data
const getChartData = () => {
    if (!forecast) return {};

    // Extract the last 100 historical data points and forecast data
    const historyData = forecast.slice(1597, -10); // Full history data
    const last100HistoryData = historyData.slice(-100); // Last 100 points of history
    const forecastData = forecast.slice(-10); // 10 forecast points

    // Combine last 100 history points and forecast points into one dataset
    const combinedData = [...last100HistoryData, ...forecastData];

    // Generate labels for the 100 history points and forecast points
    const labels = Array.from({ length: combinedData.length }, (_, index) => index + 1);

    return {
        labels: labels,
        datasets: [
            {
                label: 'History + Forecast',
                data: combinedData,
                borderColor: (ctx) => {
                    const index = ctx.dataIndex;
                    return index < last100HistoryData.length ? 'rgba(75, 192, 192, 1)' : 'rgba(255, 99, 132, 1)';
                },
                borderWidth: 2,
                fill: false,
                tension: 0.1,
            },
        ],
    };
};


    return (
        <div style={{ padding: '50px' }}>
            <h2>Upload CSV</h2>
            <input type="file" accept=".csv" onChange={handleFileChange} />
            <br /><br />
            <button onClick={handleUpload}>Upload</button>
            <p>{status}</p>

            <h2>Forecast</h2>
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
                                    enabled: true, // Enable tooltips on hover
                                    callbacks: {
                                        // Custom callback to show the value on hover
                                        label: function(tooltipItem) {
                                            return `Value: ${tooltipItem.raw}`;
                                        },
                                    },
                                },
                            },
                            scales: {
                                x: {
                                    title: {
                                        display: false, // Hide X axis title
                                    },
                                    ticks: {
                                        display: true, // Display x-axis ticks
                                    },
                                },
                                y: {
                                    title: {
                                        display: false, // Hide Y axis title
                                    },
                                    ticks: {
                                        display: true, // Display Y axis ticks
                                    },
                                },
                            },
                        }} 
                    />
                </div>
            )}
        </div>
    );
}

export default App;