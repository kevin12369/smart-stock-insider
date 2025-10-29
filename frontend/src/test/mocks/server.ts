/**
 * Mock Server 配置
 * 使用 MSW (Mock Service Worker) 拦截 API 请求
 */

import { setupServer } from 'msw/node'
import { rest } from 'msw'
import {
  mockStockData,
  mockNewsData,
  mockAIAnalysisData,
  mockPortfolioData,
  mockSentimentData
} from '../data'

// 定义基础URL
const API_BASE_URL = 'http://localhost:8000/api'

// 创建handlers
export const handlers = [
  // 股票数据API
  rest.get(`${API_BASE_URL}/stocks/:symbol`, (req, res, ctx) => {
    const { symbol } = req.params
    const stock = mockStockData.find(s => s.symbol === symbol)

    if (!stock) {
      return res(
        ctx.status(404),
        ctx.json({ error: 'Stock not found' })
      )
    }

    return res(
      ctx.status(200),
      ctx.json(stock)
    )
  }),

  rest.get(`${API_BASE_URL}/stocks`, (req, res, ctx) => {
    const page = req.url.searchParams.get('page') || '1'
    const limit = req.url.searchParams.get('limit') || '10'
    const search = req.url.searchParams.get('search')

    let filteredStocks = mockStockData

    if (search) {
      filteredStocks = mockStockData.filter(stock =>
        stock.symbol.toLowerCase().includes(search.toLowerCase()) ||
        stock.name.toLowerCase().includes(search.toLowerCase())
      )
    }

    const startIndex = (parseInt(page) - 1) * parseInt(limit)
    const endIndex = startIndex + parseInt(limit)
    const paginatedStocks = filteredStocks.slice(startIndex, endIndex)

    return res(
      ctx.status(200),
      ctx.json({
        data: paginatedStocks,
        pagination: {
          page: parseInt(page),
          limit: parseInt(limit),
          total: filteredStocks.length,
          pages: Math.ceil(filteredStocks.length / parseInt(limit))
        }
      })
    )
  }),

  // 实时价格API
  rest.get(`${API_BASE_URL}/stocks/:symbol/realtime`, (req, res, ctx) => {
    const { symbol } = req.params
    const stock = mockStockData.find(s => s.symbol === symbol)

    if (!stock) {
      return res(
        ctx.status(404),
        ctx.json({ error: 'Stock not found' })
      )
    }

    // 模拟实时价格变化
    const priceVariation = (Math.random() - 0.5) * 2
    const currentPrice = stock.price * (1 + priceVariation / 100)

    return res(
      ctx.status(200),
      ctx.json({
        symbol: stock.symbol,
        price: parseFloat(currentPrice.toFixed(2)),
        change: parseFloat((currentPrice - stock.price).toFixed(2)),
        changePercent: parseFloat(((currentPrice - stock.price) / stock.price * 100).toFixed(2)),
        timestamp: new Date().toISOString(),
        volume: Math.floor(Math.random() * 1000000) + 100000
      })
    )
  }),

  // 新闻数据API
  rest.get(`${API_BASE_URL}/news`, (req, res, ctx) => {
    const page = req.url.searchParams.get('page') || '1'
    const limit = req.url.searchParams.get('limit') || '20'
    const category = req.url.searchParams.get('category')

    let filteredNews = mockNewsData

    if (category) {
      filteredNews = mockNewsData.filter(news =>
        news.category.toLowerCase() === category.toLowerCase()
      )
    }

    const startIndex = (parseInt(page) - 1) * parseInt(limit)
    const endIndex = startIndex + parseInt(limit)
    const paginatedNews = filteredNews.slice(startIndex, endIndex)

    return res(
      ctx.status(200),
      ctx.json({
        data: paginatedNews,
        pagination: {
          page: parseInt(page),
          limit: parseInt(limit),
          total: filteredNews.length,
          pages: Math.ceil(filteredNews.length / parseInt(limit))
        }
      })
    )
  }),

  rest.get(`${API_BASE_URL}/news/:id`, (req, res, ctx) => {
    const { id } = req.params
    const news = mockNewsData.find(n => n.id === id)

    if (!news) {
      return res(
        ctx.status(404),
        ctx.json({ error: 'News not found' })
      )
    }

    return res(
      ctx.status(200),
      ctx.json(news)
    )
  }),

  // AI分析API
  rest.post(`${API_BASE_URL}/ai/analyze`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json(mockAIAnalysisData)
    )
  }),

  rest.get(`${API_BASE_URL}/ai/history`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        data: [mockAIAnalysisData],
        total: 1
      })
    )
  }),

  // 情感分析API
  rest.post(`${API_BASE_URL}/sentiment/analyze`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json(mockSentimentData)
    )
  }),

  rest.get(`${API_BASE_URL}/sentiment/market`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        sentiment: 'bullish',
        score: 0.75,
        confidence: 0.85,
        timestamp: new Date().toISOString(),
        sentiment_distribution: {
          bullish: 45,
          bearish: 25,
          neutral: 30
        }
      })
    )
  }),

  // 投资组合API
  rest.post(`${API_BASE_URL}/portfolio/optimize`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json(mockPortfolioData)
    )
  }),

  rest.get(`${API_BASE_URL}/portfolio/:id/performance`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        portfolio_id: req.params.id,
        total_return: 0.125,
        annualized_return: 0.156,
        volatility: 0.089,
        sharpe_ratio: 1.75,
        max_drawdown: -0.045,
        performance_history: Array.from({ length: 30 }, (_, i) => ({
          date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          value: 100000 * (1 + Math.random() * 0.2 - 0.05)
        }))
      })
    )
  }),

  // 聊天机器人API
  rest.post(`${API_BASE_URL}/chatbot/conversation/start`, (req, res, ctx) => {
    return res(
      ctx.status(201),
      ctx.json({
        conversation_id: 'conv_123456',
        session_id: 'sess_789012',
        status: 'active',
        created_at: new Date().toISOString()
      })
    )
  }),

  rest.post(`${API_BASE_URL}/chatbot/message`, async (req, res, ctx) => {
    const { message, conversation_id } = await req.json()

    // 模拟AI回复
    const responses = [
      '根据技术分析，该股票目前处于上升趋势中。',
      '建议关注成交量变化，确认突破的有效性。',
      '市场情绪偏向乐观，但需注意风险管理。',
      '从基本面来看，公司业绩表现良好。'
    ]

    return res(
      ctx.status(200),
      ctx.json({
        conversation_id,
        message_id: 'msg_' + Math.random().toString(36).substr(2, 9),
        response: responses[Math.floor(Math.random() * responses.length)],
        timestamp: new Date().toISOString(),
        metadata: {
          sentiment: 'neutral',
          confidence: 0.8,
          intent: 'investment_advice'
        }
      })
    )
  }),

  // 用户分析API
  rest.get(`${API_BASE_URL}/analytics/user/:userId/behavior`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        user_id: req.params.userId,
        total_sessions: 156,
        total_duration: 23400,
        avg_session_duration: 150,
        pages_viewed: 2340,
        bounce_rate: 0.25,
        conversion_rate: 0.15,
        preferred_stocks: ['AAPL', 'GOOGL', 'MSFT'],
        preferred_categories: ['technology', 'healthcare'],
        last_activity: new Date().toISOString()
      })
    )
  }),

  rest.get(`${API_BASE_URL}/analytics/funnel`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        visitors: 10000,
        signups: 2500,
        activated_users: 1800,
        premium_users: 450,
        conversion_rates: {
          visitor_to_signup: 0.25,
          signup_to_activation: 0.72,
          activation_to_premium: 0.25
        },
        period: '30d'
      })
    )
  }),

  // 错误处理
  rest.get(`${API_BASE_URL}/error`, (req, res, ctx) => {
    return res(
      ctx.status(500),
      ctx.json({ error: 'Internal server error' })
    )
  }),

  // 超时处理
  rest.get(`${API_BASE_URL}/timeout`, (req, res, ctx) => {
    return res(
      ctx.delay(10000), // 10秒延迟
      ctx.status(200),
      ctx.json({ message: 'This should timeout' })
    )
  }),
]

// 创建服务器实例
export const server = setupServer(...handlers)