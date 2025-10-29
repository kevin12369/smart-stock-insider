/**
 * Jest配置文件
 * 兼容Vitest测试环境
 */

module.exports = {
  // 测试环境
  testEnvironment: 'jsdom',

  // 设置文件
  setupFilesAfterEnv: ['<rootDir>/setup.ts'],

  // 模块文件扩展名
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json'],

  // 模块路径映射
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/../$1',
    '^@components/(.*)$': '<rootDir>/../components/$1',
    '^@pages/(.*)$': '<rootDir>/../pages/$1',
    '^@hooks/(.*)$': '<rootDir>/../hooks/$1',
    '^@utils/(.*)$': '<rootDir>/../utils/$1',
    '^@types/(.*)$': '<rootDir>/../types/$1',
    '^@assets/(.*)$': '<rootDir>/../assets/$1',
    '^@styles/(.*)$': '<rootDir>/../styles/$1',
  },

  // 转换配置
  transform: {
    '^.+\\.(ts|tsx)$': ['ts-jest', {
      tsconfig: '<rootDir>/../../tsconfig.json',
    }],
  },

  // 模块转换忽略
  transformIgnorePatterns: [
    'node_modules/(?!(.*\\.mjs$))',
  ],

  // 测试匹配模式
  testMatch: [
    '<rootDir>/**/*.test.(ts|tsx|js)',
    '<rootDir>/**/*.spec.(ts|tsx|js)',
  ],

  // 覆盖率收集
  collectCoverageFrom: [
    '../**/*.{ts,tsx}',
    '!../**/*.d.ts',
    '!../**/index.ts',
    '!../main.tsx',
    '!../vite.config.ts',
    '!../dist/**',
    '!../node_modules/**',
  ],

  // 覆盖率报告格式
  coverageReporters: [
    'text',
    'lcov',
    'html',
  ],

  // 覆盖率阈值
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70,
    },
  },

  // 模拟文件
  moduleNameMapping: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '\\.(jpg|jpeg|png|gif|webp|svg)$': '<rootDir>/__mocks__/fileMock.js',
  },

  // 清除模拟
  clearMocks: true,
  restoreMocks: true,

  // 测试超时
  testTimeout: 10000,

  // 详细输出
  verbose: true,
}