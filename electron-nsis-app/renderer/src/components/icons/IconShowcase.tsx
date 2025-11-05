/**
 * Showcase delle Icone
 *
 * Componente demo per visualizzare tutte le icone disponibili.
 * Utile per sviluppo e testing.
 *
 * Utilizzo:
 * import { IconShowcase } from '@icons/IconShowcase';
 * <IconShowcase />
 */

import React from 'react';
import { Icons, IconSizes, IconColors } from './index';
import {
  LoadingIcon,
  LoveIcon,
  StatiIcon,
  StatisticsIcon,
  LoadingDotsIcon,
} from './AnimatedIcons';
import './AnimatedIcons.css';

export const IconShowcase: React.FC = () => {
  return (
    <div style={{ padding: '20px', fontFamily: 'system-ui' }}>
      <h1>🎨 Showcase Icone - ControlloStatoNSIS</h1>

      {/* File Icons */}
      <section style={{ marginBottom: '40px' }}>
        <h2>📄 File e Documenti</h2>
        <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
          <div style={{ textAlign: 'center' }}>
            <Icons.File.Text size={IconSizes.xl} />
            <p>Text</p>
          </div>
          <div style={{ textAlign: 'center' }}>
            <Icons.File.Excel size={IconSizes.xl} color={IconColors.success} />
            <p>Excel</p>
          </div>
          <div style={{ textAlign: 'center' }}>
            <Icons.File.Folder size={IconSizes.xl} color={IconColors.warning} />
            <p>Folder</p>
          </div>
          <div style={{ textAlign: 'center' }}>
            <Icons.File.FolderOpen size={IconSizes.xl} color={IconColors.warning} />
            <p>Folder Open</p>
          </div>
        </div>
      </section>

      {/* Media Controls */}
      <section style={{ marginBottom: '40px' }}>
        <h2>▶️ Controlli Media</h2>
        <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
          <div style={{ textAlign: 'center' }}>
            <Icons.Media.Start size={IconSizes.xl} color={IconColors.success} />
            <p>Start</p>
          </div>
          <div style={{ textAlign: 'center' }}>
            <Icons.Media.Pause size={IconSizes.xl} color={IconColors.warning} />
            <p>Pause</p>
          </div>
          <div style={{ textAlign: 'center' }}>
            <Icons.Media.Stop size={IconSizes.xl} color={IconColors.error} />
            <p>Stop</p>
          </div>
        </div>
      </section>

      {/* Window Controls */}
      <section style={{ marginBottom: '40px' }}>
        <h2>🪟 Controlli Finestra</h2>
        <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
          <div style={{ textAlign: 'center' }}>
            <Icons.Window.Close size={IconSizes.xl} color={IconColors.error} />
            <p>Close</p>
          </div>
          <div style={{ textAlign: 'center' }}>
            <Icons.Window.Minimize size={IconSizes.xl} />
            <p>Minimize</p>
          </div>
          <div style={{ textAlign: 'center' }}>
            <Icons.Window.Maximize size={IconSizes.xl} />
            <p>Maximize</p>
          </div>
        </div>
      </section>

      {/* Navigation */}
      <section style={{ marginBottom: '40px' }}>
        <h2>🧭 Navigazione</h2>
        <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
          <div style={{ textAlign: 'center' }}>
            <Icons.Navigation.Home size={IconSizes.xl} color={IconColors.primary} />
            <p>Home</p>
          </div>
          <div style={{ textAlign: 'center' }}>
            <Icons.Navigation.Left size={IconSizes.xl} />
            <p>Left</p>
          </div>
          <div style={{ textAlign: 'center' }}>
            <Icons.Navigation.Right size={IconSizes.xl} />
            <p>Right</p>
          </div>
        </div>
      </section>

      {/* Status */}
      <section style={{ marginBottom: '40px' }}>
        <h2>✓ Stato e Feedback</h2>
        <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
          <div style={{ textAlign: 'center' }}>
            <Icons.Status.Success size={IconSizes.xl} color={IconColors.success} />
            <p>Success</p>
          </div>
          <div style={{ textAlign: 'center' }}>
            <Icons.Status.Error size={IconSizes.xl} color={IconColors.error} />
            <p>Error</p>
          </div>
          <div style={{ textAlign: 'center' }}>
            <Icons.Status.Warning size={IconSizes.xl} color={IconColors.warning} />
            <p>Warning</p>
          </div>
          <div style={{ textAlign: 'center' }}>
            <Icons.Status.Info size={IconSizes.xl} color={IconColors.info} />
            <p>Info</p>
          </div>
        </div>
      </section>

      {/* Statistics */}
      <section style={{ marginBottom: '40px' }}>
        <h2>📊 Statistiche</h2>
        <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
          <div style={{ textAlign: 'center' }}>
            <Icons.Stats.BarChart size={IconSizes.xl} color={IconColors.primary} />
            <p>Bar Chart</p>
          </div>
          <div style={{ textAlign: 'center' }}>
            <Icons.Stats.PieChart size={IconSizes.xl} color={IconColors.primary} />
            <p>Pie Chart</p>
          </div>
          <div style={{ textAlign: 'center' }}>
            <Icons.Stats.Activity size={IconSizes.xl} color={IconColors.success} />
            <p>Activity</p>
          </div>
        </div>
      </section>

      {/* Utility */}
      <section style={{ marginBottom: '40px' }}>
        <h2>🔧 Utility</h2>
        <div style={{ display: 'flex', gap: '20px', alignItems: 'center', flexWrap: 'wrap' }}>
          <div style={{ textAlign: 'center' }}>
            <Icons.Utility.Trash size={IconSizes.xl} color={IconColors.error} />
            <p>Trash</p>
          </div>
          <div style={{ textAlign: 'center' }}>
            <Icons.Utility.Save size={IconSizes.xl} color={IconColors.success} />
            <p>Save</p>
          </div>
          <div style={{ textAlign: 'center' }}>
            <Icons.Utility.Download size={IconSizes.xl} />
            <p>Download</p>
          </div>
          <div style={{ textAlign: 'center' }}>
            <Icons.Utility.Upload size={IconSizes.xl} />
            <p>Upload</p>
          </div>
          <div style={{ textAlign: 'center' }}>
            <Icons.Utility.Refresh size={IconSizes.xl} />
            <p>Refresh</p>
          </div>
        </div>
      </section>

      {/* Animated Icons */}
      <section style={{ marginBottom: '40px' }}>
        <h2>🎬 Icone Animate (sostituiscono GIF)</h2>
        <div style={{ display: 'flex', gap: '40px', alignItems: 'center', flexWrap: 'wrap' }}>
          <div style={{ textAlign: 'center' }}>
            <LoadingIcon size={IconSizes.xxl} color={IconColors.primary} />
            <p>Loading</p>
            <small>(era loading.gif)</small>
          </div>
          <div style={{ textAlign: 'center' }}>
            <LoveIcon size={IconSizes.xxl} />
            <p>Love</p>
            <small>(era love.gif)</small>
          </div>
          <div style={{ textAlign: 'center' }}>
            <StatiIcon size={IconSizes.xxl} color={IconColors.primary} />
            <p>Stati</p>
            <small>(era stati.gif)</small>
          </div>
          <div style={{ textAlign: 'center' }}>
            <StatisticsIcon size={IconSizes.xxl} color={IconColors.success} />
            <p>Statistics</p>
            <small>(era statistics.gif)</small>
          </div>
          <div style={{ textAlign: 'center' }}>
            <LoadingDotsIcon />
            <p>Loading Dots</p>
            <small>(nuovo)</small>
          </div>
        </div>
      </section>

      {/* Size Examples */}
      <section style={{ marginBottom: '40px' }}>
        <h2>📏 Dimensioni Standard</h2>
        <div style={{ display: 'flex', gap: '20px', alignItems: 'flex-end' }}>
          <div style={{ textAlign: 'center' }}>
            <Icons.Shipping.Package size={IconSizes.xs} />
            <p>XS (12px)</p>
          </div>
          <div style={{ textAlign: 'center' }}>
            <Icons.Shipping.Package size={IconSizes.sm} />
            <p>SM (16px)</p>
          </div>
          <div style={{ textAlign: 'center' }}>
            <Icons.Shipping.Package size={IconSizes.md} />
            <p>MD (20px)</p>
          </div>
          <div style={{ textAlign: 'center' }}>
            <Icons.Shipping.Package size={IconSizes.lg} />
            <p>LG (24px)</p>
          </div>
          <div style={{ textAlign: 'center' }}>
            <Icons.Shipping.Package size={IconSizes.xl} />
            <p>XL (32px)</p>
          </div>
          <div style={{ textAlign: 'center' }}>
            <Icons.Shipping.Package size={IconSizes.xxl} />
            <p>XXL (48px)</p>
          </div>
        </div>
      </section>

      {/* Color Examples */}
      <section style={{ marginBottom: '40px' }}>
        <h2>🎨 Colori Standard</h2>
        <div style={{ display: 'flex', gap: '20px', alignItems: 'center', flexWrap: 'wrap' }}>
          <div style={{ textAlign: 'center' }}>
            <Icons.Shipping.Package size={IconSizes.xl} color={IconColors.primary} />
            <p>Primary</p>
          </div>
          <div style={{ textAlign: 'center' }}>
            <Icons.Shipping.Package size={IconSizes.xl} color={IconColors.success} />
            <p>Success</p>
          </div>
          <div style={{ textAlign: 'center' }}>
            <Icons.Shipping.Package size={IconSizes.xl} color={IconColors.warning} />
            <p>Warning</p>
          </div>
          <div style={{ textAlign: 'center' }}>
            <Icons.Shipping.Package size={IconSizes.xl} color={IconColors.error} />
            <p>Error</p>
          </div>
          <div style={{ textAlign: 'center' }}>
            <Icons.Shipping.Package size={IconSizes.xl} color={IconColors.info} />
            <p>Info</p>
          </div>
          <div style={{ textAlign: 'center' }}>
            <Icons.Shipping.Package size={IconSizes.xl} color={IconColors.muted} />
            <p>Muted</p>
          </div>
        </div>
      </section>

      <section style={{ marginTop: '60px', padding: '20px', background: '#f0f0f0', borderRadius: '8px' }}>
        <h3>💡 Note d'uso</h3>
        <ul style={{ lineHeight: '1.8' }}>
          <li>Tutte le icone sono <strong>SVG vettoriali</strong> - perfette su display HiDPI/Retina</li>
          <li>Le animazioni CSS sostituiscono i vecchi GIF (90% più leggere)</li>
          <li>Usa <code>@icons</code> alias per import rapidi</li>
          <li>Tree-shaking automatico - solo icone usate nel bundle</li>
          <li>Consulta <code>assets/ICONS_README.md</code> per documentazione completa</li>
        </ul>
      </section>
    </div>
  );
};

export default IconShowcase;
