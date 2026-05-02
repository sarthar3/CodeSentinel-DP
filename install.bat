@echo off
echo ========================================
echo CodeSentinel Installation Script
echo ========================================
echo.

echo [1/4] Installing Backend Dependencies...
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Backend installation failed!
    pause
    exit /b 1
)
echo Backend dependencies installed successfully!
echo.

echo [2/4] Skipping Demo Data Ingestion (Add files to your data directory)
echo.

cd ..

echo [3/4] Installing Frontend Dependencies...
cd frontend
call npm install --legacy-peer-deps
if %errorlevel% neq 0 (
    echo ERROR: Frontend installation failed!
    pause
    exit /b 1
)
echo Frontend dependencies installed successfully!
echo.

cd ..

echo [4/4] Installation Complete!
echo.
echo ========================================
echo Next Steps:
echo ========================================
echo.
echo 1. Start Backend (in Terminal 1):
echo    cd backend
echo    python -m uvicorn api.main:app --reload
echo.
echo 2. Start Frontend (in Terminal 2):
echo    cd frontend
echo    npm run dev
echo.
echo 3. Open Browser:
echo    http://localhost:5173
echo.
echo ========================================
pause

@REM Made with Bob
