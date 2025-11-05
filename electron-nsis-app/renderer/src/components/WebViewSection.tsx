import React, { useEffect, useState, useRef } from 'react';
import { useSelector, useDispatch } from 'react-redux';
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
    };

    const handleDidFailLoad = (e: any) => {
      console.error('[WebView] Failed to load:', e);
      dispatch(setWebViewLoading(false));
    };

    // Add event listeners
    webview.addEventListener('did-navigate', handleDidNavigate);
    webview.addEventListener('did-navigate-in-page', handleDidNavigate);
    webview.addEventListener('did-start-loading', handleDidStartLoading);
    webview.addEventListener('did-stop-loading', handleDidStopLoading);
    webview.addEventListener('did-fail-load', handleDidFailLoad);

    // Initial URL
    dispatch(setWebViewUrl(URL_NSIS));

    return () => {
      webview.removeEventListener('did-navigate', handleDidNavigate);
      webview.removeEventListener('did-navigate-in-page', handleDidNavigate);
      webview.removeEventListener('did-start-loading', handleDidStartLoading);
      webview.removeEventListener('did-stop-loading', handleDidStopLoading);
      webview.removeEventListener('did-fail-load', handleDidFailLoad);
    };
  }, [dispatch]);

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
          <span className="icon">🌐</span>
          Navigazione Web NSIS
        </h3>

        <div className="webview-controls">
          <button
            className="nav-button"
            onClick={handleBack}
            disabled={!canGoBack}
            title="Indietro"
          >
            ←
          </button>
          <button
            className="nav-button"
            onClick={handleForward}
            disabled={!canGoForward}
            title="Avanti"
          >
            →
          </button>
          <button
            className="nav-button"
            onClick={handleReload}
            title="Ricarica"
          >
            ↻
          </button>
          <button
            className="nav-button"
            onClick={handleHome}
            title="Home NSIS"
          >
            🏠
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
