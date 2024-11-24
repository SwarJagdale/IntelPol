import React from 'react';
import { Link } from 'react-router-dom';
import styles from './LandingPage.module.css';

const LandingPage = () => {
  return (
    <div className={styles.landingPage}>
      <header className={styles.hero}>
        <div className={styles.heroBackground}>
          <div className={styles.particles}></div>
        </div>
        <div className={styles.heroContent}>
          <h1 className={styles.title}>Welcome to PyPDF</h1>
          <p className={styles.subtitle}>Your all-in-one solution for PDF processing and data analysis</p>
          <Link to="/signup" className={styles.ctaButton}>Get Started</Link>
        </div>
      </header>
      
      <section className={styles.features}>
        <div className={styles.feature}>
          <div className={styles.iconWrapper}>
            <i className={`${styles.icon} ${styles.rotatingIcon} fas fa-file-upload`}></i>
          </div>
          <h2>Upload CSV</h2>
          <p>Easily upload and process your CSV files with our intuitive interface.</p>
        </div>
        <div className={styles.feature}>
          <div className={styles.iconWrapper}>
            <i className={`${styles.icon} ${styles.rotatingIcon} fas fa-keyboard`}></i>
          </div>
          <h2>Data Input</h2>
          <p>Manually input data through our user-friendly form for quick analysis.</p>
        </div>
        <div className={styles.feature}>
          <div className={styles.iconWrapper}>
            <i className={`${styles.icon} ${styles.rotatingIcon} fas fa-chart-line`}></i>
          </div>
          <h2>Grafana Dashboard</h2>
          <p>Visualize your data with powerful, interactive Grafana dashboards.</p>
        </div>
        <div className={styles.feature}>
          <div className={styles.iconWrapper}>
            <i className={`${styles.icon} ${styles.rotatingIcon} fas fa-magic`}></i>
          </div>
          <h2>Forecasting</h2>
          <p>Generate accurate forecasts based on your historical data.</p>
        </div>
      </section>
      
      <section className={styles.showcase}>
        <div className={styles.showcaseContent}>
          <h2>Transform Your Data</h2>
          <p>PyPDF offers a comprehensive suite of tools to help you make sense of your data. From CSV processing to advanced forecasting, we've got you covered.</p>
          <Link to="/signup" className={styles.showcaseButton}>Start Your Journey</Link>
        </div>
        <div className={styles.showcaseImage}>
          <img src="/placeholder.svg?height=400&width=600" alt="Data visualization" />
        </div>
      </section>
      
      <section className={styles.testimonials}>
        <h2>What Our Users Say</h2>
        <div className={styles.testimonialGrid}>
          <div className={styles.testimonial}>
            <p>"PyPDF has revolutionized our data processing workflow. It's a game-changer!"</p>
            <span>- John Doe, Data Scientist</span>
          </div>
          <div className={styles.testimonial}>
            <p>"The forecasting feature is incredibly accurate. It's helped us make better business decisions."</p>
            <span>- Jane Smith, Business Analyst</span>
          </div>
          <div className={styles.testimonial}>
            <p>"Easy to use and powerful. PyPDF is now an essential part of our toolkit."</p>
            <span>- Mike Johnson, Research Manager</span>
          </div>
        </div>
      </section>
      
      <section className={styles.cta}>
        <h2>Ready to Get Started?</h2>
        <p>Join thousands of satisfied users and experience the power of PyPDF today!</p>
        <Link to="/signup" className={styles.ctaButton}>Sign Up Now</Link>
      </section>
    </div>
  );
};

export default LandingPage;
