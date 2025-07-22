# windows_config.py
# Windows-specific configuration for ControlloStatoNSIS

import os
import sys
from pathlib import Path

# Windows-specific paths
def get_windows_app_data():
    """Get Windows AppData path."""
    return os.path.join(os.environ.get('APPDATA', ''), 'ControlloStatoNSIS')

def get_windows_documents():
    """Get Windows Documents path."""
    return os.path.join(os.environ.get('USERPROFILE', ''), 'Documents', 'ControlloStatoNSIS')

def get_windows_temp():
    """Get Windows temp path."""
    return os.path.join(os.environ.get('TEMP', ''), 'ControlloStatoNSIS')

# Windows-specific settings
WINDOWS_CONFIG = {
    'app_data_dir': get_windows_app_data(),
    'documents_dir': get_windows_documents(),
    'temp_dir': get_windows_temp(),
    'log_dir': os.path.join(get_windows_app_data(), 'logs'),
    'config_dir': os.path.join(get_windows_app_data(), 'config'),
    'cache_dir': os.path.join(get_windows_app_data(), 'cache'),
}

# Windows-specific UI settings
WINDOWS_UI_CONFIG = {
    'theme': 'windows',
    'font_family': 'Segoe UI',
    'font_size': 9,
    'window_style': 'windowsvista',
    'taskbar_icon': True,
    'high_dpi_aware': True,
}

# Windows-specific web automation settings
WINDOWS_WEB_CONFIG = {
    'chrome_path': r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    'edge_path': r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    'default_browser': 'chrome',
    'webdriver_path': None,
}

def ensure_windows_directories():
    """Ensure Windows-specific directories exist."""
    for dir_path in WINDOWS_CONFIG.values():
        Path(dir_path).mkdir(parents=True, exist_ok=True)

def get_windows_version():
    """Get Windows version information."""
    try:
        import platform
        return platform.platform()
    except:
        return "Windows (version unknown)"

def is_windows_10_or_later():
    """Check if running on Windows 10 or later."""
    try:
        import platform
        version = platform.version()
        major_version = int(version.split('.')[0])
        return major_version >= 10
    except:
        return True  # Assume modern Windows if detection fails

def setup_windows_environment():
    """Setup Windows-specific environment."""
    # Ensure directories exist
    ensure_windows_directories()
    
    # Set high DPI awareness
    if is_windows_10_or_later():
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per Monitor DPI Aware
        except:
            pass
    
    # Set environment variables
    os.environ['CONTROLLO_STATO_NSIS_APP_DATA'] = WINDOWS_CONFIG['app_data_dir']
    os.environ['CONTROLLO_STATO_NSIS_DOCUMENTS'] = WINDOWS_CONFIG['documents_dir']
    os.environ['CONTROLLO_STATO_NSIS_TEMP'] = WINDOWS_CONFIG['temp_dir']

def get_windows_log_path():
    """Get Windows-specific log path."""
    return os.path.join(WINDOWS_CONFIG['log_dir'], 'nsis_app.log')

def get_windows_config_path():
    """Get Windows-specific config path."""
    return os.path.join(WINDOWS_CONFIG['config_dir'], 'app_config.ini') 