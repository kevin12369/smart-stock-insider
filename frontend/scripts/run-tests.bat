@echo off
REM 前端测试运行脚本 - Windows版本
REM 支持多种测试模式和报告选项

setlocal enabledelayedexpansion

REM 默认参数
set TEST_MODE=unit
set COVERAGE=false
set WATCH=false
set REPORTER=verbose
set COMPONENT=

REM 解析命令行参数
:parse_args
if "%~1"=="" goto args_done
if "%~1"=="-c" (
    set COVERAGE=true
    shift
    goto parse_args
)
if "%~1"=="--coverage" (
    set COVERAGE=true
    shift
    goto parse_args
)
if "%~1"=="-w" (
    set WATCH=true
    shift
    goto parse_args
)
if "%~1"=="--watch" (
    set WATCH=true
    shift
    goto parse_args
)
if "%~1"=="-m" (
    set TEST_MODE=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--mode" (
    set TEST_MODE=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="-r" (
    set REPORTER=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--reporter" (
    set REPORTER=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--component" (
    set COMPONENT=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="-h" (
    goto show_help
)
if "%~1"=="--help" (
    goto show_help
)
echo Unknown option: %~1
exit /b 1

:args_done

REM 打印函数
:print_info
echo [INFO] %~1
goto :eof

:print_warning
echo [WARNING] %~1
goto :eof

:print_error
echo [ERROR] %~1
goto :eof

:print_header
echo ========================================
echo   Frontend Test Runner
echo ========================================
goto :eof

REM 显示帮助信息
:show_help
echo Usage: %~nx0 [OPTIONS]
echo.
echo Options:
echo   -c, --coverage     Generate coverage report
echo   -w, --watch        Run tests in watch mode
echo   -m, --mode MODE    Test mode: unit, integration, e2e, all
echo   -r, --reporter R   Reporter: verbose, dot, json, junit
echo   --component NAME   Run tests for specific component
echo   -h, --help         Show this help message
goto :eof

REM 检查依赖
:check_dependencies
call :print_info "Checking dependencies..."

npm list vitest >nul 2>&1
if %errorlevel% neq 0 (
    call :print_warning "vitest not found, installing..."
    npm install --save-dev vitest
)

if "%COVERAGE%"=="true" (
    npm list @vitest/coverage-v8 >nul 2>&1
    if %errorlevel% neq 0 (
        call :print_warning "@vitest/coverage-v8 not found, installing..."
        npm install --save-dev @vitest/coverage-v8
    )
)
goto :eof

REM 清理旧的测试结果
:cleanup_test_results
call :print_info "Cleaning up old test results..."

if exist coverage (
    rmdir /s /q coverage
)

if exist test-results (
    rmdir /s /q test-results
)

mkdir test-results
goto :eof

REM 运行单元测试
:run_unit_tests
call :print_info "Running unit tests..."

set test_command=npx vitest run
set test_pattern=src/test/**/*.test.{ts,tsx}

if not "%COMPONENT%"=="" (
    set test_pattern=src/test/components/%COMPONENT%/**/*.test.{ts,tsx}
)

if "%COVERAGE%"=="true" (
    set test_command=%test_command% --coverage
)

if "%WATCH%"=="true" (
    set test_command=npx vitest %test_pattern%
) else (
    set test_command=%test_command% %test_pattern%
)

echo %test_command%
%test_command%
if %errorlevel% neq 0 exit /b 1
goto :eof

REM 运行集成测试
:run_integration_tests
call :print_info "Running integration tests..."

set test_command=npx vitest run
set test_pattern=src/test/integration/**/*.test.{ts,tsx}

if "%COVERAGE%"=="true" (
    set test_command=%test_command% --coverage
)

%test_command% %test_pattern%
if %errorlevel% neq 0 exit /b 1
goto :eof

REM 运行E2E测试
:run_e2e_tests
call :print_info "Running E2E tests..."

npx playwright --version >nul 2>&1
if %errorlevel% neq 0 (
    call :print_error "Playwright not found. Install with: npm install --save-dev @playwright/test"
    exit /b 1
)

set test_command=npx playwright test
%test_command%
if %errorlevel% neq 0 exit /b 1
goto :eof

REM 运行所有测试
:run_all_tests
call :print_info "Running all tests..."

REM 运行单元测试
call :run_unit_tests

REM 运行集成测试
call :run_integration_tests

REM 运行E2E测试（如果存在）
if exist e2e (
    call :run_e2e_tests
)
goto :eof

REM 生成测试报告
:generate_reports
call :print_info "Generating test reports..."

if "%COVERAGE%"=="true" (
    if exist coverage (
        call :print_info "Coverage report generated in coverage/ directory"
    )
)

if exist test-results (
    call :print_info "Test results saved in test-results/ directory"
)
goto :eof

REM 主函数
:main
call :print_header

call :check_dependencies
call :cleanup_test_results

if "%TEST_MODE%"=="unit" (
    call :run_unit_tests
) else if "%TEST_MODE%"=="integration" (
    call :run_integration_tests
) else if "%TEST_MODE%"=="e2e" (
    call :run_e2e_tests
) else if "%TEST_MODE%"=="all" (
    call :run_all_tests
) else (
    call :print_error "Unknown test mode: %TEST_MODE%"
    call :print_info "Available modes: unit, integration, e2e, all"
    exit /b 1
)

call :generate_reports

call :print_info "Tests completed successfully!"
goto :eof

REM 错误处理
if %errorlevel% neq 0 (
    call :print_error "Test execution failed!"
    exit /b 1
)

REM 运行主函数
call :main %*