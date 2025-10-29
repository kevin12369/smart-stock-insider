/**
 * 全局测试拆卸
 * 在所有测试运行后执行一次
 */

import { FullConfig } from '@playwright/test';
import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs';
import path from 'path';

const execAsync = promisify(exec);

async function globalTeardown(config: FullConfig) {
  console.log('🧹 Starting E2E test global teardown...');

  // 清理测试数据
  console.log('🗑️  Cleaning up test data...');
  try {
    // 删除测试报告目录（如果需要）
    const reportDir = path.join(process.cwd(), 'playwright-report');
    if (fs.existsSync(reportDir)) {
      console.log('📊 Test reports saved to:', reportDir);
    }

    // 清理临时文件
    const tempDirs = [
      path.join(process.cwd(), 'test-results'),
      path.join(process.cwd(), '.playwright-cache'),
    ];

    for (const dir of tempDirs) {
      if (fs.existsSync(dir)) {
        console.log('📁 Temporary files preserved in:', dir);
      }
    }

  } catch (error) {
    console.log('⚠️  Cleanup warning:', error);
  }

  // 生成测试总结
  console.log('📈 Generating test summary...');
  try {
    const resultsFile = path.join(process.cwd(), 'test-results.json');
    if (fs.existsSync(resultsFile)) {
      const results = JSON.parse(fs.readFileSync(resultsFile, 'utf8'));
      console.log(`📊 Test Summary:`);
      console.log(`   Total tests: ${results.suites?.reduce((sum: number, suite: any) =>
        sum + (suite.specs?.length || 0), 0) || 0}`);
      console.log(`   Passed: ${results.suites?.reduce((sum: number, suite: any) =>
        sum + (suite.specs?.filter((spec: any) => spec.ok).length || 0), 0) || 0}`);
      console.log(`   Failed: ${results.suites?.reduce((sum: number, suite: any) =>
        sum + (suite.specs?.filter((spec: any) => !spec.ok).length || 0), 0) || 0}`);
    }
  } catch (error) {
    console.log('⚠️  Could not generate test summary:', error);
  }

  // 清理环境变量
  delete process.env.E2E_TEST_MODE;
  delete process.env.E2E_BASE_URL;

  console.log('✅ E2E test global teardown completed');
}

export default globalTeardown;