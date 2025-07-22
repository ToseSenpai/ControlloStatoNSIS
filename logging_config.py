# logging_config.py
# Configuration for application logging

import logging
import os
from datetime import datetime

def setup_logging(log_level=logging.INFO):
    """Setup logging configuration for the application."""
    
    # Use Windows-specific paths if available
    try:
        from windows_config import WINDOWS_CONFIG
        logs_dir = WINDOWS_CONFIG['log_dir']
    except ImportError:
        # Fallback to local logs directory
        logs_dir = "logs"
    
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = os.path.join(logs_dir, f"nsis_app_{timestamp}.log")
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()  # Console output
        ]
    )
    
    # Set specific logger levels
    logging.getLogger('PyQt6').setLevel(logging.WARNING)
    logging.getLogger('PyQt6.QtWebEngine').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

def get_logger(name):
    """Get a logger instance for a specific module."""
    return logging.getLogger(name) 