@echo off
title Grand Horizon Hotel Reservation Management System
echo ====================================================================
echo   GRAND HORIZON HOTEL RESERVATION MANAGEMENT SYSTEM
echo   Academic DBMS Full-Stack Web Application
echo ====================================================================
echo.
echo Checking database initialization...
python db_setup.py
echo.
echo Starting Flask Full-Stack Server at http://127.0.0.1:5000 ...
echo Press Ctrl+C to stop the server anytime.
echo.
start http://127.0.0.1:5000
python app.py
pause
