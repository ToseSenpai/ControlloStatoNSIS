import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface ExcelData {
  filePath: string;
  codes: string[];
  columns: string[];
  results: Map<string, any>;
}

interface DataSliceState {
  excel: ExcelData | null;
  selectedFilePath: string | null;
}

const initialState: DataSliceState = {
  excel: null,
  selectedFilePath: null
};

const dataSlice = createSlice({
  name: 'data',
  initialState,
  reducers: {
    setFilePath: (state, action: PayloadAction<string>) => {
      state.selectedFilePath = action.payload;
    },
    setExcelData: (state, action: PayloadAction<ExcelData>) => {
      state.excel = action.payload;
    },
    clearExcelData: (state) => {
      state.excel = null;
      state.selectedFilePath = null;
    },
    updateResult: (state, action: PayloadAction<{ code: string; result: any }>) => {
      if (state.excel) {
        if (!state.excel.results) {
          state.excel.results = new Map();
        }
        state.excel.results.set(action.payload.code, action.payload.result);
      }
    },
    resetData: (state) => {
      return initialState;
    }
  }
});

export const {
  setFilePath,
  setExcelData,
  clearExcelData,
  updateResult,
  resetData
} = dataSlice.actions;

export default dataSlice.reducer;
