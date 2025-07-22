# main_window/state_manager.py
# State Machine implementation for application states

from enum import Enum
from typing import List, Callable, Optional
from PyQt6 import QtCore
import logging

class AppState(Enum):
    """Enumeration of possible application states."""
    IDLE = "idle"
    LOADING = "loading"
    PROCESSING = "processing"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"
    STOPPING = "stopping"

class StateTransition:
    """Represents a state transition with validation."""
    def __init__(self, from_state: AppState, to_state: AppState, condition: Optional[Callable] = None):
        self.from_state = from_state
        self.to_state = to_state
        self.condition = condition or (lambda: True)

class StateManager(QtCore.QObject):
    """Manages application state transitions and notifies observers of changes."""
    
    stateChanged = QtCore.pyqtSignal(AppState, AppState)  # old_state, new_state
    stateTransitionFailed = QtCore.pyqtSignal(AppState, AppState, str)  # from_state, to_state, reason
    
    def __init__(self):
        super().__init__()
        self._current_state = AppState.IDLE
        self._previous_state = AppState.IDLE
        self._observers: List[Callable] = []
        self._transitions: List[StateTransition] = []
        self._logger = logging.getLogger(__name__)
        
        # Define valid state transitions
        self._setup_transitions()
    
    def _setup_transitions(self):
        """Setup valid state transitions."""
        transitions = [
            # From IDLE
            StateTransition(AppState.IDLE, AppState.LOADING),
            StateTransition(AppState.IDLE, AppState.ERROR),
            
            # From LOADING
            StateTransition(AppState.LOADING, AppState.PROCESSING),
            StateTransition(AppState.LOADING, AppState.ERROR),
            StateTransition(AppState.LOADING, AppState.IDLE),
            
            # From PROCESSING
            StateTransition(AppState.PROCESSING, AppState.PAUSED),
            StateTransition(AppState.PROCESSING, AppState.COMPLETED),
            StateTransition(AppState.PROCESSING, AppState.ERROR),
            StateTransition(AppState.PROCESSING, AppState.STOPPING),
            
            # From PAUSED
            StateTransition(AppState.PAUSED, AppState.PROCESSING),
            StateTransition(AppState.PAUSED, AppState.IDLE),
            StateTransition(AppState.PAUSED, AppState.ERROR),
            
            # From COMPLETED
            StateTransition(AppState.COMPLETED, AppState.IDLE),
            StateTransition(AppState.COMPLETED, AppState.LOADING),
            
            # From ERROR
            StateTransition(AppState.ERROR, AppState.IDLE),
            StateTransition(AppState.ERROR, AppState.LOADING),
            
            # From STOPPING
            StateTransition(AppState.STOPPING, AppState.IDLE),
            StateTransition(AppState.STOPPING, AppState.ERROR),
        ]
        
        self._transitions = transitions
    
    @property
    def current_state(self) -> AppState:
        """Get current application state."""
        return self._current_state
    
    @property
    def previous_state(self) -> AppState:
        """Get previous application state."""
        return self._previous_state
    
    def can_transition_to(self, new_state: AppState) -> bool:
        """Check if transition to new state is valid."""
        for transition in self._transitions:
            if (transition.from_state == self._current_state and 
                transition.to_state == new_state):
                return transition.condition()
        return False
    
    def transition_to(self, new_state: AppState) -> bool:
        """Attempt to transition to new state."""
        if not self.can_transition_to(new_state):
            reason = f"Invalid transition from {self._current_state.value} to {new_state.value}"
            self._logger.warning(reason)
            self.stateTransitionFailed.emit(self._current_state, new_state, reason)
            return False
        
        old_state = self._current_state
        self._previous_state = old_state
        self._current_state = new_state
        
        self._logger.info(f"State transition: {old_state.value} -> {new_state.value}")
        self.stateChanged.emit(old_state, new_state)
        
        # Notify observers
        for observer in self._observers:
            try:
                observer(old_state, new_state)
            except Exception as e:
                self._logger.error(f"Error in state observer: {e}")
        
        return True
    
    def add_observer(self, observer: Callable[[AppState, AppState], None]):
        """Add an observer to be notified of state changes."""
        self._observers.append(observer)
    
    def remove_observer(self, observer: Callable[[AppState, AppState], None]):
        """Remove an observer."""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def is_processing(self) -> bool:
        """Check if application is in processing state."""
        return self._current_state in [AppState.PROCESSING, AppState.PAUSED]
    
    def is_idle(self) -> bool:
        """Check if application is idle."""
        return self._current_state == AppState.IDLE
    
    def can_start_processing(self) -> bool:
        """Check if processing can be started."""
        return self._current_state in [AppState.IDLE, AppState.COMPLETED]
    
    def can_stop_processing(self) -> bool:
        """Check if processing can be stopped."""
        return self._current_state in [AppState.PROCESSING, AppState.PAUSED]
    
    def get_available_transitions(self) -> List[AppState]:
        """Get list of available transitions from current state."""
        available = []
        for transition in self._transitions:
            if (transition.from_state == self._current_state and 
                transition.condition()):
                available.append(transition.to_state)
        return available 