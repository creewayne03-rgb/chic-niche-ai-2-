@echo off
title Chic Niche AI by Wayne Wanjohi
color 0A
echo.
echo  ==========================================
echo   Chic Niche AI - Created by Wayne Wanjohi
echo  ==========================================
echo.
cd /d "%~dp0backend"
echo  Installing packages...
pip install fastapi uvicorn python-multipart groq pypdf python-dotenv pydantic httpx -q
echo.
echo  Starting Chic Niche AI...
start "" http://127.0.0.1:9000/app
python -m uvicorn main:app --host 127.0.0.1 --port 9000
pause
