import React from 'react';
import { Link } from 'react-router-dom';
import styles from './Navbar.module.css';

const Navbar = () => {
  return (
    <nav className={styles.navbar}>
      <div className={styles.logo}>
        <Link to="/">Crime Cloud</Link>
      </div>
      <div className={styles.navLinks}>
        <Link to="/">Home</Link>
        <Link to="/upload">Upload</Link>
        <Link to="/form">Form</Link>
        <Link to="/grafana">Grafana</Link>
        <Link to="/forecast">Forecast</Link>
      </div>
      <div className={styles.authLinks}>
        <Link to="/login" className={styles.loginButton}>Login</Link>
        <Link to="/signup" className={styles.signupButton}>Sign Up</Link>
      </div>
    </nav>
  );
};

export default Navbar;

