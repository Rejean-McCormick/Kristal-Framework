@echo off
setlocal
cd /d "%~dp0"
where pyw >nul 2>nul
if %errorlevel%==0 (
  start "Kristal GitHub Setup" pyw -3.11 "%~dp0Kristal-GitHub-Setup.pyw"
  exit /b 0
)
where pythonw >nul 2>nul
if %errorlevel%==0 (
  start "Kristal GitHub Setup" pythonw "%~dp0Kristal-GitHub-Setup.pyw"
  exit /b 0
)
echo Python 3.11+ with pythonw/pyw is required.
pause
exit /b 1
