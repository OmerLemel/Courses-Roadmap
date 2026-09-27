@echo off
cd /d "%~dp0"
echo Serving TAU course roadmap on http://localhost:8000
python -m http.server 8000
