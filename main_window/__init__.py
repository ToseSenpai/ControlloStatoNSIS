# main_window/__init__.py
# Package initialization for main_window module

from .app import App
from .worker import Worker
from .excel_handler import ExcelHandler
from .web_automation import WebAutomation
from .ui_manager import UIManager
from .state_manager import StateManager

__all__ = [
    'App',
    'Worker', 
    'ExcelHandler',
    'WebAutomation',
    'UIManager',
    'StateManager'
]

__version__ = "2.0.0" 