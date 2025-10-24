@echo off
echo ========================================
echo 智股通 Windows 构建脚本
echo ========================================

:: 设置环境变量
set GO111MODULE=on
set CGO_ENABLED=1

:: 检查必要工具
echo [1/6] 检查构建环境...

:: 检查Go
where go >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo 错误: 未找到Go，请先安装Go 1.24+
    pause
    exit /b 1
)

:: 检查Node.js
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo 错误: 未找到Node.js，请先安装Node.js 18+
    pause
    exit /b 1
)

:: 检查Wails
where wails >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo 安装Wails CLI...
    go install github.com/wailsapp/wails/v2/cmd/wails@latest
)

echo Go版本:
go version

echo Node.js版本:
node --version

echo Wails版本:
wails version

:: 清理旧构建
echo [2/6] 清理旧构建文件...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

:: 安装前端依赖
echo [3/6] 安装前端依赖...
cd frontend
call npm install
if %ERRORLEVEL% neq 0 (
    echo 错误: 前端依赖安装失败
    pause
    exit /b 1
)
cd ..

:: 安装Go依赖
echo [4/6] 安装Go依赖...
go mod tidy
if %ERRORLEVEL% neq 0 (
    echo 错误: Go依赖安装失败
    pause
    exit /b 1
)

:: 前端构建
echo [5/6] 构建前端...
cd frontend
call npm run build
if %ERRORLEVEL% neq 0 (
    echo 错误: 前端构建失败
    pause
    exit /b 1
)
cd ..

:: Wails应用构建
echo [6/6] 构建桌面应用...
wails build -clean -web2 -upx
if %ERRORLEVEL% neq 0 (
    echo 错误: Wails构建失败
    pause
    exit /b 1
)

:: 创建发布目录
if not exist "release" mkdir "release"

:: 复制构建文件
echo 复制构建文件到release目录...
if exist "dist\smart-stock-insider.exe" (
    copy "dist\smart-stock-insider.exe" "release\"
    copy "dist\*.dll" "release\" 2>nul
)

:: 复制配置文件
if exist "wails.json" copy "wails.json" "release\"

:: 创建数据目录
if not exist "release\data" mkdir "release\data"

:: 复制数据库架构文件
if exist "data\smart_stock.db" copy "data\smart_stock.db" "release\data\"

:: 创建日志目录
if not exist "release\logs" mkdir "release\logs"

:: 复制备份脚本
if exist "scripts\backup-database.bat" copy "scripts\backup-database.bat" "release\"

echo ========================================
echo 构建完成!
echo ========================================
echo 可执行文件: release\smart-stock-insider.exe
echo 数据目录: release\data\
echo 日志目录: release\logs\
echo.
echo 运行应用: release\smart-stock-insider.exe
echo.

:: 询问是否立即运行
set /p run="是否立即运行应用? (y/n): "
if /i "%run%"=="y" (
    echo 启动应用...
    cd release
    start "" smart-stock-insider.exe
)

pause