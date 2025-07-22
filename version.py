# version.py
# Version management for ControlloStatoNSIS

__version__ = "2.0.0"
__author__ = "Developer"
__email__ = "developer@example.com"
__description__ = "Applicazione desktop per automatizzare il controllo dello stato di richieste NSIS"

def get_version():
    """Get the current version."""
    return __version__

def get_version_info():
    """Get version information as a dictionary."""
    return {
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "description": __description__
    }

def is_development_version():
    """Check if this is a development version."""
    return "dev" in __version__ or "alpha" in __version__ or "beta" in __version__

def is_stable_version():
    """Check if this is a stable version."""
    return not is_development_version() 