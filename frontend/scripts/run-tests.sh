#!/bin/bash

# 前端测试运行脚本
# 支持多种测试模式和报告选项

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Frontend Test Runner${NC}"
    echo -e "${BLUE}================================${NC}"
}

# 默认参数
TEST_MODE="unit"
COVERAGE=false
WATCH=false
REPORTER="verbose"
COMPONENT=""

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -w|--watch)
            WATCH=true
            shift
            ;;
        -m|--mode)
            TEST_MODE="$2"
            shift 2
            ;;
        -r|--reporter)
            REPORTER="$2"
            shift 2
            ;;
        --component)
            COMPONENT="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -c, --coverage     Generate coverage report"
            echo "  -w, --watch        Run tests in watch mode"
            echo "  -m, --mode MODE    Test mode: unit, integration, e2e, all"
            echo "  -r, --reporter R   Reporter: verbose, dot, json, junit"
            echo "  --component NAME   Run tests for specific component"
            echo "  -h, --help         Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# 检查依赖
check_dependencies() {
    print_message "Checking dependencies..."

    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed"
        exit 1
    fi

    if ! npm list vitest &> /dev/null; then
        print_warning "vitest not found, installing..."
        npm install --save-dev vitest
    fi

    if [ "$COVERAGE" = true ] && ! npm list @vitest/coverage-v8 &> /dev/null; then
        print_warning "@vitest/coverage-v8 not found, installing..."
        npm install --save-dev @vitest/coverage-v8
    fi
}

# 清理旧的测试结果
cleanup_test_results() {
    print_message "Cleaning up old test results..."

    if [ -d "coverage" ]; then
        rm -rf coverage
    fi

    if [ -d "test-results" ]; then
        rm -rf test-results
    fi

    mkdir -p test-results
}

# 运行单元测试
run_unit_tests() {
    print_message "Running unit tests..."

    local test_command="npx vitest run"
    local test_pattern="src/test/**/*.test.{ts,tsx}"

    if [ -n "$COMPONENT" ]; then
        test_pattern="src/test/components/${COMPONENT}/**/*.test.{ts,tsx}"
    fi

    if [ "$COVERAGE" = true ]; then
        test_command="$test_command --coverage"
    fi

    if [ "$WATCH" = true ]; then
        test_command="npx vitest $test_pattern"
    else
        test_command="$test_command $test_pattern"
    fi

    echo "$test_command"
    eval "$test_command"
}

# 运行集成测试
run_integration_tests() {
    print_message "Running integration tests..."

    local test_command="npx vitest run"
    local test_pattern="src/test/integration/**/*.test.{ts,tsx}"

    if [ "$COVERAGE" = true ]; then
        test_command="$test_command --coverage"
    fi

    eval "$test_command $test_pattern"
}

# 运行E2E测试
run_e2e_tests() {
    print_message "Running E2E tests..."

    if ! command -v npx playwright &> /dev/null; then
        print_error "Playwright not found. Install with: npm install --save-dev @playwright/test"
        exit 1
    fi

    local test_command="npx playwright test"

    eval "$test_command"
}

# 运行所有测试
run_all_tests() {
    print_message "Running all tests..."

    # 运行单元测试
    run_unit_tests

    # 运行集成测试
    run_integration_tests

    # 运行E2E测试（如果存在）
    if [ -d "e2e" ]; then
        run_e2e_tests
    fi
}

# 生成测试报告
generate_reports() {
    print_message "Generating test reports..."

    if [ "$COVERAGE" = true ] && [ -d "coverage" ]; then
        print_message "Coverage report generated in coverage/ directory"

        # 打开覆盖率报告（如果在开发环境）
        if [ "$WATCH" = false ] && command -v open &> /dev/null; then
            open coverage/index.html
        fi
    fi

    # 合并测试结果
    if [ -d "test-results" ]; then
        print_message "Test results saved in test-results/ directory"
    fi
}

# 主函数
main() {
    print_header

    check_dependencies
    cleanup_test_results

    case $TEST_MODE in
        unit)
            run_unit_tests
            ;;
        integration)
            run_integration_tests
            ;;
        e2e)
            run_e2e_tests
            ;;
        all)
            run_all_tests
            ;;
        *)
            print_error "Unknown test mode: $TEST_MODE"
            print_message "Available modes: unit, integration, e2e, all"
            exit 1
            ;;
    esac

    generate_reports

    print_message "Tests completed successfully!"
}

# 错误处理
trap 'print_error "Test execution failed!"; exit 1' ERR

# 运行主函数
main "$@"