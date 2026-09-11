@echo off
echo Are you sure you want to delete the GDNewsBot scheduled task?
echo This will stop the bots from running automatically.
set "select="
set /p select=[Y(yes)/n(no)]:

if /I "%select%"=="y" goto :delete
if /I "%select%"=="n" goto :close
echo Invalid input.
goto :close

:delete
echo Removing scheduled task...
schtasks /delete /tn "GDNewsBot" /f >nul
if errorlevel 1 (
    echo.
    echo Could not delete it - it may not exist, or Task Scheduler may need to be run as administrator.
) else (
    echo Done. GDNewsBot will no longer run automatically.
)
TIMEOUT /t 3 /nobreak >nul
exit /b 0


:close
cls
echo Closing.
TIMEOUT /t 1 >nul
cls
echo Closing..
TIMEOUT /t 1 >nul
cls
echo Closing...
TIMEOUT /t 1 >nul
exit /b 1
