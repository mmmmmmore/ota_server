@echo off
REM Build script for OTA Management Desktop Application (Windows)

setlocal enabledelayedexpansion

echo.
echo ============================================
echo OTA Management Desktop - Build Script (Windows)
echo ============================================
echo.

REM Check Node.js version
node --version
npm --version

echo.
echo Build options:
echo 1 - NSIS Installer (.exe) - Recommended for distribution
echo 2 - Portable Executable - No installation needed
echo 3 - Both NSIS and Portable
echo.

set /p choice="Select option (1-3): "

if "%choice%"=="1" (
    echo Building NSIS installer...
    call npm run build-win-exe
) else if "%choice%"=="2" (
    echo Building portable executable...
    call npm run build-win-portable
) else if "%choice%"=="3" (
    echo Building NSIS and portable...
    call npm run build-win
) else (
    echo Invalid option
    exit /b 1
)

echo.
echo Build completed successfully!
echo.
echo Output directory: .\dist
echo.

dir /s .\dist\*.exe

echo.
echo Done! 
pause
