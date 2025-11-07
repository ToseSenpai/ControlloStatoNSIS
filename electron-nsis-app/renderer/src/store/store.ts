import { configureStore } from '@reduxjs/toolkit';
import appReducer from './slices/app-slice';
import uiReducer from './slices/ui-slice';
import dataReducer from './slices/data-slice';
import sidebarReducer from './slices/sidebarSlice';
import updateReducer from './slices/update-slice';

export const store = configureStore({
  reducer: {
    app: appReducer,
    ui: uiReducer,
    data: dataReducer,
    sidebar: sidebarReducer,
    update: updateReducer
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false
    })
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
