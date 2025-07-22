# tests/test_config.py
# Tests for config module

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    URL_NSIS,
    MAX_RETRIES,
    FETCH_TIMEOUT_MS,
    COLOR_APERTA,
    COLOR_CHIUSA,
    COL_RICERCA,
    COL_STATO
)


class TestConfig:
    """Test configuration constants."""
    
    def test_url_nsis(self):
        """Test NSIS URL is valid."""
        assert URL_NSIS is not None
        assert isinstance(URL_NSIS, str)
        assert URL_NSIS.startswith("http")
    
    def test_max_retries(self):
        """Test max retries is positive integer."""
        assert isinstance(MAX_RETRIES, int)
        assert MAX_RETRIES > 0
    
    def test_fetch_timeout(self):
        """Test fetch timeout is positive integer."""
        assert isinstance(FETCH_TIMEOUT_MS, int)
        assert FETCH_TIMEOUT_MS > 0
    
    def test_colors(self):
        """Test color constants are valid hex colors."""
        assert COLOR_APERTA.startswith("#")
        assert COLOR_CHIUSA.startswith("#")
        assert len(COLOR_APERTA) == 7  # #RRGGBB
        assert len(COLOR_CHIUSA) == 7
    
    def test_column_names(self):
        """Test column name constants are strings."""
        assert isinstance(COL_RICERCA, str)
        assert isinstance(COL_STATO, str)
        assert len(COL_RICERCA) > 0
        assert len(COL_STATO) > 0 