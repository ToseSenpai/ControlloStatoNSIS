import React from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../store/store';
import './StatisticsSection.css';

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
      <h3 className="section-title">Statistiche</h3>

      <div className="badges-grid">
        {badgeData.map((badge) => (
          <div key={badge.label} className={`badge-card badge-${badge.color}`}>
            <span className="badge-label">{badge.label}</span>
            <span className="badge-value">{badge.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default StatisticsSection;
