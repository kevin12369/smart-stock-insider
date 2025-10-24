@echo off
REM 智股通项目Windows构建脚本
REM 打包命名规则: 项目缩写-系统-支持的架构-版本号

setlocal enabledelayedexpansion

REM 配置变量
set PROJECT_NAME=ssi
set SYSTEM=windows
set ARCH=amd64
set VERSION=v0.0.1-dev
set OUTPUT_NAME=%PROJECT_NAME%-%SYSTEM%-%ARCH%-%VERSION%

REM 颜色定义
set RED=[91m
set GREEN=[92m
set YELLOW=[93m
set BLUE=[94m
set NC=[0m

REM 打印消息函数
:print_success
echo %GREEN%✅ %~1%NC%
goto :eof

:print_info
echo %BLUE%ℹ️  %~1%NC%
goto :eof

:print_warning
echo %YELLOW%⚠️  %~1%NC%
goto :eof

:print_error
echo %RED%❌ %~1%NC%
goto :eof

REM 主构建流程
:main
echo.
call :print_info 🏗️  智股通项目Windows构建
echo ======================================
echo.

REM 检查依赖
call :print_info 检查构建依赖...

where go >nul 2>nul
if %errorlevel% neq 0 (
    call :print_error Go未安装，请先安装Go 1.21+
    exit /b 1
)

where wails >nul 2>nul
if %errorlevel% neq 0 (
    call :print_error Wails CLI未安装，请先安装Wails
    exit /b 1
)

where node >nul 2>nul
if %errorlevel% neq 0 (
    call :print_error Node.js未安装，请先安装Node.js 18+
    exit /b 1
)

call :print_success 所有依赖检查通过

REM 清理旧的构建文件
call :print_info 清理旧的构建文件...

del /q *.exe 2>nul
del /q *.installer 2>nul
del /q *.sha256 2>nul

if exist build (
    rmdir /s /q build
)

call :print_success 清理完成

REM 更新版本号
call :print_info 更新版本号: %VERSION%
echo %VERSION% > VERSION
call :print_success 版本号已更新

REM 构建前端
call :print_info 构建前端应用...

cd frontend
call npm install
if %errorlevel% neq 0 (
    call :print_error 前端依赖安装失败
    exit /b 1
)

call npm run build
if %errorlevel% neq 0 (
    call :print_error 前端构建失败
    exit /b 1
)

cd ..
call :print_success 前端构建完成

REM 构建后端
call :print_info 构建后端应用...

call go mod tidy
call go mod download

call :print_success 后端依赖准备完成

REM 构建应用
call :print_info 构建Wails应用...

call wails build -clean -upx
if %errorlevel% neq 0 (
    call :print_error 应用构建失败
    exit /b 1
)

call :print_success 应用构建完成

REM 重命名文件
call :print_info 重命名构建文件...

if exist "build\bin\smart-stock-insider.exe" (
    move "build\bin\smart-stock-insider.exe" "%OUTPUT_NAME%.exe"
    call :print_success 文件已重命名为: %OUTPUT_NAME%.exe
) else (
    call :print_error 构建的exe文件不存在
    exit /b 1
)

REM 生成校验和
call :print_info 生成文件校验和...

if exist "%OUTPUT_NAME%.exe" (
    powershell -Command "Get-FileHash '%OUTPUT_NAME%.exe' -Algorithm SHA256 | Select-Object -ExpandProperty Hash" > "%OUTPUT_NAME%.exe.sha256"
    call :print_success 校验和已生成: %OUTPUT_NAME%.exe.sha256

    call :print_info 文件信息:
    dir "%OUTPUT_NAME%.exe"
    echo.
    call :print_info SHA256校验和:
    type "%OUTPUT_NAME%.exe.sha256"
) else (
    call :print_error 目标文件不存在，无法生成校验和
)

REM 生成安装包
call :print_info 生成Windows安装包...

call wails build -nsis
if %errorlevel% equ 0 (
    if exist "build\bin\smart-stock-insider-installer.exe" (
        move "build\bin\smart-stock-insider-installer.exe" "%OUTPUT_NAME%-installer.exe"
        call :print_success 安装包已生成: %OUTPUT_NAME%-installer.exe
    )
) else (
    call :print_warning 安装包生成失败，但exe文件已生成
)

REM 显示构建信息
echo.
call :print_info 🎉 构建完成！
echo.
echo 📦 构建信息:
echo    项目名称: 智股通 ^(Smart Stock Insider^)
echo    构建文件: %OUTPUT_NAME%.exe
echo    版本号:   %VERSION%
echo    系统架构: %SYSTEM%-%ARCH%
echo.

if exist "%OUTPUT_NAME%.exe" (
    echo 📋 生成的文件:
    dir "%OUTPUT_NAME%.exe*"
)

echo.
call :print_info 🚀 使用方法:
echo    1. 直接运行: %OUTPUT_NAME%.exe
echo    2. 安装包:   %OUTPUT_NAME%-installer.exe
echo.

goto :eof

REM 处理命令行参数
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

REM 默认执行完整构建流程
call :main

goto :eof