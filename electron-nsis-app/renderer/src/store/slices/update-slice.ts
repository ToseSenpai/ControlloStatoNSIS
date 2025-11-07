import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { UpdateInfo, DownloadProgress, UpdateState } from '../../../../shared/types/update-types';

const initialState: UpdateState = {
  checking: false,
  available: false,
  downloaded: false,
  error: null,
  info: null,
  progress: null
};

const updateSlice = createSlice({
  name: 'update',
  initialState,
  reducers: {
    setChecking: (state, action: PayloadAction<boolean>) => {
      state.checking = action.payload;
    },
    setUpdateAvailable: (state, action: PayloadAction<UpdateInfo>) => {
      state.available = true;
      state.info = action.payload;
      state.checking = false;
    },
    setDownloadProgress: (state, action: PayloadAction<DownloadProgress>) => {
      state.progress = action.payload;
    },
    setUpdateDownloaded: (state, action: PayloadAction<UpdateInfo>) => {
      state.downloaded = true;
      state.info = action.payload;
      state.progress = null;
    },
    setUpdateError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
      state.checking = false;
    },
    resetUpdate: () => {
      return initialState;
    }
  }
});

export const {
  setChecking,
  setUpdateAvailable,
  setDownloadProgress,
  setUpdateDownloaded,
  setUpdateError,
  resetUpdate
} = updateSlice.actions;

export default updateSlice.reducer;
