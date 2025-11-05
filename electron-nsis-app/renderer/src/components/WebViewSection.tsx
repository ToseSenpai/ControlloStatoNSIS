import React, { useEffect, useState, useRef } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { ChevronLeft, ChevronRight, RotateCw, Home, Globe } from 'lucide-react';
import { RootState } from '../store/store';
import { setWebViewUrl, setWebViewLoading } from '../store/slices/ui-slice';
import { URL_NSIS } from '../../../shared/constants/config';
import './WebViewSection.css';

// Use Electron's webview element (declared in @types/electron)

const WebViewSection: React.FC = () => {
  const dispatch = useDispatch();
  const { webViewUrl, webViewLoading } = useSelector((state: RootState) => state.ui);
  const [canGoBack, setCanGoBack] = useState(false);
  const [canGoForward, setCanGoForward] = useState(false);
  const webviewRef = useRef<any>(null);

  // Setup webview event listeners
  useEffect(() => {
    const webview = webviewRef.current;
    if (!webview) return;

    console.log('[WebView] Initializing webview tag');

    // Navigation events
    const handleDidNavigate = (e: any) => {
      console.log('[WebView] Navigation to:', e.url);
      dispatch(setWebViewUrl(e.url));
      setCanGoBack(webview.canGoBack());
      setCanGoForward(webview.canGoForward());
    };

    const handleDidStartLoading = () => {
      console.log('[WebView] Started loading');
      dispatch(setWebViewLoading(true));
    };

    const handleDidStopLoading = () => {
      console.log('[WebView] Stopped loading');
      dispatch(setWebViewLoading(false));
      setCanGoBack(webview.canGoBack());
      setCanGoForward(webview.canGoForward());

      // Inject link click interceptor and window.open() override
      injectLinkInterceptor(webview);

      // Register webview's webContents ID with main process for automation
      try {
        const webContentsId = webview.getWebContentsId();
        console.log('[WebView] Registering webContents ID:', webContentsId);
        window.electronAPI.registerWebView(webContentsId);
      } catch (error) {
        console.error('[WebView] Failed to register webContents ID:', error);
      }
    };

    const handleDidFailLoad = (e: any) => {
      console.error('[WebView] Failed to load:', e);
      dispatch(setWebViewLoading(false));
    };

    // Handle new-window events (target="_blank" links)
    const handleNewWindow = (e: any) => {
      console.log('[WebView] new-window event:', e.url);
      e.preventDefault(); // Prevent new window
      webview.loadURL(e.url); // Navigate in same webview
    };

    // Add event listeners
    webview.addEventListener('did-navigate', handleDidNavigate);
    webview.addEventListener('did-navigate-in-page', handleDidNavigate);
    webview.addEventListener('did-start-loading', handleDidStartLoading);
    webview.addEventListener('did-stop-loading', handleDidStopLoading);
    webview.addEventListener('did-fail-load', handleDidFailLoad);
    webview.addEventListener('new-window', handleNewWindow);

    // Initial URL
    dispatch(setWebViewUrl(URL_NSIS));

    return () => {
      webview.removeEventListener('did-navigate', handleDidNavigate);
      webview.removeEventListener('did-navigate-in-page', handleDidNavigate);
      webview.removeEventListener('did-start-loading', handleDidStartLoading);
      webview.removeEventListener('did-stop-loading', handleDidStopLoading);
      webview.removeEventListener('did-fail-load', handleDidFailLoad);
      webview.removeEventListener('new-window', handleNewWindow);
    };
  }, [dispatch]);

  // Inject link interceptor into webview
  const injectLinkInterceptor = (webview: any) => {
    const scriptToInject = `
      (function() {
        console.log('[WebView Interceptor] Installing...');

        // CRITICAL: Override window.open() globally (like old PyQt6 system)
        window.open = function(url, name, features) {
          console.log('[WebView Interceptor] Blocked window.open():', url);
          if (url) {
            window.location.href = url;
          }
          return null;
        };

        // Remove existing interceptors if present
        if (window.__webview_link_interceptor) {
          document.removeEventListener('click', window.__webview_link_interceptor, true);
          document.removeEventListener('mousedown', window.__webview_link_interceptor, true);
          document.removeEventListener('auxclick', window.__webview_link_interceptor, true);
        }

        // Create new interceptor that handles ALL clicks on links
        const interceptor = function(e) {
          const link = e.target.closest('a');

          if (link && link.href) {
            // Check if any modifier key is pressed or if it's a non-left click
            const hasModifier = e.ctrlKey || e.shiftKey || e.metaKey || e.altKey;
            const isMiddleClick = e.button === 1;
            const opensNewWindow = link.target === '_blank' ||
                                  link.target === '_new' ||
                                  link.rel.includes('noopener') ||
                                  link.rel.includes('noreferrer');

            // Intercept if any condition that would open new window is true
            if (opensNewWindow || hasModifier || isMiddleClick) {
              console.log('[WebView Interceptor] Blocked link click:', link.href);
              e.preventDefault();
              e.stopPropagation();
              e.stopImmediatePropagation();

              // Navigate in same page instead of opening new window
              window.location.href = link.href;
              return false;
            }
          }
        };

        // Store reference
        window.__webview_link_interceptor = interceptor;

        // Add listeners for all types of clicks in capture phase
        document.addEventListener('click', interceptor, true);
        document.addEventListener('mousedown', interceptor, true);
        document.addEventListener('auxclick', interceptor, true); // Middle click

        console.log('[WebView Interceptor] window.open() override + click interceptor installed');
      })();
    `;

    try {
      webview.executeJavaScript(scriptToInject);
      console.log('[WebView] Link interceptor injected successfully');
    } catch (error) {
      console.error('[WebView] Error injecting link interceptor:', error);
    }
  };

  const handleBack = () => {
    if (webviewRef.current && canGoBack) {
      webviewRef.current.goBack();
    }
  };

  const handleForward = () => {
    if (webviewRef.current && canGoForward) {
      webviewRef.current.goForward();
    }
  };

  const handleReload = () => {
    if (webviewRef.current) {
      webviewRef.current.reload();
    }
  };

  const handleHome = () => {
    if (webviewRef.current) {
      webviewRef.current.loadURL(URL_NSIS);
    }
  };

  return (
    <div className="webview-section">
      <div className="webview-header">
        <h3 className="section-title">
          <Globe size={18} className="title-icon" />
          Navigazione Web NSIS
        </h3>

        <div className="webview-controls">
          <button
            className="nav-button"
            onClick={handleBack}
            disabled={!canGoBack}
            title="Indietro"
          >
            <ChevronLeft size={18} />
          </button>
          <button
            className="nav-button"
            onClick={handleForward}
            disabled={!canGoForward}
            title="Avanti"
          >
            <ChevronRight size={18} />
          </button>
          <button
            className="nav-button nav-button-reload"
            onClick={handleReload}
            title="Ricarica"
          >
            <RotateCw size={18} />
          </button>
          <button
            className="nav-button"
            onClick={handleHome}
            title="Home NSIS"
          >
            <Home size={18} />
          </button>
        </div>

        <div className="webview-url-bar">
          <div className="url-display">
            {webViewLoading && <span className="loading-indicator">⏳</span>}
            <span className="url-text">{webViewUrl || 'Nessun URL'}</span>
          </div>
        </div>
      </div>

      <div id="webview-container" className="webview-container">
        <webview
          ref={webviewRef}
          src={URL_NSIS}
          partition="persist:nsis"
          allowpopups={true}
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%'
          }}
        />
      </div>
    </div>
  );
};

export default WebViewSection;
