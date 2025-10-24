import React, { useState, useEffect } from 'react'
import {
  Card,
  Row,
  Col,
  List,
  Tag,
  Button,
  Space,
  Input,
  Select,
  Typography,
  Avatar,
  Divider,
  Badge,
  Tooltip,
  Modal,
  Spin
} from 'antd'
import {
  SearchOutlined,
  ReloadOutlined,
  EyeOutlined,
  HeartOutlined,
  ShareAltOutlined,
  BellOutlined,
  FilterOutlined,
  TrendingUpOutlined,
  FireOutlined,
  ClockCircleOutlined,
  ThunderboltOutlined
} from '@ant-design/icons'
import apiService from '../services/api'

const { Title, Text, Paragraph } = Typography
const { Option } = Select

// 新闻接口定义
interface NewsItem {
  id: string
  title: string
  summary: string
  content: string
  source: string
  author: string
  url: string
  publish_time: string
  category: string
  tags: string[]
  relevance: number
  stock_codes: string[]
  sentiment?: {
    label: string
    score: number
    confidence: number
  }
  created_at: string
  updated_at: string
}

interface NewsSource {
  id: string
  name: string
  type: string
  url: string
  enabled: boolean
  priority: number
  last_updated: string
  status: string
}

const NewsHub: React.FC = () => {
  const [news, setNews] = useState<NewsItem[]>([])
  const [sources, setSources] = useState<NewsSource[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [selectedSource, setSelectedSource] = useState<string>('all')
  const [searchKeyword, setSearchKeyword] = useState('')
  const [selectedNews, setSelectedNews] = useState<NewsItem | null>(null)
  const [newsDetailVisible, setNewsDetailVisible] = useState(false)
  const [filterVisible, setFilterVisible] = useState(false)

  useEffect(() => {
    loadNews()
    loadSources()
  }, [])

  const loadNews = async (category: string = 'all', source: string = 'all', keyword: string = '') => {
    try {
      setLoading(true)

      // 模拟API调用 - 实际应该调用后端新闻服务
      const mockNews: NewsItem[] = [
        {
          id: 'news_001',
          title: '平安银行2024年业绩预告超预期，净利润同比增长15%',
          summary: '平安银行发布2024年度业绩预告，预计全年净利润将同比增长15%左右，主要得益于零售业务快速发展和资产质量持续改善。',
          content: '平安银行今日晚间发布2024年度业绩预告，预计全年净利润将同比增长15%左右，超出市场预期。公告显示，业绩增长主要得益于零售业务快速发展和资产质量持续改善。截至2024年末，平安银行资产总额突破5万亿元，不良贷款率控制在1.5%以内。零售业务收入占比提升至55%，数字化转型成效显著。',
          source: '东方财富',
          author: '财经记者',
          url: 'https://news.example.com/news001',
          publish_time: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
          category: '财经',
          tags: ['银行', '业绩预告', '平安银行'],
          relevance: 0.95,
          stock_codes: ['000001'],
          sentiment: {
            label: 'positive',
            score: 0.75,
            confidence: 0.85
          },
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          id: 'news_002',
          title: 'A股三大指数集体收涨，新能源汽车板块领涨',
          summary: '今日A股三大指数集体收涨，上证指数涨1.2%，深证成指涨1.5%，创业板指涨1.8%。新能源汽车板块表现突出，多只个股涨停。',
          content: '今日A股市场表现强劲，三大指数集体收涨。上证指数收盘报3089点，上涨1.2%；深证成指收盘报10245点，上涨1.5%；创业板指收盘报1958点，上涨1.8%。行业板块方面，新能源汽车、半导体、军工等板块涨幅居前，银行、房地产等传统板块相对弱势。市场成交量明显放大，沪深两市成交额突破8000亿元。',
          source: '同花顺',
          author: '股市分析师',
          url: 'https://news.example.com/news002',
          publish_time: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
          category: '股市',
          tags: ['A股', '指数', '新能源汽车'],
          relevance: 0.88,
          stock_codes: [],
          sentiment: {
            label: 'positive',
            score: 0.65,
            confidence: 0.80
          },
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          id: 'news_003',
          title: '🔥 热门话题：科技股集体上涨，AI概念股爆发',
          summary: '在2小时期间，共发现5条相关新闻：科技股表现强势，人工智能、芯片、软件等细分领域全面开花，多只个股涨停。',
          content: '热门话题详情：\n\n1. 科技股集体上涨，AI概念股爆发\n   来源：东方财富\n   时间：14:30\n   摘要：受利好消息刺激，人工智能概念股集体爆发，多只个股涨停。\n\n2. 半导体板块强势崛起\n   来源：同花顺\n   时间：14:15\n   摘要：半导体板块表现强势，芯片设计、制造等子板块全线上涨。\n\n3. 软件服务板块表现活跃\n   来源：新浪财经\n   时间：14:00\n   摘要：软件服务板块表现活跃，云计算、大数据等细分领域涨幅居前。',
          source: '智股通聚合',
          author: '系统自动聚合',
          url: '',
          publish_time: new Date().toISOString(),
          category: '热门话题',
          tags: ['热门话题', '聚合', '趋势'],
          relevance: 1.0,
          stock_codes: ['000001', '000002', '600036'],
          sentiment: {
            label: 'trending',
            score: 0.0,
            confidence: 0.8
          },
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
      ]

      // 应用筛选条件
      let filteredNews = mockNews

      if (category !== 'all') {
        filteredNews = filteredNews.filter(item => item.category === category)
      }

      if (source !== 'all') {
        filteredNews = filteredNews.filter(item => item.source === source)
      }

      if (keyword) {
        filteredNews = filteredNews.filter(item =>
          item.title.includes(keyword) ||
          item.summary.includes(keyword) ||
          item.tags.some(tag => tag.includes(keyword))
        )
      }

      setNews(filteredNews)
    } catch (error) {
      console.error('加载新闻失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadSources = async () => {
    try {
      // 模拟新闻源数据
      const mockSources: NewsSource[] = [
        {
          id: 'east_money',
          name: '东方财富',
          type: 'website',
          url: 'https://www.eastmoney.com',
          enabled: true,
          priority: 1,
          last_updated: new Date().toISOString(),
          status: 'active'
        },
        {
          id: 'tonghuashun',
          name: '同花顺',
          type: 'website',
          url: 'https://www.10jqka.com.cn',
          enabled: true,
          priority: 2,
          last_updated: new Date().toISOString(),
          status: 'active'
        },
        {
          id: 'sina',
          name: '新浪财经',
          type: 'website',
          url: 'https://finance.sina.com.cn',
          enabled: true,
          priority: 3,
          last_updated: new Date().toISOString(),
          status: 'active'
        },
        {
          id: 'tencent',
          name: '腾讯财经',
          type: 'website',
          url: 'https://finance.qq.com',
          enabled: true,
          priority: 4,
          last_updated: new Date().toISOString(),
          status: 'active'
        }
      ]
      setSources(mockSources)
    } catch (error) {
      console.error('加载新闻源失败:', error)
    }
  }

  const handleSearch = (value: string) => {
    setSearchKeyword(value)
    loadNews(selectedCategory, selectedSource, value)
  }

  const handleCategoryChange = (category: string) => {
    setSelectedCategory(category)
    loadNews(category, selectedSource, searchKeyword)
  }

  const handleSourceChange = (source: string) => {
    setSelectedSource(source)
    loadNews(selectedCategory, source, searchKeyword)
  }

  const handleNewsClick = (newsItem: NewsItem) => {
    setSelectedNews(newsItem)
    setNewsDetailVisible(true)
  }

  const getCategoryColor = (category: string) => {
    const colorMap: Record<string, string> = {
      '财经': 'blue',
      '股市': 'green',
      '政策': 'orange',
      '公司': 'purple',
      '国际': 'red',
      '热门话题': 'red',
      'breaking': 'red',
      'major': 'orange'
    }
    return colorMap[category] || 'default'
  }

  const getSentimentIcon = (sentiment?: { label: string; score: number }) => {
    if (!sentiment) return null

    switch (sentiment.label) {
      case 'positive': return '📈'
      case 'negative': return '📉'
      case 'neutral': return '➡️'
      case 'trending': return '🔥'
      default: return '📊'
    }
  }

  const getNewsAvatar = (category: string) => {
    const iconMap: Record<string, React.ReactNode> = {
      '财经': <TrendingUpOutlined />,
      '股市': <TrendingUpOutlined />,
      '政策': <ThunderboltOutlined />,
      '公司': <FireOutlined />,
      '热门话题': <FireOutlined />
    }
    return iconMap[category] || <ClockCircleOutlined />
  }

  const formatPublishTime = (publishTime: string) => {
    const now = new Date()
    const publishDate = new Date(publishTime)
    const diffMs = now.getTime() - publishDate.getTime()
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffHours / 24)

    if (diffHours < 1) {
      return '刚刚'
    } else if (diffHours < 24) {
      return `${diffHours}小时前`
    } else if (diffDays < 7) {
      return `${diffDays}天前`
    } else {
      return publishDate.toLocaleDateString()
    }
  }

  const categories = [
    { value: 'all', label: '全部分类' },
    { value: '财经', label: '财经' },
    { value: '股市', label: '股市' },
    { value: '政策', label: '政策' },
    { value: '公司', label: '公司' },
    { value: '国际', label: '国际' },
    { value: '热门话题', label: '热门话题' }
  ]

  return (
    <div style={{ padding: '24px', background: '#f5f5f5', minHeight: '100vh' }}>
      <Title level={2} style={{ marginBottom: '24px' }}>
        <ThunderboltOutlined /> 新闻中心
      </Title>

      {/* 筛选和搜索区域 */}
      <Card style={{ marginBottom: '24px' }}>
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} sm={12} md={6}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Text strong>分类筛选</Text>
              <Select
                value={selectedCategory}
                onChange={handleCategoryChange}
                style={{ width: '100%' }}
                placeholder="选择分类"
              >
                {categories.map(cat => (
                  <Option key={cat.value} value={cat.value}>
                    {cat.label}
                  </Option>
                ))}
              </Select>
            </Space>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Text strong>新闻源</Text>
              <Select
                value={selectedSource}
                onChange={handleSourceChange}
                style={{ width: '100%' }}
                placeholder="选择新闻源"
              >
                <Option value="all">全部新闻源</Option>
                {sources.map(source => (
                  <Option key={source.id} value={source.name}>
                    <Badge
                      status={source.enabled ? 'success' : 'default'}
                      text={source.name}
                    />
                  </Option>
                ))}
              </Select>
            </Space>
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Text strong>搜索新闻</Text>
              <Input.Search
                placeholder="搜索新闻标题、摘要或标签"
                value={searchKeyword}
                onChange={(e) => setSearchKeyword(e.target.value)}
                onSearch={handleSearch}
                enterButton={<SearchOutlined />}
              />
            </Space>
          </Col>
          <Col xs={24} sm={12} md={4}>
            <Space>
              <Button
                icon={<ReloadOutlined />}
                onClick={() => loadNews(selectedCategory, selectedSource, searchKeyword)}
                loading={loading}
              >
                刷新
              </Button>
              <Button
                icon={<FilterOutlined />}
                onClick={() => setFilterVisible(true)}
              >
                高级筛选
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 新闻源状态 */}
      <Card
        title="新闻源状态"
        size="small"
        style={{ marginBottom: '24px' }}
        extra={<Text type="secondary">共 {sources.length} 个新闻源</Text>}
      >
        <Row gutter={[16, 16]}>
          {sources.map(source => (
            <Col xs={24} sm={12} md={6} key={source.id}>
              <Card size="small">
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Space>
                    <Badge status={source.enabled ? 'success' : 'default'} />
                    <Text strong>{source.name}</Text>
                  </Space>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    优先级: {source.priority} | 最后更新: {formatPublishTime(source.last_updated)}
                  </Text>
                </Space>
              </Card>
            </Col>
          ))}
        </Row>
      </Card>

      {/* 新闻列表 */}
      <Card title="最新新闻" extra={<Text type="secondary">共 {news.length} 条新闻</Text>}>
        <Spin spinning={loading}>
          <List
            dataSource={news}
            renderItem={(item) => (
              <List.Item
                key={item.id}
                style={{
                  padding: '16px',
                  borderRadius: '8px',
                  marginBottom: '12px',
                  backgroundColor: '#fff',
                  border: '1px solid #f0f0f0',
                  cursor: 'pointer'
                }}
                onClick={() => handleNewsClick(item)}
                actions={[
                  <Tooltip title="查看详情">
                    <Button type="link" icon={<EyeOutlined />} />
                  </Tooltip>,
                  <Tooltip title="收藏">
                    <Button type="link" icon={<HeartOutlined />} />
                  </Tooltip>,
                  <Tooltip title="分享">
                    <Button type="link" icon={<ShareAltOutlined />} />
                  </Tooltip>,
                  <Tooltip title="订阅提醒">
                    <Button type="link" icon={<BellOutlined />} />
                  </Tooltip>
                ]}
              >
                <List.Item.Meta
                  avatar={
                    <Avatar
                      style={{ backgroundColor: getCategoryColor(item.category) }}
                      icon={getNewsAvatar(item.category)}
                    />
                  }
                  title={
                    <Space>
                      <Text strong>{item.title}</Text>
                      {item.sentiment && (
                        <Tooltip title={`情感: ${item.sentiment.label} (${item.sentiment.score.toFixed(2)})`}>
                          <span>{getSentimentIcon(item.sentiment)}</span>
                        </Tooltip>
                      )}
                      {item.category === '热门话题' && (
                        <Tag color="red" icon={<FireOutlined />}>
                          热门
                        </Tag>
                      )}
                    </Space>
                  }
                  description={
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <Text type="secondary">{item.summary}</Text>
                      <Space split={<Divider type="vertical" />}>
                        <Tag color={getCategoryColor(item.category)}>{item.category}</Tag>
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                          {item.source}
                        </Text>
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                          {formatPublishTime(item.publish_time)}
                        </Text>
                        {item.stock_codes.length > 0 && (
                          <Text type="secondary" style={{ fontSize: '12px' }}>
                            相关股票: {item.stock_codes.join(', ')}
                          </Text>
                        )}
                      </Space>
                      <div>
                        {item.tags.map(tag => (
                          <Tag key={tag} size="small" style={{ margin: '2px 4px 2px 0' }}>
                            {tag}
                          </Tag>
                        ))}
                      </div>
                    </Space>
                  }
                />
              </List.Item>
            )}
            pagination={{
              pageSize: 20,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total) => `共 ${total} 条新闻`
            }}
          />
        </Spin>
      </Card>

      {/* 新闻详情模态框 */}
      <Modal
        title="新闻详情"
        open={newsDetailVisible}
        onCancel={() => setNewsDetailVisible(false)}
        footer={[
          <Button key="close" onClick={() => setNewsDetailVisible(false)}>
            关闭
          </Button>,
          <Button key="original" type="primary">
            查看原文
          </Button>
        ]}
        width={800}
      >
        {selectedNews && (
          <div>
            <Title level={3}>{selectedNews.title}</Title>
            <Space split={<Divider type="vertical" />} style={{ marginBottom: '16px' }}>
              <Text>来源: {selectedNews.source}</Text>
              <Text>作者: {selectedNews.author}</Text>
              <Text>发布时间: {new Date(selectedNews.publish_time).toLocaleString()}</Text>
              <Tag color={getCategoryColor(selectedNews.category)}>
                {selectedNews.category}
              </Tag>
            </Space>
            <Paragraph>{selectedNews.content}</Paragraph>
            {selectedNews.stock_codes.length > 0 && (
              <div style={{ marginTop: '16px' }}>
                <Text strong>相关股票: </Text>
                <Space>
                  {selectedNews.stock_codes.map(code => (
                    <Tag key={code} color="blue">
                      {code}
                    </Tag>
                  ))}
                </Space>
              </div>
            )}
            <div style={{ marginTop: '16px' }}>
              <Text strong>标签: </Text>
              <Space wrap>
                {selectedNews.tags.map(tag => (
                  <Tag key={tag}>
                    {tag}
                  </Tag>
                ))}
              </Space>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}

export default NewsHub