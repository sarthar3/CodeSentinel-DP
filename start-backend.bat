@echo off
echo ========================================
echo Starting CodeSentinel Backend Server
echo ========================================
echo.

REM Make sure we're in the project root
cd /d "%~dp0"

echo Current directory: %CD%
echo.

echo Starting backend server...
echo Backend will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn backend.api.main:app --reload

pause

@REM Made with Bob
