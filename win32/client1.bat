@echo off
title Toontown Online - Developer Mini-Server Launcher
cd..

rem Read the contents of PPYTHON_PATH into %PPYTHON_PATH%:
set /P PPYTHON_PATH=<PPYTHON_PATH

echo Toontown Online Developer Mini-Server Launcher
echo.
echo NOTE: Make sure that "mini-server" is enabled in your settings.json!
echo.


set TTOFF_LOGIN_TOKEN=dev
set TTOFF_GAME_SERVER=127.0.0.1

%PPYTHON_PATH% -m toontown.launcher.TTOffQuickStartLauncher
pause
