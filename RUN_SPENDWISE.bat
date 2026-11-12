@echo off
title SpendWise Launcher
echo ========================================================
echo               SpendWise AI Assistant
echo ========================================================
echo.
echo [1/2] Launching Python FastAPI Backend on http://localhost:8000 ...
start "SpendWise Backend" cmd /k "python -m uvicorn api:app --host 0.0.0.0 --port 8000"

echo [2/2] Launching React RealByte Frontend on http://localhost:3000 ...
cd frontend
if not exist node_modules (
    echo Installing frontend dependencies...
    call npm install
)
start "SpendWise Frontend" cmd /k "npm run dev -- --port 3000"

echo.
echo ========================================================
echo SpendWise is now running!
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo ========================================================
pause
