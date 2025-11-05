const { app, BrowserWindow } = require('electron');

console.log('Electron app:', app);
console.log('BrowserWindow:', BrowserWindow);

app.on('ready', () => {
  console.log('App is ready!');
  const win = new BrowserWindow({
    width: 800,
    height: 600
  });
  win.loadURL('https://www.google.com');
});
