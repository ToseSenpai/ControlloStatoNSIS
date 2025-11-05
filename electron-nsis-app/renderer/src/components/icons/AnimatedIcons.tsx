/**
 * Componenti Icone Animate
 *
 * Sostituisce le vecchie animazioni GIF con animazioni SVG CSS moderne.
 * Vantaggi rispetto ai GIF:
 * - Scalabili (perfette su tutti i display)
 * - Dimensioni file ridotte (10-100x più piccole)
 * - Controllabili via CSS/JS
 * - Performance migliori
 * - Supporto trasparenza e compositing
 */

import React from 'react';
import { Loader2, Heart, Package, BarChart3 } from 'lucide-react';
import type { IconProps } from './index';
import './AnimatedIcons.css';

/**
 * Icona Loading Animata
 * Sostituisce: loading.gif
 *
 * Spinner rotante con animazione fluida
 */
export const LoadingIcon: React.FC<IconProps> = ({
  size = 48,
  color = 'currentColor',
  className = '',
  ...props
}) => {
  return (
    <Loader2
      size={size}
      color={color}
      className={`icon-loading ${className}`}
      {...props}
    />
  );
};

/**
 * Icona Love Animata
 * Sostituisce: love.gif
 *
 * Cuore pulsante con effetto scala
 */
export const LoveIcon: React.FC<IconProps> = ({
  size = 48,
  color = '#ef4444',
  className = '',
  ...props
}) => {
  return (
    <Heart
      size={size}
      color={color}
      fill={color}
      className={`icon-love ${className}`}
      {...props}
    />
  );
};

/**
 * Icona Stati Animata
 * Sostituisce: stati.gif
 *
 * Pacchetto con animazione di movimento verticale
 */
export const StatiIcon: React.FC<IconProps> = ({
  size = 48,
  color = 'currentColor',
  className = '',
  ...props
}) => {
  return (
    <div className="icon-stati-container">
      <Package
        size={size}
        color={color}
        className={`icon-stati ${className}`}
        {...props}
      />
    </div>
  );
};

/**
 * Icona Statistics Animata
 * Sostituisce: statistics.gif
 *
 * Grafico a barre con animazione di crescita
 */
export const StatisticsIcon: React.FC<IconProps> = ({
  size = 48,
  color = 'currentColor',
  className = '',
  ...props
}) => {
  return (
    <div className="icon-statistics-container">
      <BarChart3
        size={size}
        color={color}
        className={`icon-statistics ${className}`}
        {...props}
      />
    </div>
  );
};

/**
 * Icona Loading con Punti
 * Alternativa moderna per loading con animazione a punti
 */
export const LoadingDotsIcon: React.FC<{ className?: string }> = ({
  className = '',
}) => {
  return (
    <div className={`loading-dots ${className}`}>
      <div className="dot"></div>
      <div className="dot"></div>
      <div className="dot"></div>
    </div>
  );
};

/**
 * Icona Pulse Generica
 * Può essere usata con qualsiasi icona Lucide per aggiungere effetto pulse
 */
export const PulseIcon: React.FC<{
  icon: React.ComponentType<IconProps>;
  iconProps?: IconProps;
  className?: string;
}> = ({ icon: Icon, iconProps = {}, className = '' }) => {
  return (
    <Icon
      {...iconProps}
      className={`icon-pulse ${iconProps.className || ''} ${className}`}
    />
  );
};

/**
 * Icona Spin Generica
 * Può essere usata con qualsiasi icona Lucide per aggiungere rotazione
 */
export const SpinIcon: React.FC<{
  icon: React.ComponentType<IconProps>;
  iconProps?: IconProps;
  className?: string;
}> = ({ icon: Icon, iconProps = {}, className = '' }) => {
  return (
    <Icon
      {...iconProps}
      className={`icon-spin ${iconProps.className || ''} ${className}`}
    />
  );
};

/**
 * Icona Bounce Generica
 * Aggiunge effetto rimbalzo a qualsiasi icona
 */
export const BounceIcon: React.FC<{
  icon: React.ComponentType<IconProps>;
  iconProps?: IconProps;
  className?: string;
}> = ({ icon: Icon, iconProps = {}, className = '' }) => {
  return (
    <Icon
      {...iconProps}
      className={`icon-bounce ${iconProps.className || ''} ${className}`}
    />
  );
};

/**
 * Esporta tutte le icone animate
 */
export const AnimatedIcons = {
  Loading: LoadingIcon,
  Love: LoveIcon,
  Stati: StatiIcon,
  Statistics: StatisticsIcon,
  LoadingDots: LoadingDotsIcon,
  Pulse: PulseIcon,
  Spin: SpinIcon,
  Bounce: BounceIcon,
} as const;

/**
 * Mappa GIF legacy -> Componenti animati moderni
 */
export const AnimatedIconMap = {
  'loading.gif': LoadingIcon,
  'love.gif': LoveIcon,
  'stati.gif': StatiIcon,
  'statistics.gif': StatisticsIcon,
} as const;

export default AnimatedIcons;
