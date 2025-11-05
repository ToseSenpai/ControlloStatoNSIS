@echo off
REM Wrapper script to start Electron with correct environment
REM Clears ELECTRON_RUN_AS_NODE if set

set ELECTRON_RUN_AS_NODE=
node_modules\.bin\electron.cmd .
