@echo off
REM Study Assistant - Setup Daily Backup Task
REM This script creates a Windows Task Scheduler task for automatic daily backups
REM Run this script as Administrator

echo ============================================
echo Study Assistant - Backup Task Setup
echo ============================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
set PYTHON_SCRIPT=%SCRIPT_DIR%run_backup.py

REM Check if Python script exists
if not exist "%PYTHON_SCRIPT%" (
    echo ERROR: run_backup.py not found at %PYTHON_SCRIPT%
    echo Please run this script from the Study Assistant directory.
    pause
    exit /b 1
)

echo This will create a scheduled task to run daily backups.
echo.
echo Options:
echo   1. Local backup only
echo   2. Backup with Google Drive upload
echo.

set /p CHOICE="Enter your choice (1-2): "

if "%CHOICE%"=="1" (
    set BACKUP_ARGS=
    set TASK_DESC=Study Assistant Daily Backup (Local)
) else if "%CHOICE%"=="2" (
    set BACKUP_ARGS=--cloud
    set TASK_DESC=Study Assistant Daily Backup (Google Drive)
) else (
    echo Invalid choice. Exiting.
    pause
    exit /b 1
)

echo.
set /p BACKUP_TIME="Enter backup time (24h format, e.g., 22:00): "

if "%BACKUP_TIME%"=="" set BACKUP_TIME=22:00

echo.
echo Creating scheduled task...
echo   Task: StudyAssistantBackup
echo   Time: %BACKUP_TIME% daily
echo   Args: %BACKUP_ARGS%
echo.

REM Delete existing task if it exists
schtasks /delete /tn "StudyAssistantBackup" /f >nul 2>&1

REM Create the scheduled task
schtasks /create ^
    /tn "StudyAssistantBackup" ^
    /tr "python \"%PYTHON_SCRIPT%\" %BACKUP_ARGS%" ^
    /sc daily ^
    /st %BACKUP_TIME% ^
    /rl HIGHEST ^
    /f

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo SUCCESS! Backup task created.
    echo ============================================
    echo.
    echo The backup will run daily at %BACKUP_TIME%.
    echo Backups will be stored in: %SCRIPT_DIR%data\backups\
    echo.
    echo To view/modify the task:
    echo   1. Open Task Scheduler (taskschd.msc)
    echo   2. Find "StudyAssistantBackup" in the list
    echo.
    echo To run a backup manually:
    echo   python "%PYTHON_SCRIPT%" %BACKUP_ARGS%
    echo.
    echo To remove the scheduled task:
    echo   schtasks /delete /tn "StudyAssistantBackup" /f
) else (
    echo.
    echo ERROR: Failed to create scheduled task.
    echo Make sure you're running this script as Administrator.
)

echo.
pause
