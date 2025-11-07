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

  // Alternating DHL colors: yellow and red
  const badgeData: Array<{ label: string; value: number; color: string }> = [
    { label: 'Annullate', value: badges.annullate, color: 'yellow' },
    { label: 'Aperte', value: badges.aperte, color: 'red' },
    { label: 'Chiuse', value: badges.chiuse, color: 'yellow' },
    { label: 'In Lavorazione', value: badges.inLavorazione, color: 'red' },
    { label: 'Inviate', value: badges.inviate, color: 'yellow' },
    { label: 'Eccezioni', value: badges.eccezioni, color: 'red' }
  ];

  return (
    <div className="statistics-section">
      <h3 className="section-title">Status</h3>

      <div className="status-list">
        {badgeData.map((badge, index) => (
          <div
            key={badge.label}
            className={`status-strip status-${badge.color}`}
            style={{ animationDelay: `${index * 30}ms` }}
          >
            <span className="status-label">{badge.label}</span>
            <AnimatedCounter value={badge.value} />
          </div>
        ))}
      </div>
    </div>
  );
};

export default StatisticsSection;
