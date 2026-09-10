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
python "GD News Bot (DashWord).py"
if errorlevel 1 goto :error
TIMEOUT /t 1 /nobreak >nul
cls

echo Creating needed files, please wait..
python "GD Reddit Bot.py"
if errorlevel 1 goto :error
TIMEOUT /t 1 /nobreak >nul
cls

echo Creating needed files, please wait...
python "GD News Bot (Pointercrate).py"
if errorlevel 1 goto :error
TIMEOUT /t 1 /nobreak >nul
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
del "%~f0"
exit /b 0

:error
echo.
echo Something went wrong while running the last bot ΓÇö see the error above.
echo init.bat was NOT deleted, so you can fix the issue and run it again.
echo.
set "select="
set /p select=Insert 1 for attempting autofix or 2 for manual fixing, then press enter:

if "%select%"=="1" goto :autofix
if "%select%"=="2" goto :manual
echo Invalid input.
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
start "" D:\Discord\Webhooks\GD News\fix
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
