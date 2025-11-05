import React, { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { RootState } from './store/store';
import SplashScreen from './components/SplashScreen';
import MainWindow from './components/MainWindow';

const App: React.FC = () => {
  const [showSplash, setShowSplash] = useState(true);
  const isLoading = useSelector((state: RootState) => state.app.isLoading);

  useEffect(() => {
    // Check if this is the splash window
    const urlParams = new URLSearchParams(window.location.search);
    const isSplash = urlParams.get('splash') === 'true' || window.location.hash === '#splash';

    if (isSplash) {
      // This is the splash window, keep showing splash
      setShowSplash(true);
    } else {
      // This is the main window, hide splash after loading
      const timer = setTimeout(() => {
        setShowSplash(false);
      }, 100);
      return () => clearTimeout(timer);
    }
  }, []);

  // If splash parameter is present, show only splash
  const urlParams = new URLSearchParams(window.location.search);
  const isSplashWindow = urlParams.get('splash') === 'true' || window.location.hash === '#splash';

  if (isSplashWindow) {
    return <SplashScreen />;
  }

  return (
    <div className="app-container">
      {showSplash ? <SplashScreen /> : <MainWindow />}
    </div>
  );
};

export default App;
