@echo off
setlocal
if exist "%~dp0.venv\Scripts\pythonw.exe" (
    start "" "%~dp0.venv\Scripts\pythonw.exe" "%~dp0install_browser_connector.py"
    exit /b
)
if exist "%USERPROFILE%\technocore-did-starter\.venv\Scripts\pythonw.exe" (
    start "" "%USERPROFILE%\technocore-did-starter\.venv\Scripts\pythonw.exe" "%~dp0install_browser_connector.py"
    exit /b
)
echo Install the dependencies first. See README.md.
pause
