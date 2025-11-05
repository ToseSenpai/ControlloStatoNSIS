/**
 * Sistema Icone Centralizzato
 *
 * Questo file esporta tutte le icone utilizzate nell'applicazione.
 * Utilizza Lucide React per icone SVG scalabili e moderne.
 *
 * Vantaggi:
 * - Icone vettoriali (perfette su tutti i display, inclusi HiDPI/Retina)
 * - Consistenza visiva in tutta l'applicazione
 * - Facile manutenzione (un solo punto di gestione)
 * - Tree-shaking automatico (solo icone usate nel bundle)
 * - Dimensioni file ridotte
 */

import {
  // File e documenti
  FileText,
  File,
  FileSpreadsheet,
  Folder,
  FolderOpen,

  // Azioni
  Play,
  Pause,
  Square,
  X,
  Minimize,
  Maximize,
  Minus,
  Plus,

  // Navigazione
  Home,
  ChevronLeft,
  ChevronRight,
  ChevronUp,
  ChevronDown,
  ArrowLeft,
  ArrowRight,

  // Stato e feedback
  Loader2,
  CheckCircle,
  XCircle,
  AlertCircle,
  Info,
  AlertTriangle,

  // Dati e statistiche
  BarChart3,
  PieChart,
  TrendingUp,
  Activity,

  // Controlli
  Settings,
  Sliders,
  Menu,
  MoreVertical,
  MoreHorizontal,

  // Utility
  Trash2,
  Edit3,
  Save,
  Download,
  Upload,
  RefreshCw,
  Search,
  Filter,

  // Browser e web
  Chrome,
  Globe,
  ExternalLink,

  // Amore/Like (per animazioni)
  Heart,

  // Box e container
  Package,
  Box,
} from 'lucide-react';

import React from 'react';
import type { LucideProps } from 'lucide-react';

/**
 * Tipo per le proprietà delle icone
 * Estende le props di Lucide con dimensioni e colori standard
 */
export interface IconProps extends LucideProps {
  size?: number | string;
  color?: string;
  className?: string;
}

/**
 * Icone per File e Documenti
 */
export const FileIcons = {
  Text: FileText,
  Generic: File,
  Excel: FileSpreadsheet,
  Folder: Folder,
  FolderOpen: FolderOpen,
} as const;

/**
 * Icone per Controlli Media
 */
export const MediaIcons = {
  Start: Play,
  Pause: Pause,
  Stop: Square,
} as const;

/**
 * Icone per Controlli Finestra
 */
export const WindowIcons = {
  Close: X,
  Minimize: Minimize,
  Maximize: Maximize,
  Large: Maximize,
} as const;

/**
 * Icone per Navigazione
 */
export const NavigationIcons = {
  Home: Home,
  Left: ChevronLeft,
  Right: ChevronRight,
  Up: ChevronUp,
  Down: ChevronDown,
  ArrowLeft: ArrowLeft,
  ArrowRight: ArrowRight,
} as const;

/**
 * Icone per Loading e Stato
 */
export const StatusIcons = {
  Loading: Loader2,
  Success: CheckCircle,
  Error: XCircle,
  Warning: AlertTriangle,
  Info: Info,
  Alert: AlertCircle,
} as const;

/**
 * Icone per Statistiche
 */
export const StatIcons = {
  BarChart: BarChart3,
  PieChart: PieChart,
  Trending: TrendingUp,
  Activity: Activity,
  Statistics: BarChart3,
} as const;

/**
 * Icone per Controlli Generali
 */
export const ControlIcons = {
  Settings: Settings,
  Controls: Sliders,
  Menu: Menu,
  MoreVertical: MoreVertical,
  MoreHorizontal: MoreHorizontal,
} as const;

/**
 * Icone per Utility
 */
export const UtilityIcons = {
  Trash: Trash2,
  Edit: Edit3,
  Save: Save,
  Download: Download,
  Upload: Upload,
  Refresh: RefreshCw,
  Search: Search,
  Filter: Filter,
  Plus: Plus,
  Minus: Minus,
} as const;

/**
 * Icone per Browser
 */
export const BrowserIcons = {
  Chrome: Chrome,
  Globe: Globe,
  ExternalLink: ExternalLink,
} as const;

/**
 * Icone per Feedback e Animazioni
 */
export const FeedbackIcons = {
  Love: Heart,
  Heart: Heart,
} as const;

/**
 * Icone per Packaging e Stato Spedizioni
 */
export const ShippingIcons = {
  Package: Package,
  Box: Box,
  Stati: Package, // Mappa l'old "stati.gif" a Package icon
} as const;

/**
 * Mappa delle icone legacy -> moderne
 * Usato per migrare codice esistente
 */
export const LegacyIconMap = {
  'chrome.png': BrowserIcons.Chrome,
  'close.png': WindowIcons.Close,
  'controls.png': ControlIcons.Controls,
  'excel.png': FileIcons.Excel,
  'folder.png': FileIcons.Folder,
  'home.png': NavigationIcons.Home,
  'large.png': WindowIcons.Large,
  'minimize.png': WindowIcons.Minimize,
  'start.png': MediaIcons.Start,
  'stop.png': MediaIcons.Stop,
  'trash.png': UtilityIcons.Trash,
  'loading.gif': StatusIcons.Loading,
  'love.gif': FeedbackIcons.Love,
  'stati.gif': ShippingIcons.Stati,
  'statistics.gif': StatIcons.Statistics,
} as const;

/**
 * Esporta tutte le icone come oggetto unico
 */
export const Icons = {
  File: FileIcons,
  Media: MediaIcons,
  Window: WindowIcons,
  Navigation: NavigationIcons,
  Status: StatusIcons,
  Stats: StatIcons,
  Control: ControlIcons,
  Utility: UtilityIcons,
  Browser: BrowserIcons,
  Feedback: FeedbackIcons,
  Shipping: ShippingIcons,
  Legacy: LegacyIconMap,
} as const;

/**
 * Esporta tutte le icone individuali per import diretto
 */
export {
  // File
  FileText,
  File,
  FileSpreadsheet,
  Folder,
  FolderOpen,

  // Media
  Play,
  Pause,
  Square,

  // Window
  X,
  Minimize,
  Maximize,

  // Navigation
  Home,
  ChevronLeft,
  ChevronRight,
  ChevronUp,
  ChevronDown,
  ArrowLeft,
  ArrowRight,

  // Status
  Loader2,
  CheckCircle,
  XCircle,
  AlertCircle,
  AlertTriangle,
  Info,

  // Stats
  BarChart3,
  PieChart,
  TrendingUp,
  Activity,

  // Controls
  Settings,
  Sliders,
  Menu,
  MoreVertical,
  MoreHorizontal,

  // Utility
  Trash2,
  Edit3,
  Save,
  Download,
  Upload,
  RefreshCw,
  Search,
  Filter,
  Plus,
  Minus,

  // Browser
  Chrome,
  Globe,
  ExternalLink,

  // Feedback
  Heart,

  // Shipping
  Package,
  Box,
};

/**
 * Dimensioni standard per le icone nell'app
 */
export const IconSizes = {
  xs: 12,
  sm: 16,
  md: 20,
  lg: 24,
  xl: 32,
  xxl: 48,
} as const;

/**
 * Colori standard per le icone
 */
export const IconColors = {
  primary: '#2563eb',
  secondary: '#64748b',
  success: '#22c55e',
  warning: '#f59e0b',
  error: '#ef4444',
  info: '#3b82f6',
  muted: '#94a3b8',
} as const;

export default Icons;
