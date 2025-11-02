@echo off
REM Activate venv first if you have one
REM call .venv\Scripts\activate

REM Start uvicorn
uvicorn app.main:app --reload --port 8000
pause
