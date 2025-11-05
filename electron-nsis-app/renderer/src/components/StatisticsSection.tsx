import React, { useEffect, useRef } from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../store/store';
import './StatisticsSection.css';

// Animated counter component
const AnimatedCounter: React.FC<{ value: number }> = ({ value }) => {
  const [displayValue, setDisplayValue] = React.useState(0);
  const prevValueRef = useRef(0);

  useEffect(() => {
    const prevValue = prevValueRef.current;
    prevValueRef.current = value;

    if (value === prevValue) return;

    const duration = 500; // 500ms animation
    const steps = 20;
    const stepDuration = duration / steps;
    const increment = (value - prevValue) / steps;

    let currentStep = 0;
    const interval = setInterval(() => {
      currentStep++;
      if (currentStep >= steps) {
        setDisplayValue(value);
        clearInterval(interval);
      } else {
        setDisplayValue(Math.round(prevValue + increment * currentStep));
      }
    }, stepDuration);

    return () => clearInterval(interval);
  }, [value]);

  return <span className="badge-value">{displayValue}</span>;
};

const StatisticsSection: React.FC = () => {
  const { badges } = useSelector((state: RootState) => state.ui);

  const badgeData = [
    { label: 'Annullate', value: badges.annullate, color: 'red' },
    { label: 'Aperte', value: badges.aperte, color: 'blue' },
    { label: 'Chiuse', value: badges.chiuse, color: 'green' },
    { label: 'In Lavorazione', value: badges.inLavorazione, color: 'orange' },
    { label: 'Inviate', value: badges.inviate, color: 'purple' },
    { label: 'Eccezioni', value: badges.eccezioni, color: 'darkred' }
  ];

  return (
    <div className="statistics-section">
      <h3 className="section-title">Status</h3>

      <div className="badges-grid">
        {badgeData.map((badge) => (
          <div key={badge.label} className={`badge-card badge-${badge.color}`}>
            <span className="badge-label">{badge.label}</span>
            <AnimatedCounter value={badge.value} />
            <div className="badge-glow"></div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default StatisticsSection;
