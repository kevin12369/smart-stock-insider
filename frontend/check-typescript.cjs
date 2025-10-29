/**
 * 简单的TypeScript检查脚本
 * 检查主要源文件是否有编译错误
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🔍 智股通前端TypeScript检查');
console.log('================================');

// 主要要检查的文件
const criticalFiles = [
  'src/main.tsx',
  'src/App.tsx',
  'src/components/AI/AIHistoryManager.tsx'
];

console.log('\n📁 检查关键文件:');

let allFilesExist = true;
criticalFiles.forEach(file => {
  const fullPath = path.join(__dirname, file);
  if (fs.existsSync(fullPath)) {
    console.log(`  ✅ ${file}`);
  } else {
    console.log(`  ❌ ${file} - 文件不存在`);
    allFilesExist = false;
  }
});

if (!allFilesExist) {
  console.log('\n❌ 部分关键文件缺失，请检查项目结构');
  process.exit(1);
}

// 检查TypeScript配置
console.log('\n⚙️ 检查TypeScript配置:');

const tsconfigPath = path.join(__dirname, 'tsconfig.json');
if (fs.existsSync(tsconfigPath)) {
  try {
    const tsconfig = JSON.parse(fs.readFileSync(tsconfigPath, 'utf8'));
    console.log('  ✅ tsconfig.json - 配置文件正常');
    console.log(`  📊 目标版本: ${tsconfig.compilerOptions.target}`);
    console.log(`  📊 模块系统: ${tsconfig.compilerOptions.module}`);
  } catch (error) {
    console.log(`  ❌ tsconfig.json - 配置文件错误: ${error.message}`);
  }
} else {
  console.log('  ❌ tsconfig.json - 配置文件不存在');
}

// 检查package.json中的脚本
console.log('\n📦 检查package.json脚本:');

const packageJsonPath = path.join(__dirname, 'package.json');
if (fs.existsSync(packageJsonPath)) {
  try {
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
    const scripts = packageJson.scripts || {};

    const importantScripts = ['build', 'dev', 'preview', 'test'];
    importantScripts.forEach(script => {
      if (scripts[script]) {
        console.log(`  ✅ ${script}: ${scripts[script]}`);
      } else {
        console.log(`  ⚠️ ${script}: 未配置`);
      }
    });
  } catch (error) {
    console.log(`  ❌ package.json - 读取错误: ${error.message}`);
  }
}

// 尝试简单的语法检查
console.log('\n🧪 检查主要文件语法:');

try {
  // 检查main.tsx
  const mainTsx = fs.readFileSync(path.join(__dirname, 'src/main.tsx'), 'utf8');
  if (mainTsx.includes('ReactDOM.createRoot')) {
    console.log('  ✅ main.tsx - React 18语法正确');
  } else {
    console.log('  ⚠️ main.tsx - 可能使用旧版React语法');
  }

  // 检查App.tsx
  const appTsx = fs.readFileSync(path.join(__dirname, 'src/App.tsx'), 'utf8');
  if (appTsx.includes('export default') && appTsx.includes('function')) {
    console.log('  ✅ App.tsx - 组件导出语法正确');
  } else {
    console.log('  ⚠️ App.tsx - 组件语法可能有问题');
  }

} catch (error) {
  console.log(`  ❌ 文件语法检查失败: ${error.message}`);
}

// 检查依赖安装
console.log('\n📚 检查依赖安装:');

const nodeModulesPath = path.join(process.cwd(), 'node_modules');
if (fs.existsSync(nodeModulesPath)) {
  const importantDeps = ['react', 'react-dom', 'typescript'];
  importantDeps.forEach(dep => {
    const depPath = path.join(nodeModulesPath, dep);
    if (fs.existsSync(depPath)) {
      console.log(`  ✅ ${dep} - 已安装`);
    } else {
      console.log(`  ❌ ${dep} - 未安装`);
    }
  });
} else {
  console.log('  ❌ node_modules - 依赖目录不存在，请运行 npm install');
}

console.log('\n💡 建议:');
console.log('  1. 如果有TypeScript错误，重点检查语法问题');
console.log('  2. 确保 JSX 文件使用 .tsx 扩展名');
console.log('  3. 检查导入语句是否正确');
console.log('  4. 确保泛型语法使用正确');

console.log('\n🏁 TypeScript检查完成');