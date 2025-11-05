# Script di avvio per Electron
# Risolve il problema della variabile ELECTRON_RUN_AS_NODE

Write-Host "Avvio Controllo Stato NSIS (Electron)..." -ForegroundColor Yellow

# Rimuove la variabile d'ambiente ELECTRON_RUN_AS_NODE se presente
if (Test-Path Env:ELECTRON_RUN_AS_NODE) {
    Write-Host "Rimozione variabile ELECTRON_RUN_AS_NODE..." -ForegroundColor Cyan
    Remove-Item Env:ELECTRON_RUN_AS_NODE
}

# Avvia Electron
Write-Host "Avvio Electron..." -ForegroundColor Green
& "$PSScriptRoot\node_modules\.bin\electron.cmd" .
