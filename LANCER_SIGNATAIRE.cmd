@echo off
setlocal
if exist "%~dp0.venv\Scripts\pythonw.exe" (
    start "" "%~dp0.venv\Scripts\pythonw.exe" "%~dp0signataire.py"
    exit /b
)
if exist "%USERPROFILE%\technocore-did-starter\.venv\Scripts\pythonw.exe" (
    start "" "%USERPROFILE%\technocore-did-starter\.venv\Scripts\pythonw.exe" "%~dp0signataire.py"
    exit /b
)
echo Python et cryptography sont necessaires. Voir README.md.
pause
