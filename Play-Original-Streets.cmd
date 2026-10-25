@echo off
cd /d "%~dp0"
if not exist "preserved-game-states\2026-10-25-before-map-work\runtime\RunnerGame.exe" goto development
cd preserved-game-states\2026-10-25-before-map-work
runtime\RunnerGame.exe
goto finished
:development
dotnet run --project RunnerGame
:finished
if errorlevel 1 pause
