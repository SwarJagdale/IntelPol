

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
          
        </footer>
      </div>
    </Router>
  );
};

export default App;



