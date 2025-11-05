import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface SidebarState {
  collapsed: boolean;
  width: number;
}

const initialState: SidebarState = {
  collapsed: false,
  width: 240,
};

// Load sidebar state from localStorage
const loadSidebarState = (): Partial<SidebarState> => {
  try {
    const savedState = localStorage.getItem('sidebarState');
    if (savedState) {
      return JSON.parse(savedState);
    }
  } catch (error) {
    console.error('Failed to load sidebar state:', error);
  }
  return {};
};

// Initialize with saved state
const savedState = loadSidebarState();
const sidebarInitialState: SidebarState = {
  ...initialState,
  ...savedState,
};

export const sidebarSlice = createSlice({
  name: 'sidebar',
  initialState: sidebarInitialState,
  reducers: {
    toggleSidebar: (state) => {
      state.collapsed = !state.collapsed;
      state.width = state.collapsed ? 40 : 240;

      // Save to localStorage
      try {
        localStorage.setItem('sidebarState', JSON.stringify({
          collapsed: state.collapsed,
          width: state.width,
        }));
      } catch (error) {
        console.error('Failed to save sidebar state:', error);
      }
    },
    setSidebarCollapsed: (state, action: PayloadAction<boolean>) => {
      state.collapsed = action.payload;
      state.width = action.payload ? 40 : 240;

      // Save to localStorage
      try {
        localStorage.setItem('sidebarState', JSON.stringify({
          collapsed: state.collapsed,
          width: state.width,
        }));
      } catch (error) {
        console.error('Failed to save sidebar state:', error);
      }
    },
  },
});

export const { toggleSidebar, setSidebarCollapsed } = sidebarSlice.actions;
export default sidebarSlice.reducer;
