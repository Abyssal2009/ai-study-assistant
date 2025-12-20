@echo off
REM Daily Email Reminder Runner
REM This script is called by Windows Task Scheduler

cd /d "C:\Code\ai-study-assistant"
python email_reminder.py --send

REM Log the result
echo [%date% %time%] Email reminder executed >> email_log.txt
