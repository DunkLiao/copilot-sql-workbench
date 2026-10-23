@echo off
setlocal

cd /d "%~dp0"
echo Closing all active Google Colab sessions and verifying the result...
echo.

python "%~dp0close_colab_sessions.py"
set "RESULT=%ERRORLEVEL%"

echo.
if "%RESULT%"=="0" (
    echo SUCCESS: All Colab sessions are closed.
) else if "%RESULT%"=="2" (
    echo CANCELLED: No sessions were closed.
) else (
    echo ERROR: The sessions could not all be confirmed closed. Review the messages above.
)

echo.
pause
exit /b %RESULT%
