/**
 * 简化的性能测试检查器
 * 验证性能测试框架的基本功能
 */

const fs = require('fs');
const path = require('path');

console.log('🚀 智股通性能测试框架检查');
console.log('================================');

// 1. 检查文件存在性
function checkFiles() {
    console.log('\n📁 检查测试文件存在性:');

    const files = [
        'locustfile.py',
        'run-performance-tests.py',
        'locust.conf',
        '../e2e/playwright.config.ts',
        '../e2e/helpers/test-helpers.ts',
        '../e2e/fixtures/test-data.ts',
        '../reports/generate-test-report.py'
    ];

    let existsCount = 0;
    files.forEach(file => {
        const fullPath = path.join(__dirname, file);
        if (fs.existsSync(fullPath)) {
            console.log(`  ✅ ${file}`);
            existsCount++;
        } else {
            console.log(`  ❌ ${file} - 文件不存在`);
        }
    });

    console.log(`\n📊 文件存在率: ${existsCount}/${files.length} (${Math.round(existsCount/files.length*100)}%)`);
    return existsCount === files.length;
}

// 2. 检查Python文件语法
function checkPythonSyntax() {
    console.log('\n🐍 检查Python文件语法:');

    const { execSync } = require('child_process');
    const pythonFiles = [
        'locustfile.py',
        'run-performance-tests.py',
        '../reports/generate-test-report.py'
    ];

    let validCount = 0;
    pythonFiles.forEach(file => {
        const fullPath = path.join(__dirname, file);
        if (fs.existsSync(fullPath)) {
            try {
                execSync(`python -m py_compile "${fullPath}"`, { stdio: 'pipe' });
                console.log(`  ✅ ${file} - 语法正确`);
                validCount++;
            } catch (error) {
                console.log(`  ❌ ${file} - 语法错误`);
            }
        }
    });

    console.log(`\n📊 Python语法正确率: ${validCount}/${pythonFiles.length} (${Math.round(validCount/pythonFiles.length*100)}%)`);
    return validCount === pythonFiles.length;
}

// 3. 检查性能测试脚本功能
function checkPerformanceScript() {
    console.log('\n⚡ 检查性能测试脚本功能:');

    const { execSync } = require('child_process');
    const scriptPath = path.join(__dirname, 'run-performance-tests.py');

    if (fs.existsSync(scriptPath)) {
        try {
            const result = execSync('python run-performance-tests.py --help', {
                cwd: __dirname,
                encoding: 'utf8',
                timeout: 5000
            });

            if (result.includes('usage:')) {
                console.log('  ✅ 性能测试脚本 - 功能正常');
                return true;
            } else {
                console.log('  ❌ 性能测试脚本 - 输出异常');
                return false;
            }
        } catch (error) {
            console.log(`  ❌ 性能测试脚本 - 执行错误: ${error.message}`);
            return false;
        }
    } else {
        console.log('  ❌ 性能测试脚本 - 文件不存在');
        return false;
    }
}

// 4. 检查Locust配置
function checkLocustConfig() {
    console.log('\n🦗 检查Locust配置:');

    const configPath = path.join(__dirname, 'locust.conf');

    if (fs.existsSync(configPath)) {
        try {
            const content = fs.readFileSync(configPath, 'utf8');

            // 检查关键配置项
            const requiredConfigs = [
                'host = http://localhost:8000',
                'users = 100',
                'spawn-rate = 10',
                'run-time = 300'
            ];

            let configCount = 0;
            requiredConfigs.forEach(config => {
                if (content.includes(config)) {
                    console.log(`  ✅ ${config}`);
                    configCount++;
                } else {
                    console.log(`  ❌ 缺少配置: ${config}`);
                }
            });

            console.log(`\n📊 配置完整性: ${configCount}/${requiredConfigs.length} (${Math.round(configCount/requiredConfigs.length*100)}%)`);
            return configCount === requiredConfigs.length;
        } catch (error) {
            console.log(`  ❌ 读取配置文件失败: ${error.message}`);
            return false;
        }
    } else {
        console.log('  ❌ Locust配置文件不存在');
        return false;
    }
}

// 5. 检查前端性能测试文件
function checkFrontendPerfFile() {
    console.log('\n🎨 检查前端性能测试文件:');

    const perfFilePath = path.join(__dirname, 'frontend-performance.spec.ts');

    if (fs.existsSync(perfFilePath)) {
        try {
            const content = fs.readFileSync(perfFilePath, 'utf8');

            // 检查关键测试函数
            const testFunctions = [
                '页面加载性能测试',
                '资源加载性能测试',
                'JavaScript执行性能测试',
                '内存使用测试',
                '交互响应性能测试'
            ];

            let testCount = 0;
            testFunctions.forEach(testName => {
                if (content.includes(testName)) {
                    console.log(`  ✅ ${testName}`);
                    testCount++;
                } else {
                    console.log(`  ❌ 缺少测试: ${testName}`);
                }
            });

            console.log(`\n📊 测试完整性: ${testCount}/${testFunctions.length} (${Math.round(testCount/testFunctions.length*100)}%)`);
            return testCount >= 3; // 至少要有3个测试
        } catch (error) {
            console.log(`  ❌ 读取前端性能测试文件失败: ${error.message}`);
            return false;
        }
    } else {
        console.log('  ❌ 前端性能测试文件不存在');
        return false;
    }
}

// 6. 生成检查报告
function generateReport(results) {
    console.log('\n📋 性能测试框架检查报告');
    console.log('================================');

    const categories = Object.keys(results);
    const passedCategories = categories.filter(cat => results[cat]);
    const totalScore = Math.round((passedCategories.length / categories.length) * 100);

    console.log(`\n🎯 总体评分: ${totalScore}%`);
    console.log(`通过项目: ${passedCategories.length}/${categories.length}`);

    console.log('\n📊 详细结果:');
    categories.forEach(category => {
        const status = results[category] ? '✅ 通过' : '❌ 失败';
        const percentage = results[category] ? '100%' : '0%';
        console.log(`  ${category}: ${status} (${percentage})`);
    });

    // 给出建议
    console.log('\n💡 建议:');
    if (totalScore >= 80) {
        console.log('  🚀 性能测试框架基本就绪，可以开始测试');
    } else if (totalScore >= 60) {
        console.log('  🔧 性能测试框架需要一些修复，建议先解决失败项目');
    } else {
        console.log('  ⚠️ 性能测试框架需要重大修复，建议重新检查配置');
    }

    // 具体建议
    if (!results.files) {
        console.log('  - 确保所有测试文件都已创建');
    }
    if (!results.python) {
        console.log('  - 检查Python文件语法错误');
    }
    if (!results.script) {
        console.log('  - 检查性能测试脚本的依赖和配置');
    }
    if (!results.config) {
        console.log('  - 完善Locust配置文件');
    }
    if (!results.frontend) {
        console.log('  - 安装Playwright依赖或修复TypeScript配置');
    }

    return totalScore;
}

// 主函数
function main() {
    const results = {
        files: checkFiles(),
        python: checkPythonSyntax(),
        script: checkPerformanceScript(),
        config: checkLocustConfig(),
        frontend: checkFrontendPerfFile()
    };

    const score = generateReport(results);

    console.log(`\n🏁 检查完成，总体评分: ${score}%`);
    return score;
}

// 如果直接运行此脚本
if (require.main === module) {
    main();
}

module.exports = { main };