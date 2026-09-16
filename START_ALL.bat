@echo off
REM ============================================
REM  TigerTrace - One-Click Full Stack Launcher
REM  Backend : http://localhost:8000  (docs at /docs)
REM  Frontend: http://localhost:3000
REM ============================================
title TigerTrace Launcher

echo Starting backend (FastAPI on :8000)...
start "TigerTrace Backend" cmd /k "cd /d %~dp0backend && .venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000"

echo Starting frontend (Next.js on :3000)...
start "TigerTrace Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

timeout /t 8 /nobreak >nul
start http://localhost:3000

echo.
echo  Both servers are launching in separate windows.
echo    Frontend : http://localhost:3000
echo    API      : http://localhost:8000
echo    API Docs : http://localhost:8000/docs
echo  Close those windows to stop the servers.
echo.
pause
