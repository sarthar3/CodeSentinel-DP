@echo off
echo ========================================
echo Starting CodeSentinel DP Frontend Server
echo ========================================
echo.

REM Navigate to frontend directory
cd /d "%~dp0\frontend"

echo Current directory: %CD%
echo.

echo Starting frontend development server...
echo Frontend will be available at: http://localhost:5173
echo.
echo Press Ctrl+C to stop the server
echo.

call npm run dev

pause

@REM Made with Bob
