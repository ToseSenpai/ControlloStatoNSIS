import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export type AppState = 'IDLE' | 'LOADING' | 'PROCESSING' | 'COMPLETED' | 'ERROR';

interface AppSliceState {
  state: AppState;
  isLoading: boolean;
  error: string | null;
}

const initialState: AppSliceState = {
  state: 'IDLE',
  isLoading: false,
  error: null
};

const appSlice = createSlice({
  name: 'app',
  initialState,
  reducers: {
    setState: (state, action: PayloadAction<AppState>) => {
      state.state = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
      if (action.payload) {
        state.state = 'ERROR';
      }
    },
    resetApp: (state) => {
      state.state = 'IDLE';
      state.isLoading = false;
      state.error = null;
    }
  }
});

export const { setState, setLoading, setError, resetApp } = appSlice.actions;
export default appSlice.reducer;
