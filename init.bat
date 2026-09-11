@echo off
setlocal

if not exist .env (
    echo.
    echo ERROR: .env file not found.
    echo Copy .env.example to .env and fill in your Discord webhook URLs first.
    echo.
    pause
    exit /b 1
)

echo Creating needed files, please wait.
python "GD News Bot (DashWord).py" >nul
if errorlevel 1 goto :error
TIMEOUT /t 1 /nobreak >nul
cls

echo Creating needed files, please wait..
python "GD Reddit Bot.py" >nul
if errorlevel 1 goto :error
TIMEOUT /t 1 /nobreak >nul
cls

echo Creating needed files, please wait...
python "GD News Bot (Pointercrate).py" >nul
if errorlevel 1 goto :error
TIMEOUT /t 1 /nobreak >nul
cls

echo Setting up automatic scheduling, please wait.
set "START_TIME=15:00"
set "REPEAT=true"
set "REPEAT_INTERVAL=15"
if exist config.txt (
    for /f "usebackq eol=# tokens=1,2 delims==" %%A in ("config.txt") do (
        if /I "%%A"=="START_TIME" set "START_TIME=%%B"
        if /I "%%A"=="REPEAT" set "REPEAT=%%B"
        if /I "%%A"=="REPEAT_INTERVAL" set "REPEAT_INTERVAL=%%B"
    )
)

if exist read.bat del read.bat
echo @echo off> read.bat
echo cd /d "%%~dp0">> read.bat
echo python "GD News Bot (DashWord).py">> read.bat
echo python "GD Reddit Bot.py">> read.bat
echo python "GD News Bot (Pointercrate).py">> read.bat

if /I "%REPEAT%"=="true" (
    schtasks /create /tn "GDNewsBot" /tr "\"%~dp0read.bat\"" /sc daily /st %START_TIME% /ri %REPEAT_INTERVAL% /du 9999:59 /f >nul
) else (
    schtasks /create /tn "GDNewsBot" /tr "\"%~dp0read.bat\"" /sc daily /st %START_TIME% /f >nul
)
if errorlevel 1 (
    cls
    echo.
    echo WARNING: could not create the scheduled task automatically.
    echo read.bat was created, but you'll need to schedule it yourself in Task Scheduler
    echo ^(action: run read.bat, trigger: daily at 15:00, repeat every 15 minutes, indefinitely^).
    echo.
    pause
) else (
    cls
    echo Scheduled task "GDNewsBot" created successfully.
    if /I "%REPEAT%"=="true" (
        echo read.bat will run automatically every %REPEAT_INTERVAL% minutes, starting at %START_TIME% today.
    ) else (
        echo read.bat will run automatically once a day, at %START_TIME%.
    )
    TIMEOUT /t 3 /nobreak >nul
)

cls
echo Done, wait.
TIMEOUT /t 1 /nobreak >nul
cls
echo Closing.
TIMEOUT /t 1 >nul
cls
echo Closing..
TIMEOUT /t 1 >nul
cls
echo Closing...
TIMEOUT /t 1 >nul
del "lib.txt"
del "env.example"
del "%~f0"
exit /b 0

:error
echo.
echo Something went wrong while running the last bot - see the error above.
echo init.bat was NOT deleted, so you can fix the issue and run it again.
echo.
set "select="
set /p select=Insert 1 for attempting autofix or 2 for manual fixing, then press enter:

if "%select%"=="1" goto :autofix
if "%select%"=="2" goto :manual
echo Invalid input.
TIMEOUT /t 1 >nul
goto :exit

:autofix
echo Installing required libraries
python -m pip install -r lib.txt --quiet
TIMEOUT /t 10 >nul
echo Run this file again after it closes
TIMEOUT /t 1 >nul
exit /b 1

:manual
cls
echo Opening fix folder...
TIMEOUT /t 1 /nobreak
start "" fix
TIMEOUT /t 1 /nobreak
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

:exit
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
