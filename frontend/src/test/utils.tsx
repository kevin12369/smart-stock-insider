/**
 * 前端测试工具函数
 * 提供常用的测试辅助函数和组件渲染器
 */

import React, { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import { vi } from 'vitest'

// 创建测试用QueryClient
export const createTestQueryClient = () => {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  })
}

// 测试渲染器包装组件
interface AllTheProvidersProps {
  children: React.ReactNode
  queryClient?: QueryClient
}

const AllTheProviders: React.FC<AllTheProvidersProps> = ({
  children,
  queryClient = createTestQueryClient()
}) => {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <ConfigProvider locale={zhCN}>
          {children}
        </ConfigProvider>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

// 自定义渲染函数
const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'> & {
    queryClient?: QueryClient
  }
) => {
  const { queryClient, ...renderOptions } = options || {}
  const Wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <AllTheProviders queryClient={queryClient}>
      {children}
    </AllTheProviders>
  )

  return render(ui, { wrapper: Wrapper, ...renderOptions })
}

// 重新导出所有testing-library的函数
export * from '@testing-library/react'
export { customRender as render }

// Mock intersection observer for lazy loading tests
export const setupIntersectionObserverMock = () => {
  const mockIntersectionObserver = vi.fn()
  mockIntersectionObserver.mockReturnValue({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
  })
  window.IntersectionObserver = mockIntersectionObserver
}

// Mock resize observer for responsive tests
export const setupResizeObserverMock = () => {
  const mockResizeObserver = vi.fn()
  mockResizeObserver.mockReturnValue({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
  })
  window.ResizeObserver = mockResizeObserver
}

// 等待异步操作完成的工具函数
export const waitForAsync = () => new Promise(resolve => setTimeout(resolve, 0))

// 模拟用户输入事件
export const mockUserInput = (element: HTMLElement, value: string) => {
  element.setAttribute('value', value)
  element.dispatchEvent(new Event('input', { bubbles: true }))
}

// 模拟表单提交
export const mockFormSubmit = (form: HTMLElement) => {
  form.dispatchEvent(new Event('submit', { bubbles: true }))
}

// 模拟鼠标事件
export const mockMouseEvent = (
  element: HTMLElement,
  eventType: 'click' | 'hover' | 'mouseenter' | 'mouseleave'
) => {
  const event = new MouseEvent(eventType, { bubbles: true })
  element.dispatchEvent(event)
}

// 模拟键盘事件
export const mockKeyboardEvent = (
  element: HTMLElement,
  key: string,
  eventType: 'keydown' | 'keyup' | 'keypress' = 'keydown'
) => {
  const event = new KeyboardEvent(eventType, {
    key,
    bubbles: true,
  })
  element.dispatchEvent(event)
}

// 模拟滚动事件
export const mockScrollEvent = (element: HTMLElement = window) => {
  element.dispatchEvent(new Event('scroll', { bubbles: true }))
}

// 模拟窗口大小变化
export const mockResizeEvent = () => {
  window.dispatchEvent(new Event('resize'))
}

// 测试数据验证器
export const validateStockData = (stock: any) => {
  expect(stock).toHaveProperty('id')
  expect(stock).toHaveProperty('symbol')
  expect(stock).toHaveProperty('name')
  expect(stock).toHaveProperty('price')
  expect(stock).toHaveProperty('change')
  expect(stock).toHaveProperty('changePercent')
  expect(typeof stock.price).toBe('number')
  expect(typeof stock.change).toBe('number')
  expect(typeof stock.changePercent).toBe('number')
}

export const validateNewsData = (news: any) => {
  expect(news).toHaveProperty('id')
  expect(news).toHaveProperty('title')
  expect(news).toHaveProperty('summary')
  expect(news).toHaveProperty('source')
  expect(news).toHaveProperty('publishedAt')
  expect(news).toHaveProperty('category')
  expect(typeof news.title).toBe('string')
  expect(typeof news.summary).toBe('string')
  expect(typeof news.category).toBe('string')
}

export const validateAIAnalysisData = (analysis: any) => {
  expect(analysis).toHaveProperty('analysis_id')
  expect(analysis).toHaveProperty('symbol')
  expect(analysis).toHaveProperty('technical_analysis')
  expect(analysis).toHaveProperty('fundamental_analysis')
  expect(analysis).toHaveProperty('sentiment_analysis')
  expect(analysis).toHaveProperty('recommendation')

  expect(analysis.technical_analysis).toHaveProperty('trend')
  expect(analysis.technical_analysis).toHaveProperty('strength')
  expect(analysis.recommendation).toHaveProperty('action')
  expect(analysis.recommendation).toHaveProperty('confidence')
}

// Mock localStorage操作
export const mockLocalStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
  length: 0,
  key: vi.fn(),
}

// 模拟网络延迟
export const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

// 生成随机测试ID
export const generateTestId = (prefix: string = 'test') => {
  return `${prefix}_${Math.random().toString(36).substr(2, 9)}`
}

// 测试断言辅助函数
export const expectElementToBeVisible = (element: HTMLElement) => {
  expect(element).toBeInTheDocument()
  expect(element).toBeVisible()
}

export const expectElementToHaveText = (element: HTMLElement, text: string) => {
  expect(element).toBeInTheDocument()
  expect(element).toHaveTextContent(text)
}

export const expectButtonToBeDisabled = (button: HTMLElement) => {
  expect(button).toBeInTheDocument()
  expect(button).toBeDisabled()
}

export const expectButtonToBeEnabled = (button: HTMLElement) => {
  expect(button).toBeInTheDocument()
  expect(button).not.toBeDisabled()
}

// 模拟Promise reject
export const mockPromiseReject = (error: Error) => {
  return Promise.reject(error)
}

// 模拟Promise resolve
export function mockPromiseResolve<T>(data: T): Promise<T> {
  return Promise.resolve(data)
}

// 检查组件是否正确渲染
export const expectComponentToRender = (component: ReactElement) => {
  const { getByTestId } = render(component)
  expect(getByTestId('component-root')).toBeInTheDocument()
}

// 测试错误边界
export class TestErrorBoundary extends React.Component<
  { children: React.ReactNode; onError?: (error: Error) => void },
  { hasError: boolean; error?: Error }
> {
  constructor(props: any) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    if (this.props.onError) {
      this.props.onError(error)
    }
    console.error('Test error boundary caught an error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div data-testid="error-boundary-fallback">
          Test error boundary fallback
        </div>
      )
    }

    return this.props.children
  }
}

// 测试Hook的辅助函数
export function renderHook<T>(hook: () => T) {
  let result: T
  let error: Error | undefined

  const TestComponent = () => {
    try {
      result = hook()
      return <div data-testid="hook-test">Hook test</div>
    } catch (e) {
      error = e as Error
      return <div data-testid="hook-error">Hook error</div>
    }
  }

  render(<TestComponent />)

  return {
    result: result!,
    error,
  }
}

// 清理函数
export const cleanupTest = () => {
  vi.clearAllMocks()
  localStorage.clear()
  sessionStorage.clear()
}

// 导出默认配置
export const defaultTestConfig = {
  queryClient: createTestQueryClient(),
  setupMocks: () => {
    setupIntersectionObserverMock()
    setupResizeObserverMock()
    vi.stubGlobal('localStorage', mockLocalStorage)
  }
}