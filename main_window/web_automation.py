# main_window/web_automation.py
# Web automation module for NSIS state checking

from PyQt6 import QtCore, QtWebEngineWidgets, QtWebEngineCore, QtWebChannel
from typing import Optional, Callable, Dict, Any
import logging
import time
from .state_manager import AppState

# Custom web engine page for handling navigation
class WebEnginePage(QtWebEngineCore.QWebEnginePage):
    """Custom web engine page for handling navigation."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._logger = logging.getLogger(__name__)
    
    def acceptNavigationRequest(self, url, _type, isMainFrame):
        """Handle navigation requests to allow external links."""
        # Allow all navigation requests
        self._logger.debug(f"Navigation request: {url.toString()} (type: {_type}, mainFrame: {isMainFrame})")
        return True
    
    def createWindow(self, _type):
        """Handle new window/tab requests by creating a new page in the same view."""
        self._logger.debug(f"New window request: {_type}")
        # Create a new page but return the same view
        new_page = WebEnginePage(self.parent())
        new_page.setUrl(self.url())
        return new_page
    
    def createStandardContextMenu(self):
        """Create standard context menu for right-click."""
        return super().createStandardContextMenu()
    
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        """Handle JavaScript console messages for debugging."""
        level_str = {0: "INFO", 1: "WARNING", 2: "ERROR"}.get(level, "UNKNOWN")
        self._logger.debug(f"JS Console [{level_str}] Line {lineNumber}: {message}")
    
    def certificateError(self, error):
        """Handle SSL certificate errors."""
        self._logger.warning(f"Certificate error: {error.errorDescription()}")
        # Accept certificate errors for development/testing
        return True

class JSBridge(QtCore.QObject):
    """JavaScript bridge for web automation."""
    pass

class WebAutomation(QtCore.QObject):
    """Handles web automation for NSIS state checking."""
    
    # Signals
    fetchCompleted = QtCore.pyqtSignal(str, str, list)  # code, state, cells
    fetchFailed = QtCore.pyqtSignal(str, str)  # code, error_message
    stateChanged = QtCore.pyqtSignal(AppState)
    
    def __init__(self):
        super().__init__()
        self._logger = logging.getLogger(__name__)
        self._web_view: Optional[QtWebEngineWidgets.QWebEngineView] = None
        self._web_page: Optional[WebEnginePage] = None
        self._js_bridge: Optional[JSBridge] = None
        self._current_state = AppState.IDLE
        self._pending_fetch: Optional[str] = None
        self._retry_count = 0
        self._max_retries = 2
        self._fetch_timeout_ms = 5000  # Reduced from 10000 to 5000ms
        self._fetch_check_interval_ms = 50  # Reduced from 100 to 50ms
        
        # Configuration from config.py
        from config import (
            URL_NSIS, STATO_SELECTOR, ALL_CELLS_JS, DELAY_AFTER_INPUT_JS,
            DELAY_AFTER_CLICK_JS, DELAY_BETWEEN_RETRIES, MAX_NULL_CHECKS
        )
        self._url_nsis = URL_NSIS
        self._stato_selector = STATO_SELECTOR
        self._all_cells_js = ALL_CELLS_JS
        self._delay_after_input_js = DELAY_AFTER_INPUT_JS
        self._delay_after_click_js = DELAY_AFTER_CLICK_JS
        self._delay_between_retries = DELAY_BETWEEN_RETRIES
        self._max_null_checks = MAX_NULL_CHECKS
    
    def setup_web_engine(self, web_view: QtWebEngineWidgets.QWebEngineView):
        """Setup web engine components."""
        try:
            self._web_view = web_view
            
            # Create custom web page
            self._web_page = WebEnginePage(self._web_view)
            self._web_view.setPage(self._web_page)
            
            self._js_bridge = JSBridge()
            
            # Connect signals
            self._web_page.loadFinished.connect(self._handle_page_load_finished)
            self._web_view.urlChanged.connect(self._handle_url_changed)
            self._web_page.linkHovered.connect(self._handle_link_hovered)
            
            # Enable JavaScript and plugins
            self._web_page.settings().setAttribute(
                QtWebEngineCore.QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
            self._web_page.settings().setAttribute(
                QtWebEngineCore.QWebEngineSettings.WebAttribute.PluginsEnabled, True)
            self._web_page.settings().setAttribute(
                QtWebEngineCore.QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
            self._web_page.settings().setAttribute(
                QtWebEngineCore.QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
            
            # Inject JavaScript to handle link clicks
            self._inject_link_handler_js()
            
            self._logger.info("Web automation setup completed")
            
        except Exception as e:
            self._logger.error(f"Error in WebAutomation.setup_web_engine: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _inject_link_handler_js(self):
        """Inject JavaScript to handle link clicks and prevent new windows."""
        js_code = """
        (function() {
            // Override window.open to prevent popups
            window.open = function(url, name, features) {
                console.log('Intercepted window.open:', url);
                if (url) {
                    window.location.href = url;
                }
                return null;
            };
            
            // Handle all link clicks
            document.addEventListener('click', function(e) {
                var target = e.target;
                while (target && target.tagName !== 'A') {
                    target = target.parentElement;
                }
                
                if (target && target.tagName === 'A') {
                    var href = target.getAttribute('href');
                    var target_attr = target.getAttribute('target');
                    
                    if (href && (target_attr === '_blank' || target_attr === '_new')) {
                        e.preventDefault();
                        console.log('Intercepted external link:', href);
                        window.location.href = href;
                    }
                }
            }, true);
            
            // Override target="_blank" links
            var links = document.querySelectorAll('a[target="_blank"], a[target="_new"]');
            for (var i = 0; i < links.length; i++) {
                links[i].removeAttribute('target');
            }
        })();
        """
        self._web_page.runJavaScript(js_code)
    
    def _inject_rounded_corners_css(self):
        """Inject CSS for elegant web integration."""
        css_code = """
        /* Elegant web integration - subtle styling */
        body {
            margin: 0 !important;
            padding: 8px !important;
            background: transparent !important;
        }
        
        /* Ensure content doesn't overflow */
        html {
            overflow-x: hidden !important;
        }
        
        /* Subtle styling for better integration */
        body > div:first-child {
            margin: 0 !important;
            padding: 0 !important;
        }
        """
        
        # Single injection for clean integration
        def inject_css():
            self._web_page.runJavaScript(f"""
            (function() {{
                // Remove any existing style
                var existingStyle = document.getElementById('web-integration-style');
                if (existingStyle) {{
                    existingStyle.remove();
                }}
                
                // Create and inject new style
                var style = document.createElement('style');
                style.id = 'web-integration-style';
                style.textContent = `{css_code}`;
                document.head.appendChild(style);
                
                // Apply subtle styling
                document.body.style.margin = '0';
                document.body.style.padding = '8px';
                document.body.style.background = 'transparent';
                
                console.log('Web integration CSS applied successfully');
            }})();
            """)
        
        # Single injection after page load
        QtCore.QTimer.singleShot(500, inject_css)
    
    def load_url(self, url: Optional[str] = None):
        """Load the NSIS URL."""
        target_url = url or self._url_nsis
        self._set_state(AppState.LOADING)
        self._logger.info(f"Loading URL: {target_url}")
        
        if self._web_view:
            try:
                self._web_view.load(QtCore.QUrl(target_url))
                
                # Set timeout for page load (increased for stability)
                QtCore.QTimer.singleShot(30000, self._handle_load_timeout)
                
            except Exception as e:
                self._logger.error(f"Error loading URL: {e}")
                self._set_state(AppState.ERROR)
    
    def _handle_load_timeout(self):
        """Handle page load timeout."""
        print("DEBUG: Load timeout handler called")
        if self._current_state == AppState.LOADING:
            self._logger.warning("Page load timeout, continuing anyway")
            print("DEBUG: Page load timeout, continuing anyway")
            self._set_state(AppState.IDLE)
            # Force the page to be considered loaded
            if self._web_page:
                self._web_page.loadFinished.emit(True)
        else:
            print(f"DEBUG: Load timeout but state is {self._current_state}")
    
    def fetch_state_for_code(self, code: str):
        """Fetch state for a specific code."""
        self._logger.debug(f"fetch_state_for_code chiamato con codice: '{code}'")
        self._pending_fetch = code
        self._logger.debug(f"_pending_fetch impostato a: '{self._pending_fetch}'")
        
        if not self._web_page or not self._web_page.isLoading():
            self._attempt_fetch(self._web_page, code)
        else:
            self._logger.info(f"Page still loading, queuing fetch for code: {code}")
    
    def _attempt_fetch(self, page: WebEnginePage, code: str):
        """Attempt to fetch state for a code."""
        if not page:
            self.fetchFailed.emit(code, "Web page not available")
            return
        
        self._set_state(AppState.PROCESSING)
        self._logger.info(f"Attempting fetch for code: {code} (attempt {self._retry_count + 1})")
        
        # Execute JavaScript to input the code
        self._execute_js_input(page, code)
    
    def _execute_js_input(self, page: WebEnginePage, code: str):
        """Execute JavaScript to input the code in the search field."""
        input_script = f'''
        (function() {{
            var inputField = document.querySelector('input[type="text"], input[name*="codice"], input[id*="codice"]');
            if (inputField) {{
                inputField.value = "{code}";
                inputField.dispatchEvent(new Event('input', {{ bubbles: true }}));
                inputField.dispatchEvent(new Event('change', {{ bubbles: true }}));
                return true;
            }}
            return false;
        }})();
        '''
        
        # Pass the code to the callback using a lambda
        page.runJavaScript(input_script, lambda result: self._handle_input_result(result, code))
    
    def _handle_input_result(self, result, code: str):
        """Handle the result of input JavaScript execution."""
        if result:
            self._logger.info("Code input successful, scheduling click")
            # Schedule click after delay with the passed code
            QtCore.QTimer.singleShot(self._delay_after_input_js, 
                                   lambda: self._schedule_js_click(self._web_page, code))
        else:
            self._logger.error("Failed to input code")
            current_code = code or "UNKNOWN"
            self.fetchFailed.emit(current_code, "Failed to input code")
    
    def _schedule_js_click(self, page: WebEnginePage, code: str):
        """Schedule the click operation."""
        if page:
            QtCore.QTimer.singleShot(self._delay_after_click_js, 
                                   lambda: self._execute_js_click(page, code))
    
    def _execute_js_click(self, page: WebEnginePage, code: str):
        """Execute JavaScript to click the search button."""
        click_script = '''
        (function() {
            var buttons = document.querySelectorAll('button, input[type="submit"], .btn');
            for (var i = 0; i < buttons.length; i++) {
                var btn = buttons[i];
                var text = btn.textContent || btn.value || '';
                if (text.toLowerCase().includes('cerca') || text.toLowerCase().includes('search') || 
                    text.toLowerCase().includes('invia') || text.toLowerCase().includes('submit')) {
                    btn.click();
                    return true;
                }
            }
            return false;
        })();
        '''
        
        # Pass the code to the callback using a lambda
        page.runJavaScript(click_script, lambda result: self._handle_click_result(result, code))
    
    def _handle_click_result(self, result, code: str):
        """Handle the result of click JavaScript execution."""
        if result:
            self._logger.info("Click successful, scheduling result check")
            # Use the code passed as parameter
            if code:
                # Schedule the check with the passed code
                QtCore.QTimer.singleShot(1000, 
                                       lambda: self._schedule_first_check(self._web_page, code))
            else:
                self._logger.error("Codice mancante in _handle_click_result")
                self.fetchFailed.emit("UNKNOWN", "Missing code in click result")
        else:
            self._logger.error("Failed to click search button")
            current_code = code or "UNKNOWN"
            self.fetchFailed.emit(current_code, "Failed to click search button")
    
    def _schedule_first_check(self, page: WebEnginePage, code: str):
        """Schedule the first check for results."""
        if page:
            QtCore.QTimer.singleShot(500, 
                                   lambda: self._check_fetch_result(page, code))
    
    def _check_fetch_result(self, page: WebEnginePage, code: str):
        """Check if fetch result is available."""
        if not page:
            return
        
        # JavaScript to check for results
        check_script = f'''
        (function() {{
            var statoElement = document.querySelector('{self._stato_selector}');
            if (statoElement && statoElement.textContent.trim()) {{
                return {self._all_cells_js};
            }}
            return null;
        }})();
        '''
        
        # Pass the code to the callback using a lambda
        page.runJavaScript(check_script, lambda result: self._handle_js_evaluation_result(result, code))
    
    def _handle_js_evaluation_result(self, result, code: str):
        """Handle JavaScript evaluation result."""
        if result and isinstance(result, list) and len(result) > 0:
            # Success - extract state and cells
            state = result[2] if len(result) > 2 else "SCONOSCIUTO"
            
            # Use the code passed as parameter
            if not code:
                self._logger.error("Codice mancante nel parametro")
                self.fetchFailed.emit("UNKNOWN", "Missing code in web automation")
                self._retry_count = 0
                self._pending_fetch = None
                self._set_state(AppState.IDLE)
                return
            
            self._logger.info(f"Fetch successful for code {code}: {state}")
            self._logger.debug(f"Emettendo fetchCompleted con codice: '{code}'")
            self.fetchCompleted.emit(code, state, result)
            self._retry_count = 0
            self._pending_fetch = None
            self._set_state(AppState.IDLE)
        else:
            # No result yet, retry or fail
            self._retry_count += 1
            if self._retry_count < self._max_retries:
                self._logger.info(f"No result yet, retrying... (attempt {self._retry_count + 1})")
                QtCore.QTimer.singleShot(self._delay_between_retries, 
                                       lambda: self._check_fetch_result(self._web_page, code))
            else:
                # Use the code passed as parameter for error reporting
                current_code = code or "UNKNOWN"
                self._logger.error(f"Failed to fetch result after {self._max_retries} attempts for code: {current_code}")
                self.fetchFailed.emit(current_code, "Timeout - no result found")
                self._retry_count = 0
                self._pending_fetch = None
                self._set_state(AppState.IDLE)
    
    def _handle_page_load_finished(self, ok: bool):
        """Handle page load finished event."""
        if ok:
            self._logger.info("Page loaded successfully")
            
            # Inject link handler JavaScript after page load
            self._inject_link_handler_js()
            
            # Inject rounded corners CSS after page load
            self._inject_rounded_corners_css()
            
            self._set_state(AppState.IDLE)
            
            # If there's a pending fetch, execute it
            if self._pending_fetch:
                self._attempt_fetch(self._web_page, self._pending_fetch)
        else:
            self._logger.error("Page load failed")
            self._set_state(AppState.ERROR)
            if self._pending_fetch:
                self.fetchFailed.emit(self._pending_fetch, "Page load failed")
    
    def _handle_url_changed(self, url: QtCore.QUrl):
        """Handle URL change event."""
        self._logger.debug(f"URL changed to: {url.toString()}")
    
    def _handle_link_hovered(self, url: str):
        """Handle link hover events."""
        # Reduced logging for performance
        pass
    
    def _set_state(self, state: AppState):
        """Set automation state and emit signal."""
        self._current_state = state
        self.stateChanged.emit(state)
    
    @property
    def current_state(self) -> AppState:
        """Get current automation state."""
        return self._current_state
    
    @property
    def web_view(self) -> Optional[QtWebEngineWidgets.QWebEngineView]:
        """Get the web view."""
        return self._web_view
    
    def reset(self):
        """Reset automation state."""
        self._retry_count = 0
        self._pending_fetch = None
        self._set_state(AppState.IDLE)
    
    def stop(self):
        """Stop current automation."""
        self._pending_fetch = None
        self._retry_count = 0
        self._set_state(AppState.IDLE) 