@echo off
REM Smart Stock Insider Windows Build Script
REM Naming: Project-System-Architecture-Version

setlocal enabledelayedexpansion

REM Configuration
set PROJECT_NAME=ssi
set SYSTEM=windows
set ARCH=amd64
set VERSION=v0.0.1-dev
set OUTPUT_NAME=%PROJECT_NAME%-%SYSTEM%-%ARCH%-%VERSION%

REM Handle command line parameters
if "%1"=="clean" (
    call :clean_build
    goto :eof
)

if "%1"=="frontend" (
    call :build_frontend
    goto :eof
)

if "%1"=="backend" (
    call :build_backend
    goto :eof
)

if "%1"=="build" (
    call :build_application
    call :rename_output
    goto :eof
)

if "%1"=="package" (
    call :create_installer
    goto :eof
)

if "%1"=="checksum" (
    call :generate_checksum
    goto :eof
)

REM Default: execute full build process
call :main
goto :eof

REM Clean build files
:clean_build
echo.
echo [INFO] Cleaning build files...
del /q *.exe 2>nul
del /q *.installer 2>nul
del /q *.sha256 2>nul
if exist build rmdir /s /q build
echo [SUCCESS] Cleanup completed
goto :eof

REM Build frontend
:build_frontend
echo.
echo [INFO] Building frontend...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo [ERROR] Frontend dependencies installation failed
    exit /b 1
)
call npm run build
if %errorlevel% neq 0 (
    echo [ERROR] Frontend build failed
    exit /b 1
)
cd ..
echo [SUCCESS] Frontend build completed
goto :eof

REM Build backend
:build_backend
echo.
echo [INFO] Preparing backend dependencies...
call go mod tidy
call go mod download
echo [SUCCESS] Backend dependencies ready
goto :eof

REM Build application
:build_application
echo.
echo [INFO] Building Wails application...
call wails build -clean -upx
if %errorlevel% neq 0 (
    echo [ERROR] Application build failed
    exit /b 1
)
echo [SUCCESS] Application build completed
goto :eof

REM Rename output
:rename_output
echo.
echo [INFO] Renaming build files...
if exist "build\bin\smart-stock-insider.exe" (
    move "build\bin\smart-stock-insider.exe" "%OUTPUT_NAME%.exe"
    echo [SUCCESS] File renamed to: %OUTPUT_NAME%.exe
) else (
    echo [ERROR] Built exe file does not exist
    exit /b 1
)
goto :eof

REM Generate checksum
:generate_checksum
echo.
echo [INFO] Generating file checksum...
if exist "%OUTPUT_NAME%.exe" (
    powershell -Command "Get-FileHash '%OUTPUT_NAME%.exe' -Algorithm SHA256 | Select-Object -ExpandProperty Hash" > "%OUTPUT_NAME%.exe.sha256"
    echo [SUCCESS] Checksum generated: %OUTPUT_NAME%.exe.sha256
    echo [INFO] File info:
    dir "%OUTPUT_NAME%.exe"
    echo.
    echo [INFO] SHA256 checksum:
    type "%OUTPUT_NAME%.exe.sha256"
) else (
    echo [ERROR] Target file does not exist, cannot generate checksum
)
goto :eof

REM Create installer
:create_installer
echo.
echo [INFO] Creating Windows installer...
call wails build -nsis
if %errorlevel% equ 0 (
    if exist "build\bin\smart-stock-insider-installer.exe" (
        move "build\bin\smart-stock-insider-installer.exe" "%OUTPUT_NAME%-installer.exe"
        echo [SUCCESS] Installer created: %OUTPUT_NAME%-installer.exe
    )
) else (
    echo [WARNING] Installer creation failed, but exe file was generated
)
goto :eof

REM Main build process
:main
echo.
echo [INFO] Smart Stock Insider Windows Build Process
echo ======================================
echo.

REM Check dependencies
echo [INFO] Checking build dependencies...
where go >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Go is not installed, please install Go 1.21+
    exit /b 1
)
where wails >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Wails CLI is not installed, please install Wails
    exit /b 1
)
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed, please install Node.js 18+
    exit /b 1
)
echo [SUCCESS] All dependencies checked

REM Clean old build files
call :clean_build

REM Update version
echo [INFO] Updating version: %VERSION%
echo %VERSION% > VERSION
echo [SUCCESS] Version updated

REM Build frontend
call :build_frontend

REM Build backend
call :build_backend

REM Build application
call :build_application

REM Rename files
call :rename_output

REM Generate checksum
call :generate_checksum

REM Create installer
call :create_installer

REM Show build info
echo.
echo [SUCCESS] Build completed successfully!
echo.
echo Build Information:
echo    Project: Smart Stock Insider
echo    Build file: %OUTPUT_NAME%.exe
echo    Version: %VERSION%
echo    Architecture: %SYSTEM%-%ARCH%
echo.

if exist "%OUTPUT_NAME%.exe" (
    echo Generated files:
    dir "%OUTPUT_NAME%.exe*"
)

echo.
echo [INFO] Usage:
echo    1. Run directly: %OUTPUT_NAME%.exe
echo    2. Installer: %OUTPUT_NAME%-installer.exe
echo.

goto :eof