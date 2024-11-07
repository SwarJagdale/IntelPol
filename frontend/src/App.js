import React, { useState } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2'; // Import Line chart from react-chartjs-2
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import './App.css'; // Import the CSS file
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
              future_steps: 10 // Specify the number of steps for forecasting
          });
  
          // Set history and forecast data separately
          const { history, forecast } = response.data;
  
          // Limit history to the last 100 points if it exceeds 100 data points
          const historyData = history.slice(-100).map((value, index, array) => ({
              x: array.length - 100 + index + 1, // Re-index to maintain continuity
              y: value
          }));
  
          const forecastData = forecast.map((value, index) => ({
              x: historyData.length + index + 1,
              y: value
          }));
  
          setForecast({
              history: historyData,
              forecast: forecastData
          });
  
          setStatus('Forecast generated successfully!');
      } catch (error) {
          console.error(error);
          setStatus('Forecast generation failed.');
      }
  };
  
  // Prepare chart data
  const getChartData = () => {
      if (!forecast) return {};
  
      const historyData = forecast.history; // Array of {x, y} for history
      const forecastData = forecast.forecast; // Array of {x, y} for forecast
  
      return {
          labels: [...historyData.map(point => point.x), ...forecastData.map(point => point.x)],
          datasets: [
              {
                  label: 'History',
                  data: historyData,
                  parsing: {
                      xAxisKey: 'x',
                      yAxisKey: 'y'
                  },
                  borderColor: 'rgba(75, 192, 192, 1)',
                  borderWidth: 2,
                  fill: false,
                  tension: 0.1,
              },
              {
                  label: 'Forecast',
                  data: forecastData,
                  parsing: {
                      xAxisKey: 'x',
                      yAxisKey: 'y'
                  },
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
            <iframe src="http://bdemini.viewdns.net:3001/d/ee2z0zjgfzh1cc/bde-mini-project?from=2020-01-01T00:00:00.000Z&to=2024-09-28T00:00:00.000Z&timezone=browser&kiosk" style={{ width: '80vw', height: '80vh' }}></iframe>
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