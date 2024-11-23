import React from 'react';
import styles from './GrafanaPage.module.css';

const GrafanaPage = () => {
  return (
    <div className={styles.grafanaPage}>
      <h1 className={styles.title}>Grafana Dashboard</h1>
      <div className={styles.dashboardContainer}>
        <iframe
          src="http://localhost:3001/public-dashboards/edb196cf46e64a42baf3a6a1ac7c05a1"
          className={styles.dashboard}
          title="Grafana Dashboard"
        ></iframe>
      </div>
    </div>
  );
};

export default GrafanaPage;
