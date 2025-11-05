import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface ProgressState {
  current: number;
  total: number;
  percentage: number;
  status: string;
  isProcessing: boolean;
}

interface BadgeData {
  annullate: number;
  aperte: number;
  chiuse: number;
  inLavorazione: number;
  inviate: number;
  eccezioni: number;
}

interface UISliceState {
  progress: ProgressState;
  badges: BadgeData;
  logs: string[];
  showLogs: boolean;
  webViewUrl: string;
  webViewLoading: boolean;
}

const initialState: UISliceState = {
  progress: {
    current: 0,
    total: 0,
    percentage: 0,
    status: '',
    isProcessing: false
  },
  badges: {
    annullate: 0,
    aperte: 0,
    chiuse: 0,
    inLavorazione: 0,
    inviate: 0,
    eccezioni: 0
  },
  logs: [],
  showLogs: false,
  webViewUrl: '',
  webViewLoading: false
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    updateProgress: (state, action: PayloadAction<{ current: number; total: number }>) => {
      state.progress.current = action.payload.current;
      state.progress.total = action.payload.total;
      state.progress.percentage = action.payload.total > 0
        ? Math.round((action.payload.current / action.payload.total) * 100)
        : 0;
    },
    setProcessing: (state, action: PayloadAction<boolean>) => {
      state.progress.isProcessing = action.payload;
      if (!action.payload) {
        state.progress.status = '';
      }
    },
    setStatus: (state, action: PayloadAction<string>) => {
      state.progress.status = action.payload;
    },
    updateBadges: (state, action: PayloadAction<Partial<BadgeData>>) => {
      state.badges = { ...state.badges, ...action.payload };
    },
    resetBadges: (state) => {
      state.badges = initialState.badges;
    },
    addLog: (state, action: PayloadAction<string>) => {
      state.logs.push(action.payload);
      // Keep only last 1000 logs
      if (state.logs.length > 1000) {
        state.logs = state.logs.slice(-1000);
      }
    },
    clearLogs: (state) => {
      state.logs = [];
    },
    toggleLogs: (state) => {
      state.showLogs = !state.showLogs;
    },
    setShowLogs: (state, action: PayloadAction<boolean>) => {
      state.showLogs = action.payload;
    },
    setWebViewUrl: (state, action: PayloadAction<string>) => {
      state.webViewUrl = action.payload;
    },
    setWebViewLoading: (state, action: PayloadAction<boolean>) => {
      state.webViewLoading = action.payload;
    },
    resetUI: (state) => {
      return initialState;
    }
  }
});

export const {
  updateProgress,
  setProcessing,
  setStatus,
  updateBadges,
  resetBadges,
  addLog,
  clearLogs,
  toggleLogs,
  setShowLogs,
  setWebViewUrl,
  setWebViewLoading,
  resetUI
} = uiSlice.actions;

export default uiSlice.reducer;
