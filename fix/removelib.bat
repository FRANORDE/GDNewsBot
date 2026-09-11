@echo off
echo Are you sure you want to uninstall the needed python libraries?
set "select="
set /p select=[Y(yes)/n(no)]:

if /I "%select%"=="y" goto :uninstall
if /I "%select%"=="n" goto :close
echo Invalid input.
goto :close

:uninstall
echo Removing needed libraries...
python -m pip uninstall requests beautifulsoup4 feedparser python-dotenv --quiet -y >nul
TIMEOUT /t 10 /nobreak >nul
echo Done.
TIMEOUT /t 1 /nobreak >nul
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
