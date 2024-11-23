import React, { useState } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import styles from './ForecastPage.module.css';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const ForecastPage = () => {
  const [forecast, setForecast] = useState(null);
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleForecast = async () => {
    setStatus('');
    setError('');
    setLoading(true);
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
      setError('Forecast generation failed. Please try again.');
    } finally {
      setLoading(false);
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
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          borderWidth: 2,
          fill: true,
        },
        {
          label: 'Forecast',
          data: forecastData,
          borderColor: 'rgba(255, 99, 132, 1)',
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          borderDash: [5, 5],
          borderWidth: 2,
          fill: true,
        },
      ],
    };
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Forecast Visualization',
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'Time Steps',
        },
      },
      y: {
        title: {
          display: true,
          text: 'Value',
        },
      },
    },
  };

  return (
    <div className={styles.forecastPage}>
      <h1 className={styles.title}>Forecast</h1>
      <div className={styles.controlPanel}>
        <button onClick={handleForecast} className={styles.forecastButton} disabled={loading}>
          {loading ? 'Generating...' : 'Generate Forecast'}
        </button>
        {status && <p className={styles.status}>{status}</p>}
        {error && <p className={styles.error}>{error}</p>}
      </div>
      {forecast && (
        <div className={styles.chartContainer}>
          <Line data={getChartData()} options={chartOptions} />
        </div>
      )}
      <div className={styles.infoPanel}>
        <h2>About Our Forecasting</h2>
        <p>
          Our advanced forecasting algorithm uses state-of-the-art machine learning techniques to predict future trends based on historical data. This powerful tool can help you make informed decisions and stay ahead of the curve.
        </p>
        <h3>How to use:</h3>
        <ol>
          <li>Click the "Generate Forecast" button to start the process.</li>
          <li>Wait for the algorithm to analyze your data and generate predictions.</li>
          <li>Review the visualized forecast, comparing historical data with predicted future trends.</li>
          <li>Use these insights to inform your decision-making process.</li>
        </ol>
      </div>
    </div>
  );
};

export default ForecastPage;

