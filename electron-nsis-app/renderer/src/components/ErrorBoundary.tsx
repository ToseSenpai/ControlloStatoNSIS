import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('[ErrorBoundary] React Error Caught:', error);
    console.error('[ErrorBoundary] Component Stack:', errorInfo.componentStack);

    this.setState({
      error,
      errorInfo
    });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          padding: '40px',
          fontFamily: 'monospace',
          backgroundColor: '#1e1e1e',
          color: '#fff',
          height: '100vh',
          overflow: 'auto'
        }}>
          <h1 style={{ color: '#f04747' }}>⚠️ Errore Applicazione</h1>
          <h2>Si è verificato un errore durante il rendering</h2>

          <div style={{
            marginTop: '20px',
            padding: '20px',
            backgroundColor: '#2f3136',
            borderRadius: '8px',
            border: '1px solid #f04747'
          }}>
            <h3 style={{ marginTop: 0 }}>Errore:</h3>
            <pre style={{
              color: '#f04747',
              overflow: 'auto',
              fontSize: '14px'
            }}>
              {this.state.error && this.state.error.toString()}
            </pre>
          </div>

          {this.state.errorInfo && (
            <div style={{
              marginTop: '20px',
              padding: '20px',
              backgroundColor: '#2f3136',
              borderRadius: '8px'
            }}>
              <h3 style={{ marginTop: 0 }}>Stack dei Componenti:</h3>
              <pre style={{
                color: '#b9bbbe',
                overflow: 'auto',
                fontSize: '12px',
                lineHeight: '1.5'
              }}>
                {this.state.errorInfo.componentStack}
              </pre>
            </div>
          )}

          <button
            onClick={() => window.location.reload()}
            style={{
              marginTop: '30px',
              padding: '12px 24px',
              backgroundColor: '#5865f2',
              color: '#fff',
              border: 'none',
              borderRadius: '4px',
              fontSize: '16px',
              cursor: 'pointer'
            }}
          >
            🔄 Ricarica Applicazione
          </button>

          <div style={{
            marginTop: '30px',
            padding: '20px',
            backgroundColor: '#2f3136',
            borderRadius: '8px',
            color: '#72767d',
            fontSize: '13px'
          }}>
            <p style={{ margin: 0 }}>
              💡 <strong>Suggerimento:</strong> Controlla la Console DevTools (F12) per maggiori dettagli.
            </p>
            <p style={{ marginTop: '10px', marginBottom: 0 }}>
              Se il problema persiste, prova a ricompilare: <code style={{ color: '#fff' }}>npm run build</code>
            </p>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
