/**
 * StockList组件测试
 * 测试股票列表组件的渲染、交互和数据管理功能
 */

import React from 'react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient } from '@tanstack/react-query'
import StockList from '@/components/Stock/StockList'
import { render } from '../../utils'
import { mockStockData } from '../../data'
import * as apiClient from '@/services/api'

// Mock API客户端
vi.mock('@/services/api')
const mockApiClient = vi.mocked(apiClient)

// Mock store
vi.mock('@/stores/watchlistStore', () => ({
  useWatchlistStore: () => ({
    watchlist: [],
    addToWatchlist: vi.fn(),
    removeFromWatchlist: vi.fn(),
  }),
}))

// Mock debounce
vi.mock('lodash-es', () => ({
  debounce: (fn: Function) => fn,
}))

describe('StockList组件', () => {
  let queryClient: QueryClient

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    })

    // Mock API响应
    mockApiClient.apiClient.get.mockImplementation((url: string) => {
      if (url.includes('/api/stocks/list')) {
        return Promise.resolve({
          data: {
            data: mockStockData.slice(0, 5),
            pagination: {
              page: 1,
              size: 5,
              total: 5,
              pages: 1,
            },
          },
        })
      }
      if (url.includes('/api/stocks/sectors')) {
        return Promise.resolve({
          data: [
            { code: 'TECH', name: '科技' },
            { code: 'FIN', name: '金融' },
            { code: 'HEALTH', name: '医疗' },
          ],
        })
      }
      return Promise.resolve({ data: [] })
    })

    mockApiClient.apiClient.post.mockImplementation((url: string) => {
      if (url.includes('/api/stocks/realtime')) {
        return Promise.resolve({
          data: mockStockData.slice(0, 5).map(stock => ({
            symbol: stock.symbol,
            price: stock.price + Math.random() * 2 - 1,
            timestamp: new Date().toISOString(),
          })),
        })
      }
      return Promise.resolve({ data: [] })
    })
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('应该正确渲染股票列表', async () => {
    render(<StockList />)

    // 等待数据加载
    await waitFor(() => {
      expect(screen.getByText('股票列表')).toBeInTheDocument()
    })

    // 检查表格是否渲染
    expect(screen.getByText('代码')).toBeInTheDocument()
    expect(screen.getByText('名称')).toBeInTheDocument()
    expect(screen.getByText('当前价')).toBeInTheDocument()

    // 检查股票数据是否显示
    mockStockData.slice(0, 5).forEach(stock => {
      expect(screen.getByText(stock.symbol)).toBeInTheDocument()
      expect(screen.getByText(stock.name)).toBeInTheDocument()
    })
  })

  it('应该处理搜索功能', async () => {
    render(<StockList />)

    // 等待初始数据加载
    await waitFor(() => {
      expect(screen.getByText('股票列表')).toBeInTheDocument()
    })

    // 获取搜索框
    const searchInput = screen.getByPlaceholderText('搜索股票代码或名称')
    expect(searchInput).toBeInTheDocument()

    // 输入搜索关键词
    const searchKeyword = 'AAPL'
    fireEvent.change(searchInput, { target: { value: searchKeyword } })

    // Mock搜索API响应
    mockApiClient.apiClient.get.mockResolvedValue({
      data: [mockStockData[0]],
    })

    // 触发搜索
    fireEvent.click(screen.getByTitle('搜索'))

    await waitFor(() => {
      // 验证搜索API被调用
      expect(mockApiClient.apiClient.get).toHaveBeenCalledWith(
        expect.stringContaining('/api/stocks/search')
      )
    })
  })

  it('应该处理市场筛选', async () => {
    render(<StockList />)

    await waitFor(() => {
      expect(screen.getByText('股票列表')).toBeInTheDocument()
    })

    // 获取市场选择器
    const marketSelect = screen.getByText('选择市场')
    expect(marketSelect).toBeInTheDocument()

    // 点击市场选择器
    fireEvent.click(marketSelect)

    // 选择上海市场
    await waitFor(() => {
      const shOption = screen.getByText('上海')
      fireEvent.click(shOption)
    })

    // 验证API调用参数
    await waitFor(() => {
      expect(mockApiClient.apiClient.get).toHaveBeenCalledWith(
        expect.stringContaining('market=SH')
      )
    })
  })

  it('应该处理行业筛选', async () => {
    render(<StockList />)

    await waitFor(() => {
      expect(screen.getByText('股票列表')).toBeInTheDocument()
    })

    // 获取行业选择器
    const sectorSelect = screen.getByText('选择行业')
    expect(sectorSelect).toBeInTheDocument()

    // 点击行业选择器
    fireEvent.click(sectorSelect)

    // 等待行业数据加载并选择科技行业
    await waitFor(() => {
      const techOption = screen.getByText('科技')
      fireEvent.click(techOption)
    })

    // 验证API调用参数
    await waitFor(() => {
      expect(mockApiClient.apiClient.get).toHaveBeenCalledWith(
        expect.stringContaining('sector=科技')
      )
    })
  })

  it('应该处理自动刷新开关', async () => {
    render(<StockList />)

    await waitFor(() => {
      expect(screen.getByText('股票列表')).toBeInTheDocument()
    })

    // 获取自动刷新开关
    const refreshSwitch = screen.getByRole('switch')
    expect(refreshSwitch).toBeInTheDocument()

    // 初始状态应该是开启的
    expect(refreshSwitch).toBeChecked()

    // 关闭自动刷新
    fireEvent.click(refreshSwitch)

    // 验证开关状态改变
    expect(refreshSwitch).not.toBeChecked()
  })

  it('应该处理手动刷新', async () => {
    render(<StockList />)

    await waitFor(() => {
      expect(screen.getByText('股票列表')).toBeInTheDocument()
    })

    // 获取刷新按钮
    const refreshButton = screen.getByText('刷新')
    expect(refreshButton).toBeInTheDocument()

    // 清除之前的mock调用
    vi.clearAllMocks()

    // 点击刷新按钮
    fireEvent.click(refreshButton)

    // 验证刷新API被调用
    await waitFor(() => {
      expect(mockApiClient.apiClient.get).toHaveBeenCalled()
    })
  })

  it('应该处理股票选择事件', async () => {
    const onStockSelectMock = vi.fn()
    render(<StockList onStockSelect={onStockSelectMock} />)

    await waitFor(() => {
      expect(screen.getByText('股票列表')).toBeInTheDocument()
    })

    // 点击第一行股票
    const firstStockRow = screen.getByText(mockStockData[0].symbol).closest('tr')
    expect(firstStockRow).toBeInTheDocument()

    fireEvent.click(firstStockRow!)

    // 验证回调函数被调用
    expect(onStockSelectMock).toHaveBeenCalledWith(
      expect.objectContaining({
        symbol: mockStockData[0].symbol,
        name: mockStockData[0].name,
      })
    )
  })

  it('应该正确渲染涨跌标签', async () => {
    render(<StockList />)

    await waitFor(() => {
      expect(screen.getByText('股票列表')).toBeInTheDocument()
    })

    // 检查涨跌标签渲染
    mockStockData.slice(0, 5).forEach(stock => {
      if (stock.change > 0) {
        // 检查上涨标签
        const positiveTag = screen.getByText(`+${stock.changePercent}%`)
        expect(positiveTag).toBeInTheDocument()
        expect(positiveTag).toHaveClass('ant-tag-red')
      } else if (stock.change < 0) {
        // 检查下跌标签
        const negativeTag = screen.getByText(`${stock.changePercent}%`)
        expect(negativeTag).toBeInTheDocument()
        expect(negativeTag).toHaveClass('ant-tag-green')
      }
    })
  })

  it('应该处理自选股功能', async () => {
    const mockAddToWatchlist = vi.fn()
    const mockRemoveFromWatchlist = vi.fn()

    // Mock watchlist store
    vi.doMock('@/stores/watchlistStore', () => ({
      useWatchlistStore: () => ({
        watchlist: [],
        addToWatchlist: mockAddToWatchlist,
        removeFromWatchlist: mockRemoveFromWatchlist,
      }),
    }))

    render(<StockList />)

    await waitFor(() => {
      expect(screen.getByText('股票列表')).toBeInTheDocument()
    })

    // 获取第一只股票的收藏按钮
    const favoriteButtons = screen.getAllByRole('button')
    const favoriteButton = favoriteButtons.find(btn =>
      btn.querySelector('svg')?.getAttribute('data-icon') === 'star'
    )

    expect(favoriteButton).toBeInTheDocument()

    // 点击收藏按钮
    fireEvent.click(favoriteButton!)

    // 验证添加到自选股的函数被调用
    await waitFor(() => {
      expect(mockAddToWatchlist).toHaveBeenCalledWith(
        expect.objectContaining({
          symbol: mockStockData[0].symbol,
        })
      )
    })
  })

  it('应该处理分页功能', async () => {
    // Mock更多数据用于分页测试
    const largeStockList = Array.from({ length: 25 }, (_, i) => ({
      ...mockStockData[0],
      id: i + 1,
      symbol: `STOCK${String(i + 1).padStart(3, '0')}`,
      name: `Stock Company ${i + 1}`,
    }))

    mockApiClient.apiClient.get.mockImplementation((url: string) => {
      if (url.includes('/api/stocks/list')) {
        return Promise.resolve({
          data: {
            data: largeStockList.slice(0, 10),
            pagination: {
              page: 1,
              size: 10,
              total: 25,
              pages: 3,
            },
          },
        })
      }
      return Promise.resolve({ data: [] })
    })

    render(<StockList pageSize={10} />)

    await waitFor(() => {
      expect(screen.getByText('股票列表')).toBeInTheDocument()
    })

    // 检查分页组件是否渲染
    await waitFor(() => {
      expect(screen.getByText('第 1-10 条，共 25 条')).toBeInTheDocument()
    })

    // 点击下一页
    const nextPageButton = screen.getByTitle('下一页')
    fireEvent.click(nextPageButton)

    // 验证API调用参数更新
    await waitFor(() => {
      expect(mockApiClient.apiClient.get).toHaveBeenCalledWith(
        expect.stringContaining('page=2')
      )
    })
  })

  it('应该正确处理错误状态', async () => {
    // Mock API错误
    mockApiClient.apiClient.get.mockRejectedValue(new Error('Network error'))

    render(<StockList />)

    // 等待错误处理
    await waitFor(() => {
      expect(screen.getByText('股票列表')).toBeInTheDocument()
    })

    // 表格应该显示加载状态或错误状态
    const table = screen.getByRole('table')
    expect(table).toBeInTheDocument()
  })

  it('应该正确显示实时数据标识', async () => {
    render(<StockList showRealtime={true} />)

    await waitFor(() => {
      expect(screen.getByText('股票列表')).toBeInTheDocument()
    })

    // 等待实时数据加载
    await waitFor(() => {
      expect(screen.getByText('实时数据')).toBeInTheDocument()
    })
  })

  it('应该响应组件属性变化', async () => {
    const { rerender } = render(<StockList pageSize={10} />)

    await waitFor(() => {
      expect(screen.getByText('股票列表')).toBeInTheDocument()
    })

    // 重新渲染并更新页面大小
    rerender(<StockList pageSize={20} />)

    // 验证组件能正确响应属性变化
    expect(screen.getByText('股票列表')).toBeInTheDocument()
  })

  it('应该正确处理搜索结果的显示', async () => {
    render(<StockList />)

    await waitFor(() => {
      expect(screen.getByText('股票列表')).toBeInTheDocument()
    })

    // Mock搜索API响应
    mockApiClient.apiClient.get.mockImplementation((url: string) => {
      if (url.includes('/api/stocks/search')) {
        return Promise.resolve({
          data: [mockStockData[0]],
        })
      }
      return Promise.resolve({ data: [] })
    })

    // 获取搜索框并输入关键词
    const searchInput = screen.getByPlaceholderText('搜索股票代码或名称')
    fireEvent.change(searchInput, { target: { value: 'AAPL' } })

    // 等待搜索结果显示
    await waitFor(() => {
      expect(screen.getByText('搜索结果')).toBeInTheDocument()
      expect(screen.getByText(mockStockData[0].name)).toBeInTheDocument()
    })
  })
})