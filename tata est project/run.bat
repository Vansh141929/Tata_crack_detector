@echo off
echo ========================================================
echo  SteelGuard AI - Tata Steel Surface Inspection Platform
echo ========================================================
echo.
echo Starting Web Server on http://localhost:8000 ...
echo Press Ctrl+C to terminate the server.
echo.

py -m uvicorn server:app --host 0.0.0.0 --port 8000
pause
