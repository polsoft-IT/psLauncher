@echo off
REM ─────────────────────────────────────────────
REM  psLauncher - uruchamianie programu
REM  Launcher script for psLauncher.py
REM ─────────────────────────────────────────────

REM Przejdz do katalogu, w ktorym znajduje sie ten plik .bat
cd /d "%~dp0"

REM 1) Sprobuj uzyc interpretera z lokalnego srodowiska venv (jesli istnieje)
if exist ".venv\Scripts\pythonw.exe" (
    start "" ".venv\Scripts\pythonw.exe" "psLauncher.py" %*
    exit /b 0
)

if exist ".venv\Scripts\python.exe" (
    start "" ".venv\Scripts\python.exe" "psLauncher.py" %*
    exit /b 0
)

REM 2) Fallback: systemowy Python (pythonw = bez okna konsoli)
where pythonw.exe >nul 2>nul
if %errorlevel%==0 (
    start "" pythonw.exe "psLauncher.py" %*
    exit /b 0
)

REM 3) Ostatecznosc: zwykly python w konsoli
python "psLauncher.py" %*
pause
