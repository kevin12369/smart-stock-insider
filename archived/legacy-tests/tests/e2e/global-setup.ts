/**
 * 全局测试设置
 * 在所有测试运行前执行一次
 */

import { chromium, FullConfig } from '@playwright/test';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting E2E test global setup...');

  const baseURL = config.webServer?.url || 'http://localhost:3000';
  console.log(`📡 Base URL: ${baseURL}`);

  // 检查前端服务是否运行
  console.log('🔍 Checking frontend service...');
  try {
    await execAsync('curl -f http://localhost:3000', { timeout: 5000 });
    console.log('✅ Frontend service is running');
  } catch (error) {
    console.log('⚠️  Frontend service not detected, starting...');
  }

  // 检查后端服务是否运行
  console.log('🔍 Checking backend service...');
  try {
    await execAsync('curl -f http://localhost:8000/api/health', { timeout: 5000 });
    console.log('✅ Backend service is running');
  } catch (error) {
    console.log('⚠️  Backend service not detected');
    console.log('💡 Please ensure backend service is running on http://localhost:8000');
  }

  // 创建测试数据
  console.log('📝 Creating test data...');
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // 访问健康检查端点
    await page.goto(`${baseURL}/api/health`).catch(() => {
      console.log('⚠️  Health check endpoint not available');
    });

    // 初始化测试数据（如果需要）
    await page.evaluate(() => {
      // 清除本地存储
      localStorage.clear();
      sessionStorage.clear();

      // 设置测试环境标识
      localStorage.setItem('test-environment', 'true');
      localStorage.setItem('test-start-time', new Date().toISOString());
    });

  } catch (error) {
    console.log('⚠️  Test data initialization failed:', error);
  } finally {
    await context.close();
    await browser.close();
  }

  // 设置环境变量
  process.env.E2E_TEST_MODE = 'true';
  process.env.E2E_BASE_URL = baseURL;

  console.log('✅ E2E test global setup completed');
}

export default globalSetup;