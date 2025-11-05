import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { RootState } from '../store/store';
import { toggleSidebar } from '../store/slices/sidebarSlice';
import './SidebarToggle.css';

const SidebarToggle: React.FC = () => {
  const dispatch = useDispatch();
  const collapsed = useSelector((state: RootState) => state.sidebar.collapsed);

  const handleToggle = () => {
    dispatch(toggleSidebar());
  };

  return (
    <button
      className={`sidebar-toggle ${collapsed ? 'collapsed' : ''}`}
      onClick={handleToggle}
      title={collapsed ? 'Espandi sidebar (Ctrl+B)' : 'Riduci sidebar (Ctrl+B)'}
      aria-label={collapsed ? 'Espandi sidebar' : 'Riduci sidebar'}
    >
      <span className="toggle-icon">
        {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
      </span>
    </button>
  );
};

export default SidebarToggle;
