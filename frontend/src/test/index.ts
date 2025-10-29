/**
 * 前端测试入口文件
 * 导出所有测试相关的配置和工具
 */

// 导出测试工具
export * from './utils'
export * from './data'

// 导出Mock配置
export { server } from './mocks/server'

// 导出测试常量
export const TEST_CONSTANTS = {
  TIMEOUT: 10000,
  RETRY_COUNT: 3,
  MOCK_DELAY: 100,
}

// 导出测试辅助函数
export const createMockProps = <T extends Record<string, any>>(defaults: T) => {
  return (overrides: Partial<T> = {}): T => ({
    ...defaults,
    ...overrides,
  })
}

export const waitForElement = async (element: () => HTMLElement | null, timeout = TEST_CONSTANTS.TIMEOUT) => {
  return new Promise((resolve, reject) => {
    const startTime = Date.now()

    const check = () => {
      const el = element()
      if (el) {
        resolve(el)
      } else if (Date.now() - startTime > timeout) {
        reject(new Error('Element not found within timeout'))
      } else {
        setTimeout(check, 100)
      }
    }

    check()
  })
}

export const createMockEvent = (type: string, properties: Record<string, any> = {}) => {
  return {
    type,
    preventDefault: vi.fn(),
    stopPropagation: vi.fn(),
    target: {
      value: '',
      checked: false,
      ...properties.target,
    },
    ...properties,
  }
}

// 全局测试设置
beforeEach(() => {
  // 清除所有mock调用
  vi.clearAllMocks()

  // 重置localStorage
  localStorage.clear()
  sessionStorage.clear()
})

afterEach(() => {
  // 清理定时器
  vi.clearAllTimers()

  // 清理DOM
  document.body.innerHTML = ''
})

// 设置全局测试环境
Object.defineProperty(window, 'scrollTo', {
  value: vi.fn(),
  writable: true,
})

// Mock console方法以减少测试噪音
global.console = {
  ...console,
  warn: vi.fn(),
  error: vi.fn(),
}