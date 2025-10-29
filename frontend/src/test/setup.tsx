/**
 * 前端测试设置文件
 * 配置测试环境、全局设置和模拟对象
 */

import '@testing-library/jest-dom'
import { beforeAll, afterEach, afterAll } from 'vitest'
import { cleanup } from '@testing-library/react'
import { ReactNode } from 'react'
import { server } from './mocks/server'

// 在每个测试前清理DOM
afterEach(() => {
  cleanup()
})

// 启动mock服务器
beforeAll(() => {
  server.listen({ onUnhandledRequest: 'error' })
})

// 每个测试后重置handlers
afterEach(() => {
  server.resetHandlers()
})

// 测试完成后关闭服务器
afterAll(() => {
  server.close()
})

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Mock Tauri APIs
vi.mock('@tauri-apps/api', () => ({
  invoke: vi.fn(),
  dialog: {
    open: vi.fn(),
    save: vi.fn(),
    confirm: vi.fn(),
  },
  window: {
    getCurrent: vi.fn().mockReturnValue({
      label: 'main',
      title: 'Smart Stock Insider',
    }),
  },
}))

// Mock Tauri Shell API
vi.mock('@tauri-apps/plugin-shell', () => ({
  open: vi.fn(),
}))

// Mock Socket.IO
vi.mock('socket.io-client', () => ({
  io: vi.fn().mockReturnValue({
    on: vi.fn(),
    off: vi.fn(),
    emit: vi.fn(),
    disconnect: vi.fn(),
    connect: vi.fn(),
  }),
}))

// Mock ECharts
vi.mock('echarts', () => ({
  init: vi.fn().mockReturnValue({
    setOption: vi.fn(),
    resize: vi.fn(),
    dispose: vi.fn(),
    on: vi.fn(),
    off: vi.fn(),
  }),
  registerTheme: vi.fn(),
}))

// Mock recharts
vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: { children: ReactNode }) => (
    <div data-testid="responsive-container">{children}</div>
  ),
  LineChart: ({ children }: { children: ReactNode }) => (
    <div data-testid="line-chart">{children}</div>
  ),
  Line: vi.fn(),
  XAxis: vi.fn(),
  YAxis: vi.fn(),
  CartesianGrid: vi.fn(),
  Tooltip: vi.fn(),
  Legend: vi.fn(),
  BarChart: ({ children }: { children: ReactNode }) => (
    <div data-testid="bar-chart">{children}</div>
  ),
  Bar: vi.fn(),
  PieChart: ({ children }: { children: ReactNode }) => (
    <div data-testid="pie-chart">{children}</div>
  ),
  Pie: vi.fn(),
  Cell: vi.fn(),
  AreaChart: ({ children }: { children: ReactNode }) => (
    <div data-testid="area-chart">{children}</div>
  ),
  Area: vi.fn(),
}))

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
vi.stubGlobal('localStorage', localStorageMock)

// Mock sessionStorage
const sessionStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
vi.stubGlobal('sessionStorage', sessionStorageMock)

// Mock console methods in tests
global.console = {
  ...console,
  warn: vi.fn(),
  error: vi.fn(),
}

// Add custom matchers
expect.extend({
  toBeInTheDocument: (received) => {
    const pass = received && document.body.contains(received)
    return {
      message: () =>
        pass
          ? `expected element not to be in the document`
          : `expected element to be in the document`,
      pass,
    }
  },
})

// Mock environment variables
process.env.NODE_ENV = 'test'