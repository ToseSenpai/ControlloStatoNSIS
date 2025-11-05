import React, { useEffect, useState } from 'react';
import './SplashScreen.css';

const loadingSteps = [
  'Inizializzazione applicazione...',
  'Caricamento componenti UI...',
  'Configurazione sistema...',
  'Preparazione automazione web...',
  'Caricamento moduli Excel...',
  'Inizializzazione state management...',
  'Applicazione pronta!'
];

const SplashScreen: React.FC = () => {
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    const duration = 5000; // 5 seconds
    const steps = loadingSteps.length;
    const stepDuration = duration / steps;

    const interval = setInterval(() => {
      setProgress((prev) => {
        const next = prev + (100 / steps);
        return next >= 100 ? 100 : next;
      });

      setCurrentStep((prev) => {
        const next = prev + 1;
        return next >= steps ? steps - 1 : next;
      });
    }, stepDuration);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="splash-screen">
      <div className="splash-content">
        <div className="splash-header">
          <div className="splash-logo">
            <div className="logo-circle">
              <div className="logo-text">NSIS</div>
            </div>
          </div>
          <h1 className="splash-title">Controllo Stato NSIS</h1>
          <p className="splash-subtitle">Sistema di monitoraggio spedizioni</p>
        </div>

        <div className="progress-section">
          <div className="progress-bar-container">
            <div
              className="progress-bar-fill"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="progress-text">{Math.round(progress)}%</p>
        </div>

        <p className="loading-step">{loadingSteps[currentStep]}</p>

        <div className="splash-footer">
          <p className="footer-text">Sviluppato da ST</p>
        </div>
      </div>
    </div>
  );
};

export default SplashScreen;
