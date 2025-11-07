/**
 * TypeScript types for electron-updater auto-update system
 */

export interface UpdateInfo {
  version: string;
  releaseNotes?: string;
  releaseDate?: string;
  files?: any[];
}

export interface DownloadProgress {
  percent: number;
  transferred: number;
  total: number;
  bytesPerSecond: number;
}

export interface UpdateState {
  checking: boolean;
  available: boolean;
  downloaded: boolean;
  error: string | null;
  info: UpdateInfo | null;
  progress: DownloadProgress | null;
}
