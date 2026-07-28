@echo off
REM psLauncher Build Script (One-File Mode)
REM Builds psLauncher.exe using PyInstaller with icon and version info
REM Uses one-file mode (single executable file)

echo ========================================
echo psLauncher Build Script (One-File)
echo ========================================
echo.

REM Change to parent directory (main project folder)
cd ..

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [ERROR] PyInstaller is not installed.
    echo Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo [ERROR] Failed to install PyInstaller
        pause
        exit /b 1
    )
)

REM Check if icon file exists
if not exist "icons\psl-ico.ico" (
    echo [WARNING] Icon file icons\psl-ico.ico not found
    echo The build will continue without icon
)

REM Check if version info file exists
if not exist "builder\version_info.txt" (
    echo [WARNING] builder\version_info.txt not found
    echo The build will continue without version info
)

REM Check if spec file exists
if not exist "builder\psLauncher.spec" (
    echo [ERROR] builder\psLauncher.spec not found
    pause
    exit /b 1
)

REM Check if main script exists
if not exist "psLauncher.py" (
    echo [ERROR] psLauncher.py not found
    pause
    exit /b 1
)

echo [INFO] Starting build process...
echo [INFO] Mode: One-file (single executable)
echo [INFO] UPX: Disabled (faster startup)
echo [INFO] Hidden imports: Minimal
echo.

REM Clean previous build
if exist "build" (
    echo [INFO] Cleaning previous build directory...
    rmdir /s /q build
)
if exist "dist" (
    echo [INFO] Cleaning previous dist directory...
    rmdir /s /q dist
)

REM Run PyInstaller with spec file
echo [INFO] Building executable with PyInstaller...
pyinstaller builder\psLauncher.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

REM Clean build folder after successful compilation
if exist "build" (
    echo [INFO] Cleaning build folder...
    rmdir /s /q build
)

echo.
echo ========================================
echo [SUCCESS] Build completed successfully!
echo ========================================
echo.
echo Executable location: dist\psLauncher.exe
echo.

REM Check if executable was created
if exist "dist\psLauncher.exe" (
    echo [INFO] Executable size:
    dir "dist\psLauncher.exe" | find "psLauncher.exe"
    echo.
    echo [INFO] You can now run dist\psLauncher.exe
    echo [INFO] To distribute: just share the psLauncher.exe file
) else (
    echo [WARNING] Executable not found in dist directory
)

echo.
pause
