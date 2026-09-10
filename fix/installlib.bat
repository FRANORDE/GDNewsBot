@echo off
echo Are you sure you want to install the needed python libraries?
set "select="
set /p select=[Y(yes)/n(no)]:

if "%select%"=="y" goto :install
if "%select%"=="n" goto :close
echo Invalid input.
goto :close

:install
echo Installing needed libraries...
pip install requests beautifulsoup4 feedparser python-dotenv --quiet >nul
TIMEOUT /t 10 /nobreak >nul
echo Done.
TIMEOUT /t 1 /nobreak >nul
exit /b 1


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
