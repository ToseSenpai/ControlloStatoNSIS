# tests/test_state_manager.py
# Tests for state_manager module

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main_window.state_manager import StateManager, AppState


class TestStateManager:
    """Test StateManager class."""
    
    def setup_method(self):
        """Setup test method."""
        self.state_manager = StateManager()
    
    def test_initial_state(self):
        """Test initial state is IDLE."""
        assert self.state_manager.current_state == AppState.IDLE
    
    def test_transition_to_loading(self):
        """Test transition to LOADING state."""
        self.state_manager.transition_to(AppState.LOADING)
        assert self.state_manager.current_state == AppState.LOADING
    
    def test_transition_to_processing(self):
        """Test transition to PROCESSING state."""
        self.state_manager.transition_to(AppState.LOADING)
        self.state_manager.transition_to(AppState.PROCESSING)
        assert self.state_manager.current_state == AppState.PROCESSING
    
    def test_transition_to_completed(self):
        """Test transition to COMPLETED state."""
        self.state_manager.transition_to(AppState.LOADING)
        self.state_manager.transition_to(AppState.PROCESSING)
        self.state_manager.transition_to(AppState.COMPLETED)
        assert self.state_manager.current_state == AppState.COMPLETED
    
    def test_invalid_transition(self):
        """Test invalid state transition returns False."""
        # IDLE -> PROCESSING is not a valid transition
        result = self.state_manager.transition_to(AppState.PROCESSING)
        assert result == False
    
    def test_can_start_processing(self):
        """Test can_start_processing method."""
        # Should be True in IDLE state
        assert self.state_manager.can_start_processing() is True
        
        # Should be False in other states
        self.state_manager.transition_to(AppState.LOADING)
        assert self.state_manager.can_start_processing() is False
    
    def test_can_stop_processing(self):
        """Test can_stop_processing method."""
        # Should be False in IDLE state
        assert self.state_manager.can_stop_processing() is False
        
        # Should be True in PROCESSING state
        self.state_manager.transition_to(AppState.LOADING)
        self.state_manager.transition_to(AppState.PROCESSING)
        assert self.state_manager.can_stop_processing() is True


class TestAppState:
    """Test AppState enum."""
    
    def test_state_values(self):
        """Test AppState enum values."""
        assert AppState.IDLE.value == "idle"
        assert AppState.LOADING.value == "loading"
        assert AppState.PROCESSING.value == "processing"
        assert AppState.COMPLETED.value == "completed"
        assert AppState.ERROR.value == "error"
        assert AppState.STOPPING.value == "stopping" 