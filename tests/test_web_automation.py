# tests/test_web_automation.py
# Unit tests for WebAutomation module

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, QTimer
from main_window.web_automation import WebAutomation


class TestWebAutomation:
    """Test cases for WebAutomation class."""

    def setup_method(self):
        """Setup test fixtures."""
        self.web_automation = WebAutomation()

    def test_init(self):
        """Test WebAutomation initialization."""
        assert self.web_automation is not None
        assert hasattr(self.web_automation, 'load_url')
        assert hasattr(self.web_automation, 'fetch_nsis_status')

    def test_set_web_view(self):
        """Test setting web view."""
        mock_web_view = Mock()
        self.web_automation.set_web_view(mock_web_view)
        assert self.web_automation.web_view == mock_web_view

    def test_set_web_view_none(self):
        """Test setting web view to None."""
        self.web_automation.set_web_view(None)
        assert self.web_automation.web_view is None

    def test_load_url_success(self):
        """Test successful URL loading."""
        mock_web_view = Mock()
        self.web_automation.set_web_view(mock_web_view)
        
        url = "https://www.impresa.gov.it/intro/info/news.html"
        result = self.web_automation.load_url(url)
        
        assert result is True
        mock_web_view.load.assert_called_once_with(QUrl(url))

    def test_load_url_no_web_view(self):
        """Test URL loading without web view."""
        self.web_automation.web_view = None
        
        url = "https://www.impresa.gov.it/intro/info/news.html"
        result = self.web_automation.load_url(url)
        
        assert result is False

    def test_load_url_invalid_url(self):
        """Test URL loading with invalid URL."""
        mock_web_view = Mock()
        self.web_automation.set_web_view(mock_web_view)
        
        result = self.web_automation.load_url("invalid-url")
        
        assert result is False
        mock_web_view.load.assert_not_called()

    def test_load_url_empty_url(self):
        """Test URL loading with empty URL."""
        mock_web_view = Mock()
        self.web_automation.set_web_view(mock_web_view)
        
        result = self.web_automation.load_url("")
        
        assert result is False
        mock_web_view.load.assert_not_called()

    def test_load_url_none_url(self):
        """Test URL loading with None URL."""
        mock_web_view = Mock()
        self.web_automation.set_web_view(mock_web_view)
        
        result = self.web_automation.load_url(None)
        
        assert result is False
        mock_web_view.load.assert_not_called()

    @patch('main_window.web_automation.QTimer')
    def test_wait_for_load_success(self, mock_timer_class):
        """Test successful wait for page load."""
        mock_timer = Mock()
        mock_timer_class.return_value = mock_timer
        
        mock_web_view = Mock()
        mock_web_view.page().isLoading.return_value = False
        self.web_automation.set_web_view(mock_web_view)
        
        result = self.web_automation._wait_for_load(timeout_ms=1000)
        
        assert result is True
        mock_timer.start.assert_called_once()

    @patch('main_window.web_automation.QTimer')
    def test_wait_for_load_timeout(self, mock_timer_class):
        """Test wait for page load with timeout."""
        mock_timer = Mock()
        mock_timer_class.return_value = mock_timer
        
        mock_web_view = Mock()
        mock_web_view.page().isLoading.return_value = True
        self.web_automation.set_web_view(mock_web_view)
        
        result = self.web_automation._wait_for_load(timeout_ms=100)
        
        assert result is False
        mock_timer.start.assert_called_once()

    def test_wait_for_load_no_web_view(self):
        """Test wait for page load without web view."""
        self.web_automation.web_view = None
        
        result = self.web_automation._wait_for_load(timeout_ms=1000)
        
        assert result is False

    def test_execute_javascript_success(self):
        """Test successful JavaScript execution."""
        mock_web_view = Mock()
        mock_page = Mock()
        mock_web_view.page.return_value = mock_page
        self.web_automation.set_web_view(mock_web_view)
        
        script = "document.title"
        result = self.web_automation._execute_javascript(script)
        
        assert result is True
        mock_page.runJavaScript.assert_called_once_with(script, self.web_automation._handle_js_result)

    def test_execute_javascript_no_web_view(self):
        """Test JavaScript execution without web view."""
        self.web_automation.web_view = None
        
        script = "document.title"
        result = self.web_automation._execute_javascript(script)
        
        assert result is False

    def test_execute_javascript_empty_script(self):
        """Test JavaScript execution with empty script."""
        mock_web_view = Mock()
        self.web_automation.set_web_view(mock_web_view)
        
        result = self.web_automation._execute_javascript("")
        
        assert result is False

    def test_handle_js_result_success(self):
        """Test successful JavaScript result handling."""
        result = "Test Result"
        self.web_automation._handle_js_result(result)
        
        # Should store the result
        assert hasattr(self.web_automation, '_last_js_result')
        assert self.web_automation._last_js_result == result

    def test_handle_js_result_none(self):
        """Test JavaScript result handling with None."""
        self.web_automation._handle_js_result(None)
        
        assert self.web_automation._last_js_result is None

    def test_get_last_js_result(self):
        """Test getting last JavaScript result."""
        expected_result = "Test Result"
        self.web_automation._last_js_result = expected_result
        
        result = self.web_automation.get_last_js_result()
        
        assert result == expected_result

    def test_get_last_js_result_none(self):
        """Test getting last JavaScript result when None."""
        self.web_automation._last_js_result = None
        
        result = self.web_automation.get_last_js_result()
        
        assert result is None

    def test_clear_js_result(self):
        """Test clearing JavaScript result."""
        self.web_automation._last_js_result = "Test Result"
        self.web_automation.clear_js_result()
        
        assert self.web_automation._last_js_result is None

    def test_fetch_nsis_status_success(self):
        """Test successful NSIS status fetching."""
        mock_web_view = Mock()
        mock_page = Mock()
        mock_web_view.page.return_value = mock_page
        mock_web_view.page().isLoading.return_value = False
        self.web_automation.set_web_view(mock_web_view)
        
        # Mock successful operations
        with patch.object(self.web_automation, 'load_url', return_value=True), \
             patch.object(self.web_automation, '_wait_for_load', return_value=True), \
             patch.object(self.web_automation, '_execute_javascript', return_value=True):
            
            result = self.web_automation.fetch_nsis_status("TEST001")
            
            assert result is not None
            assert "status" in result
            assert "result" in result
            assert "timestamp" in result

    def test_fetch_nsis_status_no_web_view(self):
        """Test NSIS status fetching without web view."""
        self.web_automation.web_view = None
        
        result = self.web_automation.fetch_nsis_status("TEST001")
        
        assert result is not None
        assert result["status"] == "Error"
        assert "No web view" in result["result"]

    def test_fetch_nsis_status_load_failure(self):
        """Test NSIS status fetching with load failure."""
        mock_web_view = Mock()
        self.web_automation.set_web_view(mock_web_view)
        
        with patch.object(self.web_automation, 'load_url', return_value=False):
            result = self.web_automation.fetch_nsis_status("TEST001")
            
            assert result is not None
            assert result["status"] == "Error"
            assert "Failed to load" in result["result"]

    def test_fetch_nsis_status_wait_timeout(self):
        """Test NSIS status fetching with wait timeout."""
        mock_web_view = Mock()
        mock_page = Mock()
        mock_web_view.page.return_value = mock_page
        self.web_automation.set_web_view(mock_web_view)
        
        with patch.object(self.web_automation, 'load_url', return_value=True), \
             patch.object(self.web_automation, '_wait_for_load', return_value=False):
            
            result = self.web_automation.fetch_nsis_status("TEST001")
            
            assert result is not None
            assert result["status"] == "Error"
            assert "Timeout" in result["result"]

    def test_fetch_nsis_status_js_failure(self):
        """Test NSIS status fetching with JavaScript failure."""
        mock_web_view = Mock()
        mock_page = Mock()
        mock_web_view.page.return_value = mock_page
        mock_web_view.page().isLoading.return_value = False
        self.web_automation.set_web_view(mock_web_view)
        
        with patch.object(self.web_automation, 'load_url', return_value=True), \
             patch.object(self.web_automation, '_wait_for_load', return_value=True), \
             patch.object(self.web_automation, '_execute_javascript', return_value=False):
            
            result = self.web_automation.fetch_nsis_status("TEST001")
            
            assert result is not None
            assert result["status"] == "Error"
            assert "Failed to execute" in result["result"]

    def test_simulate_nsis_status_success(self):
        """Test successful NSIS status simulation."""
        result = self.web_automation._simulate_nsis_status("TEST001")
        
        assert result is not None
        assert "status" in result
        assert "result" in result
        assert "timestamp" in result
        assert result["nsis_code"] == "TEST001"

    def test_simulate_nsis_status_error(self):
        """Test NSIS status simulation with error."""
        # Mock random to always return error
        with patch('main_window.web_automation.random.random', return_value=0.9):
            result = self.web_automation._simulate_nsis_status("TEST001")
            
            assert result is not None
            assert result["status"] == "Error"
            assert "error" in result["result"]

    def test_validate_nsis_code_valid(self):
        """Test NSIS code validation with valid codes."""
        valid_codes = ["TEST001", "NSIS123", "ABC123456"]
        
        for code in valid_codes:
            result = self.web_automation._validate_nsis_code(code)
            assert result is True

    def test_validate_nsis_code_invalid(self):
        """Test NSIS code validation with invalid codes."""
        invalid_codes = ["", None, "123", "TEST", "A" * 50]  # Too long
        
        for code in invalid_codes:
            result = self.web_automation._validate_nsis_code(code)
            assert result is False

    def test_get_page_title_success(self):
        """Test successful page title retrieval."""
        mock_web_view = Mock()
        mock_page = Mock()
        mock_web_view.page.return_value = mock_page
        self.web_automation.set_web_view(mock_web_view)
        
        with patch.object(self.web_automation, '_execute_javascript', return_value=True):
            result = self.web_automation.get_page_title()
            
            assert result is True
            self.web_automation._execute_javascript.assert_called_once_with("document.title")

    def test_get_page_title_no_web_view(self):
        """Test page title retrieval without web view."""
        self.web_automation.web_view = None
        
        result = self.web_automation.get_page_title()
        
        assert result is False

    def test_get_page_content_success(self):
        """Test successful page content retrieval."""
        mock_web_view = Mock()
        mock_page = Mock()
        mock_web_view.page.return_value = mock_page
        self.web_automation.set_web_view(mock_web_view)
        
        with patch.object(self.web_automation, '_execute_javascript', return_value=True):
            result = self.web_automation.get_page_content()
            
            assert result is True
            self.web_automation._execute_javascript.assert_called_once_with("document.body.innerText")

    def test_get_page_content_no_web_view(self):
        """Test page content retrieval without web view."""
        self.web_automation.web_view = None
        
        result = self.web_automation.get_page_content()
        
        assert result is False

    def test_is_page_loaded_true(self):
        """Test page loaded check when true."""
        mock_web_view = Mock()
        mock_web_view.page().isLoading.return_value = False
        self.web_automation.set_web_view(mock_web_view)
        
        result = self.web_automation.is_page_loaded()
        
        assert result is True

    def test_is_page_loaded_false(self):
        """Test page loaded check when false."""
        mock_web_view = Mock()
        mock_web_view.page().isLoading.return_value = True
        self.web_automation.set_web_view(mock_web_view)
        
        result = self.web_automation.is_page_loaded()
        
        assert result is False

    def test_is_page_loaded_no_web_view(self):
        """Test page loaded check without web view."""
        self.web_automation.web_view = None
        
        result = self.web_automation.is_page_loaded()
        
        assert result is False

    def test_get_current_url_success(self):
        """Test successful current URL retrieval."""
        mock_web_view = Mock()
        mock_web_view.url.return_value = QUrl("https://example.com")
        self.web_automation.set_web_view(mock_web_view)
        
        result = self.web_automation.get_current_url()
        
        assert result == "https://example.com"

    def test_get_current_url_no_web_view(self):
        """Test current URL retrieval without web view."""
        self.web_automation.web_view = None
        
        result = self.web_automation.get_current_url()
        
        assert result is None 