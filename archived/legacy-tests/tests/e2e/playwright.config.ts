/**
 * Playwright配置文件
 * 端到端测试框架配置
 */

import { defineConfig, devices } from '@playwright/test';
import path from 'path';

export default defineConfig({
  // 测试目录
  testDir: './tests',

  // 全局测试设置
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,

  // 报告配置
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'test-results.json' }],
    ['junit', { outputFile: 'test-results.xml' }],
    ['list'],
    process.env.CI ? ['github'] : ['html']
  ],

  // 全局设置
  use: {
    // 基础URL
    baseURL: process.env.BASE_URL || 'http://localhost:3000',

    // 截图配置
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',

    // 追踪配置
    trace: 'on-first-retry',

    // 浏览器上下文选项
    ignoreHTTPSErrors: true,

    // 视窗大小
    viewport: { width: 1280, height: 720 },

    // 用户代理
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',

    // 网络条件
    // offline: false,
    // colorScheme: 'light',
    // reducedMotion: 'reduce',
  },

  // 测试超时配置
  timeout: 30 * 1000,
  expect: {
    timeout: 5 * 1000
  },

  // 项目配置 - 支持多浏览器测试
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },

    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },

    // 移动端测试
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },

    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },

    // 平板测试
    {
      name: 'iPad',
      use: { ...devices['iPad Pro'] },
    },
  ],

  // 测试环境配置
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },

  // 输出目录
  outputDir: 'test-results/',

  // 全局设置文件
  globalSetup: require.resolve('./global-setup.ts'),
  globalTeardown: require.resolve('./global-teardown.ts'),
});