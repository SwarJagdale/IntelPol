// import React, { useState } from 'react';
// import axios from 'axios';

// function App() {
//     const [file, setFile] = useState(null);
//     const [status, setStatus] = useState('');
//     const [forecast, setForecast] = useState(null);

//     const handleFileChange = (e) => {
//         setFile(e.target.files[0]);
//     };

//     const handleUpload = async () => {
//         if (!file) {
//             alert('Please select a file first!');
//             return;
//         }

//         const formData = new FormData();
//         formData.append('file', file);

//         setStatus('Uploading...');

//         try {
//             const response = await axios.post('http://localhost:8000/upload', formData, {
//                 headers: {
//                     'Content-Type': 'multipart/form-data',
//                 },
//             });
//             setStatus(`Upload successful: ${response.data.message}`);
//         } catch (error) {
//             console.error(error);
//             setStatus('Upload failed.');
//         }
//     };

//     const handleForecast = async () => {
//         setStatus('Generating forecast...');
    
//         try {
//             const response = await axios.post('http://localhost:8000/forecast', {
//                 future_steps: 10 // Include any parameters needed for the forecast
//             });
//             setForecast(response.data.complete_curve);
//             setStatus('Forecast generated successfully!');
//         } catch (error) {
//             console.error(error);
//             setStatus('Forecast generation failed.');
//         }
//     };

//     return (
//         <div style={{ padding: '50px' }}>
//             <h2>Upload CSV</h2>
//             <input type="file" accept=".csv" onChange={handleFileChange} />
//             <br /><br />
//             <button onClick={handleUpload}>Upload</button>
//             <p>{status}</p>

//             <h2>Forecast</h2>
//             <button onClick={handleForecast}>Run Forecast</button>
//             {forecast && (
//                 <div>
//                     <h3>Forecast Results:</h3>
//                     <pre>{JSON.stringify(forecast, null, 2)}</pre>
//                 </div>
//             )}
//         </div>
//     );
// }

// export default App;



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
    const getChartData = () => {
        if (!forecast) return {};

        // Limit history data to the last 100 points
        const historyData = forecast.slice(-100); // Last 100 historical data points
        const forecastData = forecast.slice(-10); // Take the next 10 points for forecast (after the last 100)

        // Create an array of x-axis labels (history + forecast)
        const historyLabels = Array.from({ length: historyData.length }, (_, index) => index + 1);
        const forecastLabels = Array.from({ length: forecastData.length }, (_, index) => historyLabels[historyLabels.length - 1] + index + 1);
        console.log(historyData);

        return {
            labels: [...historyLabels, ...forecastLabels], // Combine history and forecast labels
            datasets: [
                {
                    label: 'History',
                    data: historyData,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.1,
                },
                {
                    label: 'Forecast',
                    data: forecastData,
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.1,
                    borderDash: [5, 5], // Dotted line for forecast
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
                    <Line data={getChartData()} options={{
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
                                    display: false, // Hide X axis title
                                },
                                ticks: {
                                    display: true, // Display x-axis ticks now
                                },
                            },
                            y: {
                                title: {
                                    display: false, // Hide Y axis title
                                },
                                ticks: {
                                    display: true, // Display Y axis ticks (values)
                                },
                            },
                        },
                    }} />
                </div>
            )}
        </div>
    );
}

export default App;


