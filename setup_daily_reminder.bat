@echo off
REM Setup Daily Email Reminder in Windows Task Scheduler
REM Run this script AS ADMINISTRATOR to create the scheduled task

echo ========================================
echo Study Assistant - Daily Reminder Setup
echo ========================================
echo.

REM Check for admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo.
    echo Right-click this file and select "Run as administrator"
    pause
    exit /b 1
)

echo Creating scheduled task to run daily at 7:00 AM...
echo.

REM Create the scheduled task
schtasks /create /tn "StudyAssistantReminder" /tr "C:\Code\ai-study-assistant\run_email_reminder.bat" /sc daily /st 07:00 /f

if %errorLevel% equ 0 (
    echo.
    echo ========================================
    echo SUCCESS! Daily reminder has been set up.
    echo ========================================
    echo.
    echo The reminder will run every day at 7:00 AM.
    echo.
    echo To change the time:
    echo   1. Open Task Scheduler (search for it in Start menu)
    echo   2. Find "StudyAssistantReminder" in the list
    echo   3. Right-click and select "Properties"
    echo   4. Go to "Triggers" tab and edit the time
    echo.
    echo To remove the reminder:
    echo   Run: schtasks /delete /tn "StudyAssistantReminder" /f
    echo.
) else (
    echo.
    echo ERROR: Failed to create scheduled task.
    echo Please try running this script as Administrator.
)

echo.
pause
