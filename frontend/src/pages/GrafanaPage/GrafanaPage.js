import React from 'react';
import styles from './GrafanaPage.module.css';

const GrafanaPage = () => {
  return (
    <div className={styles.grafanaPage}>
      <h1 className={styles.title}>Grafana Dashboard</h1>
      <div className={styles.dashboardContainer}>
        <iframe
          src="http://localhost:3001/d/ee2z0zjgfzh1cc/bde-mini-project?from=2020-01-01T00:00:00.000Z&to=2024-09-28T00:00:00.000Z&timezone=browser&kiosk"
          className={styles.dashboard}
          title="Grafana Dashboard"
        ></iframe>
      </div>
    </div>
  );
};

export default GrafanaPage;
