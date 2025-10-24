import React, { useState, useEffect } from 'react'
import {
  Card,
  Row,
  Col,
  Statistic,
  List,
  Tag,
  Button,
  Space,
  Typography,
  Progress,
  Avatar,
  Alert,
  Tabs,
  Divider,
  Badge,
  Tooltip
} from 'antd'
import {
  DashboardOutlined,
  TrophyOutlined,
  RiseOutlined,
  FallOutlined,
  LineChartOutlined,
  PieChartOutlined,
  BellOutlined,
  ThunderboltOutlined,
  EyeOutlined,
  ReloadOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
  FireOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'

const { Title, Text, Paragraph } = Typography
const { TabPane } = Tabs

interface DashboardCard {
  title: string
  value: string | number
  prefix?: React.ReactNode
  suffix?: string
  trend?: 'up' | 'down' | 'stable'
  trendValue?: number
  color?: string
  icon?: React.ReactNode
  onClick?: () => void
}

const EnhancedDashboard: React.FC = () => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [currentTime, setCurrentTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  // 模拟数据
  const systemStats = {
    status: '运行正常',
    uptime: '15天 8小时',
    totalStocks: 5234,
    totalSignals: 15678,
    dailyActiveUsers: 892,
    apiCalls: 45678
  }

  const portfolioOverview = {
    totalValue: 1250000,
    dailyChange: 12500,
    dailyChangePercent: 1.01,
    totalReturn: 0.186,
    sharpeRatio: 1.35,
    maxDrawdown: -0.082,
    winRate: 0.68,
    activePositions: 12,
    topPerformer: '贵州茅台',
    worstPerformer: '某科技股'
  }

  const marketOverview = {
    shIndex: { value: 3089.45, change: 37.28, changePercent: 1.22 },
    szIndex: { value: 10245.67, change: 152.34, changePercent: 1.51 },
    cyIndex: { value: 1958.32, change: 35.67, changePercent: 1.85 },
    totalMarketCap: '85.6万亿',
    turnover: '8234亿'
  }

  const latestNews = [
    {
      id: '1',
      title: '央行降准0.25个百分点，释放流动性约5000亿元',
      summary: '中国人民银行宣布下调金融机构存款准备金率0.25个百分点',
      source: '央行官网',
      category: 'policy',
      priority: 'high',
      time: '10分钟前',
      impact: 'positive',
      tags: ['货币政策', '降准', '流动性']
    },
    {
      id: '2',
      title: '新能源汽车销量创历史新高，板块龙头集体涨停',
      summary: '10月份新能源汽车销量同比增长45%，产业链公司股价大涨',
      source: '同花顺',
      category: 'industry',
      priority: 'medium',
      time: '25分钟前',
      impact: 'positive',
      tags: ['新能源汽车', '销量', '涨停']
    },
    {
      id: '3',
      title: '某知名房企债务违约引发市场担忧',
      summary: '知名房地产企业未能按期偿还美元债，信用评级遭下调',
      source: '财联社',
      category: 'company',
      priority: 'high',
      time: '1小时前',
      impact: 'negative',
      tags: ['房地产', '债务违约', '信用评级']
    }
  ]

  const activeAlerts = [
    {
      id: '1',
      type: 'price',
      title: '平安银行突破关键阻力位',
      content: '平安银行股价突破16.80元，建议关注后续走势',
      stockCode: '000001',
      stockName: '平安银行',
      priority: 'medium',
      time: '5分钟前'
    },
    {
      id: '2',
      type: 'volume',
      title: '某科技股异常放量',
      content: '成交量达到均值的3倍，可能有重大消息',
      stockCode: '000002',
      stockName: '万科A',
      priority: 'high',
      time: '15分钟前'
    }
  ]

  const systemNotifications = [
    {
      id: '1',
      type: 'info',
      title: '数据同步完成',
      content: '已成功同步5234只股票的最新数据',
      time: '2小时前',
      read: true
    },
    {
      id: '2',
      type: 'warning',
      title: 'API调用频率接近限制',
      content: '当前API调用频率已达限额的85%，请注意控制调用频率',
      time: '30分钟前',
      read: false
    }
  ]

  const getMarketColor = (value: number) => {
    return value >= 0 ? '#3f8600' : '#cf1322'
  }

  const getPriorityColor = (priority: string) => {
    const colorMap: Record<string, string> = {
      'high': 'red',
      'medium': 'orange',
      'low': 'blue'
    }
    return colorMap[priority] || 'default'
  }

  const getImpactColor = (impact: string) => {
    const colorMap: Record<string, string> = {
      'positive': '#52c41a',
      'negative': '#ff4d4f',
      'neutral': '#faad14'
    }
    return colorMap[impact] || 'default'
  }

  const quickActions = [
    {
      title: '投资组合管理',
      description: '查看和管理投资组合',
      icon: <PieChartOutlined />,
      color: '#1890ff',
      onClick: () => navigate('/portfolio')
    },
    {
      title: '组合分析',
      description: '深度分析投资组合表现',
      icon: <LineChartOutlined />,
      color: '#52c41a',
      onClick: () => navigate('/portfolio-analysis')
    },
    {
      title: '新闻中心',
      description: '浏览最新财经新闻',
      icon: <ThunderboltOutlined />,
      color: '#faad14',
      onClick: () => navigate('/news')
    },
    {
      title: '推送设置',
      description: '管理消息推送偏好',
      icon: <BellOutlined />,
      color: '#722ed1',
      onClick: () => navigate('/push')
    }
  ]

  return (
    <div style={{ padding: '24px', background: '#f5f5f5', minHeight: '100vh' }}>
      {/* 页面标题 */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <Title level={2} style={{ margin: 0 }}>
          <DashboardOutlined /> 智股通控制台
        </Title>
        <Space>
          <Text type="secondary">
            {currentTime.toLocaleString()}
          </Text>
          <Button icon={<ReloadOutlined />} onClick={() => window.location.reload()}>
            刷新数据
          </Button>
        </Space>
      </div>

      {/* 系统状态提醒 */}
      {systemNotifications.some(n => !n.read) && (
        <Alert
          message="您有未读的系统通知"
          description="请查看系统通知了解重要信息"
          type="warning"
          showIcon
          closable
          style={{ marginBottom: '24px' }}
        />
      )}

      {/* 快捷操作 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        {quickActions.map((action, index) => (
          <Col xs={24} sm={12} md={6} key={index}>
            <Card
              hoverable
              style={{
                cursor: 'pointer',
                borderTop: `4px solid ${action.color}`,
                transition: 'all 0.3s ease'
              }}
              onClick={action.onClick}
              bodyStyle={{ padding: '20px' }}
            >
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '32px', color: action.color, marginBottom: '12px' }}>
                  {action.icon}
                </div>
                <Title level={5} style={{ margin: '0 0 8px 0', color: '#262626' }}>
                  {action.title}
                </Title>
                <Text type="secondary" style={{ fontSize: '14px' }}>
                  {action.description}
                </Text>
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      {/* 主要数据概览 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} lg={16}>
          <Row gutter={[16, 16]}>
            <Col xs={24} sm={12} md={8}>
              <Card>
                <Statistic
                  title="投资组合总值"
                  value={portfolioOverview.totalValue}
                  prefix="¥"
                  precision={0}
                  valueStyle={{ color: '#3f8600' }}
                />
                <div style={{ marginTop: '8px' }}>
                  <Space split={<Divider type="vertical" />}>
                    <Text type="success">
                      <ArrowUpOutlined /> +¥{portfolioOverview.dailyChange.toLocaleString()}
                    </Text>
                    <Text type="success">
                      <ArrowUpOutlined /> +{(portfolioOverview.dailyChangePercent * 100).toFixed(2)}%
                    </Text>
                  </Space>
                </div>
              </Card>
            </Col>
            <Col xs={24} sm={12} md={8}>
              <Card>
                <Statistic
                  title="总收益率"
                  value={portfolioOverview.totalReturn * 100}
                  precision={2}
                  suffix="%"
                  valueStyle={{ color: portfolioOverview.totalReturn >= 0 ? '#3f8600' : '#cf1322' }}
                />
                <div style={{ marginTop: '8px' }}>
                  <Text>夏普比率: {portfolioOverview.sharpeRatio}</Text>
                </div>
              </Card>
            </Col>
            <Col xs={24} sm={12} md={8}>
              <Card>
                <Statistic
                  title="胜率"
                  value={portfolioOverview.winRate * 100}
                  precision={1}
                  suffix="%"
                  valueStyle={{ color: '#1890ff' }}
                />
                <div style={{ marginTop: '8px' }}>
                  <Text>活跃持仓: {portfolioOverview.activePositions}个</Text>
                </div>
              </Card>
            </Col>
          </Row>

          {/* 市场概览 */}
          <Card title="市场概览" style={{ marginTop: '16px' }}>
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={8}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Text strong>上证指数</Text>
                  <div>
                    <Text style={{ fontSize: '18px', fontWeight: 'bold' }}>
                      {marketOverview.shIndex.value}
                    </Text>
                    <Text style={{ color: getMarketColor(marketOverview.shIndex.change), marginLeft: '8px' }}>
                      {marketOverview.shIndex.change >= 0 ? '+' : ''}{marketOverview.shIndex.change}
                      ({marketOverview.shIndex.changePercent >= 0 ? '+' : ''}{marketOverview.shIndex.changePercent}%)
                    </Text>
                  </div>
                </Space>
              </Col>
              <Col xs={24} sm={8}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Text strong>深证成指</Text>
                  <div>
                    <Text style={{ fontSize: '18px', fontWeight: 'bold' }}>
                      {marketOverview.szIndex.value}
                    </Text>
                    <Text style={{ color: getMarketColor(marketOverview.szIndex.change), marginLeft: '8px' }}>
                      {marketOverview.szIndex.change >= 0 ? '+' : ''}{marketOverview.szIndex.change}
                      ({marketOverview.szIndex.changePercent >= 0 ? '+' : ''}{marketOverview.szIndex.changePercent}%)
                    </Text>
                  </div>
                </Space>
              </Col>
              <Col xs={24} sm={8}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Text strong>创业板指</Text>
                  <div>
                    <Text style={{ fontSize: '18px', fontWeight: 'bold' }}>
                      {marketOverview.cyIndex.value}
                    </Text>
                    <Text style={{ color: getMarketColor(marketOverview.cyIndex.change), marginLeft: '8px' }}>
                      {marketOverview.cyIndex.change >= 0 ? '+' : ''}{marketOverview.cyIndex.change}
                      ({marketOverview.cyIndex.changePercent >= 0 ? '+' : ''}{marketOverview.cyIndex.changePercent}%)
                    </Text>
                  </div>
                </Space>
              </Col>
            </Row>
          </Card>
        </Col>

        <Col xs={24} lg={8}>
          <Tabs defaultActiveKey="alerts">
            <TabPane tab="活跃预警" key="alerts" badge={<Badge count={activeAlerts.length} />}>
              <List
                size="small"
                dataSource={activeAlerts}
                renderItem={(alert) => (
                  <List.Item style={{ padding: '12px 0', cursor: 'pointer' }}>
                    <List.Item.Meta
                      avatar={
                        <Avatar
                          style={{
                            backgroundColor: getPriorityColor(alert.priority)
                          }}
                          icon={<ExclamationCircleOutlined />}
                        />
                      }
                      title={
                        <Space>
                          <Text strong style={{ fontSize: '14px' }}>
                            {alert.title}
                          </Text>
                          <Tag color={getPriorityColor(alert.priority)} size="small">
                            {alert.priority === 'high' ? '高' : '中'}
                          </Tag>
                        </Space>
                      }
                      description={
                        <Space direction="vertical" style={{ width: '100%' }}>
                          <Text type="secondary">{alert.content}</Text>
                          <Text type="secondary" style={{ fontSize: '12px' }}>
                            {alert.stockCode} | {alert.time}
                          </Text>
                        </Space>
                      }
                    />
                  </List.Item>
                )}
              />
            </TabPane>
            <TabPane tab="系统通知" key="notifications" badge={<Badge count={systemNotifications.filter(n => !n.read).length} />}>
              <List
                size="small"
                dataSource={systemNotifications}
                renderItem={(notification) => (
                  <List.Item style={{ padding: '12px 0', cursor: 'pointer' }}>
                    <List.Item.Meta
                      avatar={
                        <Avatar
                          style={{
                            backgroundColor: notification.type === 'warning' ? '#faad14' : '#1890ff'
                          }}
                          icon={<BellOutlined />}
                        />
                      }
                      title={
                        <Space>
                          <Text strong style={{ fontSize: '14px' }}>
                            {notification.title}
                          </Text>
                          {!notification.read && (
                            <Badge status="processing" />
                          )}
                        </Space>
                      }
                      description={
                        <Space direction="vertical" style={{ width: '100%' }}>
                          <Text type="secondary">{notification.content}</Text>
                          <Text type="secondary" style={{ fontSize: '12px' }}>
                            {notification.time}
                          </Text>
                        </Space>
                      }
                    />
                  </List.Item>
                )}
              />
            </TabPane>
          </Tabs>
        </Col>
      </Row>

      {/* 最新新闻 */}
      <Card
        title={
          <Space>
            <ThunderboltOutlined />
            最新财经要闻
            <Button type="link" size="small" onClick={() => navigate('/news')}>
              查看更多
            </Button>
          </Space>
        }
        extra={
          <Tooltip title="自动聚合来自多个新闻源的财经要闻">
            <FireOutlined style={{ color: '#ff4d4f' }} />
          </Tooltip>
        }
      >
        <List
          dataSource={latestNews}
          renderItem={(news) => (
            <List.Item
              style={{
                padding: '16px',
                borderRadius: '8px',
                marginBottom: '8px',
                backgroundColor: '#fafafa',
                border: '1px solid #f0f0f0',
                cursor: 'pointer'
              }}
              actions={[
                <Button type="link" size="small" icon={<EyeOutlined />}>
                  查看详情
                </Button>
              ]}
            >
              <List.Item.Meta
                avatar={
                  <Avatar
                    style={{ backgroundColor: getPriorityColor(news.priority) }}
                  />
                }
                title={
                  <Space>
                    <Text strong>{news.title}</Text>
                    <Tag color={getImpactColor(news.impact)} size="small">
                      {news.impact === 'positive' ? '利好' :
                       news.impact === 'negative' ? '利空' : '中性'}
                    </Tag>
                    {news.priority === 'high' && (
                      <Tag color="red" size="small">
                        重要
                      </Tag>
                    )}
                  </Space>
                }
                description={
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <Text type="secondary">{news.summary}</Text>
                    <Space split={<Divider type="vertical" />}>
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        {news.source}
                      </Text>
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        {news.time}
                      </Text>
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        {news.category}
                      </Text>
                    </Space>
                    <div style={{ marginTop: '4px' }}>
                      {news.tags.map(tag => (
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
        />
      </Card>
    </div>
  )
}

export default EnhancedDashboard