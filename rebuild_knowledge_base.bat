@echo off
echo ========================================
echo  CodeSentinel DP Knowledge Base Rebuild
echo ========================================
echo.
echo This will:
echo 1. Delete old knowledge base
echo 2. Build new Wikipedia-based knowledge
echo 3. Ingest 50+ technical articles
echo.
echo Press Ctrl+C to cancel, or
pause

echo.
echo [1/2] Installing/Updating dependencies...
pip install --upgrade sentence-transformers==2.2.2 huggingface-hub==0.20.0 datasets==2.14.0 wikipedia-api

echo.
echo [2/2] Building knowledge base from Wikipedia...
python backend/rag/wikipedia_ingest.py

echo.
echo ========================================
echo  Knowledge Base Rebuild Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Start backend: start-backend.bat
echo 2. Start frontend: start-frontend.bat
echo 3. Open http://localhost:5173
echo.
pause

@REM Made with Bob
