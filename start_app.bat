@echo off
cd /d %~dp0
..\python\python.exe -m streamlit run app.py
pause