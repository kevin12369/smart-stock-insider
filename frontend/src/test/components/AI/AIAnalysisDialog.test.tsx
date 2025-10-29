/**
 * AIAnalysisDialog组件测试
 * 测试AI分析对话框的渲染、交互和流式分析功能
 */

import React from 'react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient } from '@tanstack/react-query'
import AIAnalysisDialog from '@/components/AI/AIAnalysisDialog'
import { render } from '../../utils'
import { mockAIAnalysisData } from '../../data'

// Mock API
vi.mock('@/services/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
  },
}))

const mockApi = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
}))

vi.mock('@/services/api', () => ({
  api: mockApi,
}))

// Mock formatDateTime
vi.mock('@/utils/format', () => ({
  formatDateTime: vi.fn((date) => date.toLocaleString()),
}))

// Mock fetch for streaming
global.fetch = vi.fn()

describe('AIAnalysisDialog组件', () => {
  let queryClient: QueryClient
  let user: ReturnType<typeof userEvent.setup>

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    })

    user = userEvent.setup()

    // Mock API responses
    mockApi.get.mockResolvedValue({
      data: {
        suggestions: [
          '分析这只股票的技术指标',
          '评估当前的投资机会',
          '预测未来走势',
        ],
      },
    })

    mockApi.post.mockResolvedValue({
      data: {
        answer: '根据技术分析，该股票目前处于上升趋势中。',
        role: 'technical_analyst',
        symbol: 'AAPL',
        question: '分析AAPL股票',
        confidence: 0.85,
        suggestions: ['建议持有', '关注技术指标变化'],
        reasoning: '基于MACD、RSI等技术指标的综合分析',
      },
    })

    // Mock fetch for streaming
    const mockFetch = vi.fn()
    global.fetch = mockFetch
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('应该正确渲染对话框', () => {
    render(<AIAnalysisDialog visible={true} onClose={vi.fn()} />)

    expect(screen.getByText('AI投资分析师')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('股票代码')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('请输入您的投资分析问题...')).toBeInTheDocument()
    expect(screen.getByText('技术分析师')).toBeInTheDocument()
  })

  it('应该正确处理默认参数', () => {
    render(
      <AIAnalysisDialog
        visible={true}
        onClose={vi.fn()}
        defaultSymbol="AAPL"
        defaultRole="fundamental_analyst"
      />
    )

    const symbolInput = screen.getByPlaceholderText('股票代码') as HTMLInputElement
    expect(symbolInput.value).toBe('AAPL')
    expect(screen.getByText('基本面分析师')).toBeInTheDocument()
  })

  it('应该正确处理股票代码输入', async () => {
    render(<AIAnalysisDialog visible={true} onClose={vi.fn()} />)

    const symbolInput = screen.getByPlaceholderText('股票代码')
    await user.type(symbolInput, 'AAPL')

    expect((symbolInput as HTMLInputElement).value).toBe('AAPL')
  })

  it('应该正确转换股票代码为大写', async () => {
    render(<AIAnalysisDialog visible={true} onClose={vi.fn()} />)

    const symbolInput = screen.getByPlaceholderText('股票代码')
    await user.type(symbolInput, 'aapl')

    expect((symbolInput as HTMLInputElement).value).toBe('AAPL')
  })

  it('应该正确处理角色切换', async () => {
    render(<AIAnalysisDialog visible={true} onClose={vi.fn()} />)

    const roleButton = screen.getByText('技术分析师')
    await user.click(roleButton)

    // 验证角色菜单是否出现
    await waitFor(() => {
      expect(screen.getByText('基本面分析师')).toBeInTheDocument()
      expect(screen.getByText('新闻分析师')).toBeInTheDocument()
      expect(screen.getByText('风控分析师')).toBeInTheDocument()
    })

    // 切换到基本面分析师
    await user.click(screen.getByText('基本面分析师'))
    expect(screen.getByText('基本面分析师')).toBeInTheDocument()
  })

  it('应该正确处理消息输入', async () => {
    render(<AIAnalysisDialog visible={true} onClose={vi.fn()} />)

    const symbolInput = screen.getByPlaceholderText('股票代码')
    const messageInput = screen.getByPlaceholderText('请输入您的投资分析问题...')

    await user.type(symbolInput, 'AAPL')
    await user.type(messageInput, '分析这只股票')

    expect((messageInput as HTMLTextAreaElement).value).toBe('分析这只股票')
  })

  it('应该正确发送消息并获得回复', async () => {
    render(<AIAnalysisDialog visible={true} onClose={vi.fn()} />)

    const symbolInput = screen.getByPlaceholderText('股票代码')
    const messageInput = screen.getByPlaceholderText('请输入您的投资分析问题...')
    const sendButton = screen.getByText('发送')

    await user.type(symbolInput, 'AAPL')
    await user.type(messageInput, '分析这只股票')
    await user.click(sendButton)

    // 验证用户消息是否显示
    await waitFor(() => {
      expect(screen.getByText('分析这只股票')).toBeInTheDocument()
    })

    // 验证API调用
    expect(mockApi.post).toHaveBeenCalledWith('/api/ai/analyze', {
      symbol: 'AAPL',
      question: '分析这只股票',
      role: 'technical_analyst',
      use_cache: true,
    })

    // 验证AI回复是否显示
    await waitFor(() => {
      expect(screen.getByText('根据技术分析，该股票目前处于上升趋势中。')).toBeInTheDocument()
      expect(screen.getByText('85%')).toBeInTheDocument() // 置信度
    })
  })

  it('应该正确处理流式响应开关', async () => {
    render(<AIAnalysisDialog visible={true} onClose={vi.fn()} />)

    const streamSwitch = screen.getByText('流式')
    expect(streamSwitch).toBeInTheDocument()

    // 关闭流式响应
    await user.click(streamSwitch)
    expect(screen.getByText('普通')).toBeInTheDocument()

    // 重新开启流式响应
    await user.click(streamSwitch)
    expect(screen.getByText('流式')).toBeInTheDocument()
  })

  it('应该正确处理建议显示开关', async () => {
    render(<AIAnalysisDialog visible={true} onClose={vi.fn()} />)

    const suggestionsSwitch = screen.getByText('建议')
    const symbolInput = screen.getByPlaceholderText('股票代码')

    await user.type(symbolInput, 'AAPL')

    // 等待建议加载
    await waitFor(() => {
      expect(screen.getByText('分析建议')).toBeInTheDocument()
      expect(screen.getByText('分析这只股票的技术指标')).toBeInTheDocument()
    })

    // 关闭建议显示
    await user.click(suggestionsSwitch)
    expect(screen.getByText('隐藏')).toBeInTheDocument()

    // 验证建议面板消失
    await waitFor(() => {
      expect(screen.queryByText('分析建议')).not.toBeInTheDocument()
    })
  })

  it('应该正确使用建议', async () => {
    render(<AIAnalysisDialog visible={true} onClose={vi.fn()} />)

    const symbolInput = screen.getByPlaceholderText('股票代码')
    const messageInput = screen.getByPlaceholderText('请输入您的投资分析问题...')

    await user.type(symbolInput, 'AAPL')

    // 等待建议加载
    await waitFor(() => {
      expect(screen.getByText('分析这只股票的技术指标')).toBeInTheDocument()
    })

    // 点击使用建议
    await user.click(screen.getByText('分析这只股票的技术指标'))

    // 验证建议是否填入输入框
    expect((messageInput as HTMLTextAreaElement).value).toBe('分析这只股票的技术指标')
  })

  it('应该正确处理清空对话', async () => {
    render(<AIAnalysisDialog visible={true} onClose={vi.fn()} />)

    const symbolInput = screen.getByPlaceholderText('股票代码')
    const messageInput = screen.getByPlaceholderText('请输入您的投资分析问题...')
    const sendButton = screen.getByText('发送')

    // 发送一条消息
    await user.type(symbolInput, 'AAPL')
    await user.type(messageInput, '测试消息')
    await user.click(sendButton)

    // 等待消息显示
    await waitFor(() => {
      expect(screen.getByText('测试消息')).toBeInTheDocument()
    })

    // 清空对话
    const clearButton = screen.getByTitle('清空对话')
    await user.click(clearButton)

    // 验证消息是否被清空
    await waitFor(() => {
      expect(screen.queryByText('测试消息')).not.toBeInTheDocument()
    })
  })

  it('应该正确处理导出对话', async () => {
    // Mock URL.createObjectURL and download
    const mockCreateObjectURL = vi.fn(() => 'mock-url')
    const mockRevokeObjectURL = vi.fn()
    global.URL.createObjectURL = mockCreateObjectURL
    global.URL.revokeObjectURL = mockRevokeObjectURL

    // Mock link creation and click
    const mockLink = {
      href: '',
      download: '',
      click: vi.fn(),
    }
    const mockCreateElement = vi.fn(() => mockLink)
    global.document.createElement = mockCreateElement

    render(<AIAnalysisDialog visible={true} onClose={vi.fn()} />)

    const symbolInput = screen.getByPlaceholderText('股票代码')
    const messageInput = screen.getByPlaceholderText('请输入您的投资分析问题...')
    const sendButton = screen.getByText('发送')

    // 发送一条消息
    await user.type(symbolInput, 'AAPL')
    await user.type(messageInput, '测试消息')
    await user.click(sendButton)

    // 等待消息显示
    await waitFor(() => {
      expect(screen.getByText('测试消息')).toBeInTheDocument()
    })

    // 导出对话
    const exportButton = screen.getByTitle('导出对话')
    await user.click(exportButton)

    // 验证导出功能是否被调用
    expect(mockCreateElement).toHaveBeenCalledWith('a')
    expect(mockLink.click).toHaveBeenCalled()
  })

  it('应该正确处理键盘快捷键', async () => {
    render(<AIAnalysisDialog visible={true} onClose={vi.fn()} />)

    const symbolInput = screen.getByPlaceholderText('股票代码')
    const messageInput = screen.getByPlaceholderText('请输入您的投资分析问题...')

    await user.type(symbolInput, 'AAPL')
    await user.type(messageInput, '测试消息')

    // 使用Enter键发送消息
    await user.keyboard('{Enter}')

    // 验证消息是否发送
    await waitFor(() => {
      expect(screen.getByText('测试消息')).toBeInTheDocument()
    })
  })

  it('应该正确处理Shift+Enter换行', async () => {
    render(<AIAnalysisDialog visible={true} onClose={vi.fn()} />)

    const symbolInput = screen.getByPlaceholderText('股票代码')
    const messageInput = screen.getByPlaceholderText('请输入您的投资分析问题...')

    await user.type(symbolInput, 'AAPL')
    await user.type(messageInput, '第一行')
    await user.keyboard('{Shift>}{Enter}{/Shift}')
    await user.type(messageInput, '第二行')

    // 验证输入框内容包含换行
    expect((messageInput as HTMLTextAreaElement).value).toBe('第一行\n第二行')
  })

  it('应该正确处理空输入验证', async () => {
    const mockMessage = vi.fn()
    render(<AIAnalysisDialog visible={true} onClose={vi.fn()} />)

    // Mock antd message
    vi.mock('antd', async () => {
      const actual = await vi.importActual('antd')
      return {
        ...actual,
        message: {
          error: mockMessage,
          warning: mockMessage,
        },
      }
    })

    const sendButton = screen.getByText('发送')

    // 尝试发送空消息
    await user.click(sendButton)

    // 验证警告消息
    expect(mockMessage).toHaveBeenCalledWith('请输入股票代码和分析问题')
  })

  it('应该正确处理错误状态', async () => {
    const mockMessage = vi.fn()

    // Mock antd message
    vi.doMock('antd', async () => {
      const actual = await vi.importActual('antd')
      return {
        ...actual,
        message: {
          error: mockMessage,
        },
      }
    })

    // Mock API错误
    mockApi.post.mockRejectedValue({
      response: { data: { message: 'API错误' } },
    })

    render(<AIAnalysisDialog visible={true} onClose={vi.fn()} />)

    const symbolInput = screen.getByPlaceholderText('股票代码')
    const messageInput = screen.getByPlaceholderText('请输入您的投资分析问题...')
    const sendButton = screen.getByText('发送')

    await user.type(symbolInput, 'AAPL')
    await user.type(messageInput, '测试消息')
    await user.click(sendButton)

    // 验证错误处理
    await waitFor(() => {
      expect(mockMessage).toHaveBeenCalledWith('分析失败: API错误')
    })
  })

  it('应该正确处理关闭对话框', async () => {
    const mockOnClose = vi.fn()
    render(<AIAnalysisDialog visible={true} onClose={mockOnClose} />)

    // 查找关闭按钮并点击
    const closeButton = screen.getByRole('button', { name: /close/i })
    await user.click(closeButton)

    // 验证关闭回调被调用
    expect(mockOnClose).toHaveBeenCalled()
  })

  it('应该正确显示置信度标签', async () => {
    render(<AIAnalysisDialog visible={true} onClose={vi.fn()} />)

    const symbolInput = screen.getByPlaceholderText('股票代码')
    const messageInput = screen.getByPlaceholderText('请输入您的投资分析问题...')
    const sendButton = screen.getByText('发送')

    await user.type(symbolInput, 'AAPL')
    await user.type(messageInput, '测试消息')
    await user.click(sendButton)

    // 验证置信度标签显示
    await waitFor(() => {
      expect(screen.getByText('85%')).toBeInTheDocument()
      expect(screen.getByTitle('置信度')).toBeInTheDocument()
    })
  })

  it('应该正确显示建议列表', async () => {
    render(<AIAnalysisDialog visible={true} onClose={vi.fn()} />)

    const symbolInput = screen.getByPlaceholderText('股票代码')
    await user.type(symbolInput, 'AAPL')

    // 等待建议加载
    await waitFor(() => {
      expect(screen.getByText('分析建议')).toBeInTheDocument()
      expect(screen.getByText('分析这只股票的技术指标')).toBeInTheDocument()
      expect(screen.getByText('评估当前的投资机会')).toBeInTheDocument()
      expect(screen.getByText('预测未来走势')).toBeInTheDocument()
    })
  })

  it('应该正确处理股票代码输入限制', async () => {
    render(<AIAnalysisDialog visible={true} onClose={vi.fn()} />)

    const symbolInput = screen.getByPlaceholderText('股票代码')

    // 尝试输入超过6个字符
    await user.type(symbolInput, '1234567')

    // 验证只保留前6个字符
    expect((symbolInput as HTMLInputElement).value).toBe('123456')
  })
})