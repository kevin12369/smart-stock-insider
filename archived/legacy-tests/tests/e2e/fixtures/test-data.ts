/**
 * 端到端测试数据
 * 提供测试用的用户数据和业务数据
 */

export interface TestUser {
  id: string;
  username: string;
  email: string;
  password: string;
  displayName: string;
  riskTolerance: 'conservative' | 'moderate' | 'aggressive';
  investmentGoals: string[];
  preferredSectors: string[];
}

export interface TestStock {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume: string;
  marketCap: string;
}

export interface TestNews {
  id: string;
  title: string;
  summary: string;
  source: string;
  category: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  publishedAt: string;
  url: string;
}

export interface TestConversation {
  id: string;
  userId: string;
  messages: TestMessage[];
  createdAt: string;
}

export interface TestMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: string;
  metadata?: any;
}

// 测试用户数据
export const TEST_USERS: TestUser[] = [
  {
    id: 'user-conservative',
    username: 'conservative_user',
    email: 'conservative@test.com',
    password: 'Test123456!',
    displayName: '保守投资者',
    riskTolerance: 'conservative',
    investmentGoals: ['income', 'preservation'],
    preferredSectors: ['utilities', 'consumer_staples']
  },
  {
    id: 'user-moderate',
    username: 'moderate_user',
    email: 'moderate@test.com',
    password: 'Test123456!',
    displayName: '稳健投资者',
    riskTolerance: 'moderate',
    investmentGoals: ['growth', 'income'],
    preferredSectors: ['technology', 'healthcare']
  },
  {
    id: 'user-aggressive',
    username: 'aggressive_user',
    email: 'aggressive@test.com',
    password: 'Test123456!',
    displayName: '激进投资者',
    riskTolerance: 'aggressive',
    investmentGoals: ['growth', 'speculation'],
    preferredSectors: ['technology', 'biotech']
  }
];

// 测试股票数据
export const TEST_STOCKS: TestStock[] = [
  {
    symbol: 'AAPL',
    name: 'Apple Inc.',
    price: 178.45,
    change: 2.35,
    changePercent: 1.33,
    volume: '52.47M',
    marketCap: '2.78T'
  },
  {
    symbol: 'GOOGL',
    name: 'Alphabet Inc.',
    price: 138.21,
    change: -0.85,
    changePercent: -0.61,
    volume: '28.46M',
    marketCap: '1.73T'
  },
  {
    symbol: 'MSFT',
    name: 'Microsoft Corporation',
    price: 378.91,
    change: 5.23,
    changePercent: 1.40,
    volume: '22.65M',
    marketCap: '2.81T'
  },
  {
    symbol: 'TSLA',
    name: 'Tesla Inc.',
    price: 242.84,
    change: -3.21,
    changePercent: -1.30,
    volume: '118.23M',
    marketCap: '772B'
  }
];

// 测试新闻数据
export const TEST_NEWS: TestNews[] = [
  {
    id: 'news-1',
    title: '苹果发布新款iPhone，销量超出预期',
    summary: '苹果公司最新发布的iPhone 15系列销量表现强劲，推动股价上涨。',
    source: '财经日报',
    category: 'technology',
    sentiment: 'positive',
    publishedAt: '2024-01-15T09:30:00Z',
    url: 'https://example.com/news/1'
  },
  {
    id: 'news-2',
    title: '特斯拉第三季度交付量创新高',
    summary: '特斯拉第三季度全球交付量达到历史新高，市场反应积极。',
    source: '汽车周刊',
    category: 'automotive',
    sentiment: 'positive',
    publishedAt: '2024-01-14T14:20:00Z',
    url: 'https://example.com/news/2'
  },
  {
    id: 'news-3',
    title: '全球芯片短缺影响汽车制造业',
    summary: '持续的芯片短缺问题对全球汽车制造业造成严重影响。',
    source: '经济观察报',
    category: 'technology',
    sentiment: 'negative',
    publishedAt: '2024-01-13T11:45:00Z',
    url: 'https://example.com/news/3'
  }
];

// 测试对话数据
export const TEST_CONVERSATIONS: TestConversation[] = [
  {
    id: 'conv-stock-analysis',
    userId: 'user-moderate',
    messages: [
      {
        id: 'msg-1',
        type: 'user',
        content: '我想了解AAPL股票的投资前景',
        timestamp: '2024-01-15T10:00:00Z'
      },
      {
        id: 'msg-2',
        type: 'assistant',
        content: '根据技术分析，AAPL目前处于上升趋势中。MACD指标显示买入信号，RSI处于中性区域。',
        timestamp: '2024-01-15T10:00:05Z',
        metadata: {
          confidence: 0.85,
          symbols_mentioned: ['AAPL'],
          analysis_type: 'technical'
        }
      }
    ],
    createdAt: '2024-01-15T10:00:00Z'
  }
];

// 测试用例数据
export const TEST_SCENARIOS = {
  stockSearch: [
    {
      query: 'AAPL',
      expectedResults: ['Apple Inc.', 'AAPL'],
      description: '搜索苹果股票'
    },
    {
      query: '科技',
      expectedResults: ['Apple', 'Microsoft', 'Google'],
      description: '搜索科技公司股票'
    }
  ],

  aiAnalysis: [
    {
      symbol: 'AAPL',
      question: '请分析这只股票的投资价值',
      expectedTopics: ['技术分析', '基本面', '风险评估'],
      description: '请求股票投资分析'
    },
    {
      symbol: 'TSLA',
      question: '这个风险水平适合保守投资者吗？',
      expectedTopics: ['风险分析', '投资建议'],
      description: '询问投资风险'
    }
  ],

  portfolioOptimization: [
    {
      symbols: ['AAPL', 'GOOGL', 'MSFT'],
      riskTolerance: 'moderate',
      expectedOptimization: 'balanced_allocation',
      description: '中等风险投资组合优化'
    },
    {
      symbols: ['TSLA', 'NVDA'],
      riskTolerance: 'aggressive',
      expectedOptimization: 'growth_focused',
      description: '激进型投资组合优化'
    }
  ]
};

// 错误场景测试数据
export const ERROR_SCENARIOS = {
  invalidStock: {
    symbol: 'INVALID',
    expectedError: 'Stock not found',
    description: '无效股票代码'
  },

  emptySearch: {
    query: '',
    expectedError: 'Search query cannot be empty',
    description: '空搜索查询'
  },

  networkError: {
    scenario: 'offline',
    expectedError: 'Network connection failed',
    description: '网络连接失败'
  }
};

// 性能测试数据
export const PERFORMANCE_THRESHOLDS = {
  pageLoad: {
    maxLoadTime: 3000, // 3秒
    maxFirstContentfulPaint: 1500, // 1.5秒
    maxLargestContentfulPaint: 2500, // 2.5秒
  },

  apiResponse: {
    maxResponseTime: 2000, // 2秒
    maxStockDataResponse: 1000, // 1秒
    maxAIAnalysisResponse: 10000, // 10秒
  },

  userInteraction: {
    maxClickResponse: 200, // 200ms
    maxFormSubmit: 1000, // 1秒
    maxSearchResponse: 500, // 500ms
  }
};

// 可访问性测试数据
export const ACCESSIBILITY_REQUIREMENTS = {
  colorContrast: {
    minRatio: 4.5, // WCAG AA标准
    largeTextMinRatio: 3.0
  },

  keyboardNavigation: {
    allInteractiveElements: true,
    focusVisible: true,
    trapFocus: ['modal', 'dialog']
  },

  screenReader: {
    altText: ['img', 'chart'],
    ariaLabels: ['button', 'link', 'form'],
    semanticHTML: ['header', 'main', 'nav', 'footer']
  }
};

// 获取测试用户
export function getTestUser(type: 'conservative' | 'moderate' | 'aggressive'): TestUser {
  return TEST_USERS.find(user => user.riskTolerance === type) || TEST_USERS[1];
}

// 获取测试股票
export function getTestStock(symbol: string): TestStock | undefined {
  return TEST_STOCKS.find(stock => stock.symbol === symbol);
}

// 获取测试新闻
export function getTestNews(category?: string): TestNews[] {
  if (category) {
    return TEST_NEWS.filter(news => news.category === category);
  }
  return TEST_NEWS;
}

// 获取测试对话
export function getTestConversation(userId: string): TestConversation | undefined {
  return TEST_CONVERSATIONS.find(conv => conv.userId === userId);
}

// 创建自定义测试数据
export function createCustomTestData<T>(template: Partial<T>, overrides: Partial<T> = {}): T {
  return { ...template, ...overrides } as T;
}