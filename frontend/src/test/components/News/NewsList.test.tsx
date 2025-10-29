/**
 * NewsList组件测试
 * 测试新闻列表组件的渲染、筛选、排序和交互功能
 */

import React from 'react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient } from '@tanstack/react-query'
import NewsList from '@/components/News/NewsList'
import { render } from '../../utils'
import { mockNewsData } from '../../data'
import dayjs from 'dayjs'

// Mock API
vi.mock('@/services/api', () => ({
  api: {
    get: vi.fn(),
  },
}))

const mockApi = vi.hoisted(() => ({
  get: vi.fn(),
}))

vi.mock('@/services/api', () => ({
  api: mockApi,
}))

// Mock format utils
vi.mock('@/utils/format', () => ({
  formatDateTime: vi.fn((date) => new Date(date).toLocaleString()),
  formatRelativeTime: vi.fn((date) => '2小时前'),
}))

describe('NewsList组件', () => {
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
    mockApi.get.mockImplementation((url: string) => {
      if (url.includes('/api/news/list')) {
        return Promise.resolve({
          data: {
            data: mockNewsData.slice(0, 5),
            total: 25,
            page: 1,
            limit: 5,
          },
        })
      }
      if (url.includes('/api/news/categories')) {
        return Promise.resolve({
          data: {
            categories: [
              { value: 'technology', label: '科技' },
              { value: 'finance', label: '财经' },
              { value: 'healthcare', label: '医疗' },
            ],
          },
        })
      }
      if (url.includes('/api/news/sources')) {
        return Promise.resolve({
          data: [
            { name: '财经日报' },
            { name: '汽车周刊' },
            { name: '经济观察报' },
          ],
        })
      }
      return Promise.resolve({ data: [] })
    })
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('应该正确渲染新闻列表', async () => {
    render(<NewsList />)

    await waitFor(() => {
      expect(screen.getByText('新闻资讯')).toBeInTheDocument()
    })

    // 检查新闻条目是否渲染
    mockNewsData.slice(0, 5).forEach(news => {
      expect(screen.getByText(news.title)).toBeInTheDocument()
      expect(screen.getByText(news.source)).toBeInTheDocument()
    })
  })

  it('应该正确处理股票代码参数', async () => {
    render(<NewsList stockCode="AAPL" />)

    await waitFor(() => {
      expect(screen.getByText('AAPL 相关')).toBeInTheDocument()
    })

    // 验证API调用参数包含股票代码
    expect(mockApi.get).toHaveBeenCalledWith(
      expect.stringContaining('stock_code=AAPL')
    )
  })

  it('应该正确处理搜索功能', async () => {
    render(<NewsList />)

    await waitFor(() => {
      expect(screen.getByText('新闻资讯')).toBeInTheDocument()
    })

    const searchInput = screen.getByPlaceholderText('搜索新闻...')
    await user.type(searchInput, '苹果')

    // 触发搜索
    await user.keyboard('{Enter}')

    // 验证搜索API被调用
    await waitFor(() => {
      expect(mockApi.get).toHaveBeenCalledWith(
        expect.stringContaining('keyword=苹果')
      )
    })
  })

  it('应该正确处理分类筛选', async () => {
    render(<NewsList />)

    await waitFor(() => {
      expect(screen.getByText('新闻资讯')).toBeInTheDocument()
    })

    // 点击筛选按钮
    const filterButton = screen.getByText('筛选')
    await user.click(filterButton)

    // 等待菜单出现并选择科技分类
    await waitFor(() => {
      const techCategory = screen.getByText('科技')
      expect(techCategory).toBeInTheDocument()
    })

    await user.click(screen.getByText('科技'))

    // 验证筛选标签显示
    await waitFor(() => {
      expect(screen.getByText('分类: technology')).toBeInTheDocument()
    })

    // 验证API调用参数
    expect(mockApi.get).toHaveBeenCalledWith(
      expect.stringContaining('category=technology')
    )
  })

  it('应该正确处理来源筛选', async () => {
    render(<NewsList />)

    await waitFor(() => {
      expect(screen.getByText('新闻资讯')).toBeInTheDocument()
    })

    // 点击筛选按钮
    const filterButton = screen.getByText('筛选')
    await user.click(filterButton)

    // 选择来源
    await waitFor(() => {
      expect(screen.getByText('财经日报')).toBeInTheDocument()
    })

    await user.click(screen.getByText('财经日报'))

    // 验证筛选标签显示
    await waitFor(() => {
      expect(screen.getByText('来源: 财经日报')).toBeInTheDocument()
    })

    // 验证API调用参数
    expect(mockApi.get).toHaveBeenCalledWith(
      expect.stringContaining('source=财经日报')
    )
  })

  it('应该正确处理情感筛选', async () => {
    render(<NewsList />)

    await waitFor(() => {
      expect(screen.getByText('新闻资讯')).toBeInTheDocument()
    })

    // 点击筛选按钮
    const filterButton = screen.getByText('筛选')
    await user.click(filterButton)

    // 选择情感
    await waitFor(() => {
      expect(screen.getByText('利好')).toBeInTheDocument()
    })

    await user.click(screen.getByText('利好'))

    // 验证筛选标签显示
    await waitFor(() => {
      expect(screen.getByText('情感: positive')).toBeInTheDocument()
    })

    // 验证API调用参数
    expect(mockApi.get).toHaveBeenCalledWith(
      expect.stringContaining('sentiment=positive')
    )
  })

  it('应该正确处理日期范围筛选', async () => {
    render(<NewsList />)

    await waitFor(() => {
      expect(screen.getByText('新闻资讯')).toBeInTheDocument()
    })

    // 获取日期选择器
    const dateRangePicker = screen.getByPlaceholderText('开始日期')
    expect(dateRangePicker).toBeInTheDocument()

    // 设置日期范围
    const startDate = dayjs().subtract(7, 'day')
    const endDate = dayjs()

    // 这里需要模拟日期选择器的交互
    fireEvent.change(dateRangePicker, {
      target: { value: [startDate, endDate] },
    })

    // 验证日期筛选标签显示
    await waitFor(() => {
      expect(screen.getByText(/日期:/)).toBeInTheDocument()
    })
  })

  it('应该正确处理排序功能', async () => {
    render(<NewsList />)

    await waitFor(() => {
      expect(screen.getByText('新闻资讯')).toBeInTheDocument()
    })

    // 获取排序选择器
    const sortSelect = screen.getByDisplayValue('最新发布')
    expect(sortSelect).toBeInTheDocument()

    // 更改排序方式为相关度
    await user.selectOptions(sortSelect, 'relevance_score_desc')

    // 验证API调用参数
    await waitFor(() => {
      expect(mockApi.get).toHaveBeenCalledWith(
        expect.stringContaining('sort_by=relevance_score')
      )
      expect(mockApi.get).toHaveBeenCalledWith(
        expect.stringContaining('sort_order=desc')
      )
    })
  })

  it('应该正确处理清空筛选', async () => {
    render(<NewsList />)

    await waitFor(() => {
      expect(screen.getByText('新闻资讯')).toBeInTheDocument()
    })

    // 先设置一些筛选条件
    const filterButton = screen.getByText('筛选')
    await user.click(filterButton)

    await waitFor(() => {
      expect(screen.getByText('科技')).toBeInTheDocument()
    })

    await user.click(screen.getByText('科技'))

    // 等待筛选标签出现
    await waitFor(() => {
      expect(screen.getByText('分类: technology')).toBeInTheDocument()
    })

    // 点击清空筛选按钮
    const clearButton = screen.getByText('清空筛选')
    await user.click(clearButton)

    // 验证筛选标签消失
    await waitFor(() => {
      expect(screen.queryByText('分类: technology')).not.toBeInTheDocument()
    })
  })

  it('应该正确处理分页功能', async () => {
    // Mock更多数据用于分页测试
    mockApi.get.mockImplementation((url: string) => {
      if (url.includes('/api/news/list')) {
        const page = new URLSearchParams(url.split('?')[1]).get('page') || '1'
        const pageNum = parseInt(page)

        return Promise.resolve({
          data: {
            data: mockNewsData.slice((pageNum - 1) * 5, pageNum * 5),
            total: 25,
            page: pageNum,
            limit: 5,
          },
        })
      }
      return Promise.resolve({ data: [] })
    })

    render(<NewsList limit={5} />)

    await waitFor(() => {
      expect(screen.getByText('新闻资讯')).toBeInTheDocument()
    })

    // 检查分页组件
    await waitFor(() => {
      expect(screen.getByText('第 1-5 条，共 25 条')).toBeInTheDocument()
    })

    // 点击下一页
    const nextPageButton = screen.getByTitle('下一页')
    await user.click(nextPageButton)

    // 验证API调用参数更新
    await waitFor(() => {
      expect(mockApi.get).toHaveBeenCalledWith(
        expect.stringContaining('offset=5')
      )
    })
  })

  it('应该正确处理新闻点击事件', async () => {
    const onNewsClickMock = vi.fn()
    render(<NewsList onNewsClick={onNewsClickMock} />)

    await waitFor(() => {
      expect(screen.getByText('新闻资讯')).toBeInTheDocument()
    })

    // 点击第一条新闻
    const firstNews = screen.getByText(mockNewsData[0].title)
    await user.click(firstNews)

    // 验证回调函数被调用
    expect(onNewsClickMock).toHaveBeenCalledWith(
      expect.objectContaining({
        id: mockNewsData[0].id,
        title: mockNewsData[0].title,
      })
    )
  })

  it('应该正确渲染情感标签', async () => {
    render(<NewsList />)

    await waitFor(() => {
      expect(screen.getByText('新闻资讯')).toBeInTheDocument()
    })

    // 检查情感标签渲染
    mockNewsData.slice(0, 5).forEach(news => {
      const sentimentTag = screen.getByText(
        news.sentiment === 'positive' ? '利好' :
        news.sentiment === 'negative' ? '利空' : '中性'
      )
      expect(sentimentTag).toBeInTheDocument()
    })
  })

  it('应该正确渲染关键词标签', async () => {
    render(<NewsList />)

    await waitFor(() => {
      expect(screen.getByText('新闻资讯')).toBeInTheDocument()
    })

    // 检查关键词标签渲染
    mockNewsData.slice(0, 5).forEach(news => {
      if (news.tags && news.tags.length > 0) {
        news.tags.slice(0, 5).forEach(tag => {
          expect(screen.getByText(tag)).toBeInTheDocument()
        })
      }
    })
  })

  it('应该正确渲染相关股票信息', async () => {
    // 创建包含相关股票的新闻数据
    const newsWithStocks = {
      ...mockNewsData[0],
      mentioned_stocks: ['AAPL', 'GOOGL', 'MSFT'],
    }

    mockApi.get.mockImplementation((url: string) => {
      if (url.includes('/api/news/list')) {
        return Promise.resolve({
          data: {
            data: [newsWithStocks],
            total: 1,
          },
        })
      }
      return Promise.resolve({ data: [] })
    })

    render(<NewsList />)

    await waitFor(() => {
      expect(screen.getByText('相关股票')).toBeInTheDocument()
      expect(screen.getByText('AAPL')).toBeInTheDocument()
      expect(screen.getByText('GOOGL')).toBeInTheDocument()
      expect(screen.getByText('MSFT')).toBeInTheDocument()
    })
  })

  it('应该正确处理刷新功能', async () => {
    render(<NewsList />)

    await waitFor(() => {
      expect(screen.getByText('新闻资讯')).toBeInTheDocument()
    })

    // 清除之前的mock调用
    vi.clearAllMocks()

    // 点击刷新按钮
    const refreshButton = screen.getByText('刷新')
    await user.click(refreshButton)

    // 验证刷新API被调用
    await waitFor(() => {
      expect(mockApi.get).toHaveBeenCalled()
    })
  })

  it('应该正确处理空状态', async () => {
    // Mock空数据响应
    mockApi.get.mockResolvedValue({
      data: {
        data: [],
        total: 0,
      },
    })

    render(<NewsList />)

    await waitFor(() => {
      expect(screen.getByText('暂无相关新闻')).toBeInTheDocument()
    })
  })

  it('应该正确处理错误状态', async () => {
    // Mock API错误
    mockApi.get.mockRejectedValue(new Error('Network error'))

    render(<NewsList />)

    await waitFor(() => {
      expect(screen.getByText('加载失败，请重试')).toBeInTheDocument()
    })
  })

  it('应该正确处理加载状态', async () => {
    // Mock延迟响应
    mockApi.get.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 1000)))

    render(<NewsList />)

    // 检查加载状态
    expect(screen.getByRole('generic', { hidden: true })).toBeInTheDocument()
  })

  it('应该正确处理隐藏头部', () => {
    render(<NewsList showHeader={false} />)

    // 验证头部不显示
    expect(screen.queryByText('新闻资讯')).not.toBeInTheDocument()
  })

  it('应该正确处理隐藏筛选器', () => {
    render(<NewsList showFilters={false} />)

    // 验证筛选器不显示
    expect(screen.queryByPlaceholderText('搜索新闻...')).not.toBeInTheDocument()
    expect(screen.queryByText('筛选')).not.toBeInTheDocument()
  })

  it('应该正确处理高相关性标签', async () => {
    // Mock高相关性新闻数据
    const highRelevanceNews = {
      ...mockNewsData[0],
      relevance_score: 0.9,
    }

    mockApi.get.mockImplementation((url: string) => {
      if (url.includes('/api/news/list')) {
        return Promise.resolve({
          data: {
            data: [highRelevanceNews],
            total: 1,
          },
        })
      }
      return Promise.resolve({ data: [] })
    })

    render(<NewsList />)

    await waitFor(() => {
      expect(screen.getByText('高相关')).toBeInTheDocument()
    })
  })

  it('应该正确处理关键词数量显示', async () => {
    // Mock包含大量关键词的新闻
    const newsWithManyKeywords = {
      ...mockNewsData[0],
      keywords: ['keyword1', 'keyword2', 'keyword3', 'keyword4', 'keyword5', 'keyword6', 'keyword7'],
    }

    mockApi.get.mockImplementation((url: string) => {
      if (url.includes('/api/news/list')) {
        return Promise.resolve({
          data: {
            data: [newsWithManyKeywords],
            total: 1,
          },
        })
      }
      return Promise.resolve({ data: [] })
    })

    render(<NewsList />)

    await waitFor(() => {
      expect(screen.getByText('+2')).toBeInTheDocument() // 7个关键词 - 5个显示 = +2
    })
  })
})