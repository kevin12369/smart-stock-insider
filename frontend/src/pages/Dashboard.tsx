import React, { useState, useEffect } from 'react'
import {
  Card,
  Row,
  Col,
  Statistic,
  Table,
  Tag,
  Button,
  Space,
  Input,
  message,
  Typography,
  Progress,
  List,
  Avatar,
  Alert,
  Tabs,
  Divider
} from 'antd'
import {
  SearchOutlined,
  ReloadOutlined,
  DatabaseOutlined,
  LineChartOutlined,
  SignalFilled,
  PlusOutlined,
  SettingOutlined,
  ImportOutlined,
  DashboardOutlined,
  TrophyOutlined,
  RiseOutlined,
  FallOutlined,
  BellOutlined,
  PieChartOutlined,
  BarChartOutlined,
  ThunderboltOutlined,
  EyeOutlined
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import type { ColumnsType } from 'antd/es/table'
import apiService, { StockBasicInfo, TechnicalSignal } from '../services/api'

const { Text } = Typography

const { Text, Title } = Typography
const { TabPane } = Tabs

const Dashboard: React.FC = () => {
  const navigate = useNavigate()
  const [systemInfo, setSystemInfo] = useState<any>(null)
  const [stocks, setStocks] = useState<StockBasicInfo[]>([])
  const [signals, setSignals] = useState<TechnicalSignal[]>([])
  const [loading, setLoading] = useState(false)
  const [searchKeyword, setSearchKeyword] = useState('')

  useEffect(() => {
    loadSystemInfo()
    loadStocks()
    loadSignals()
  }, [])

  // 模拟投资组合数据
  const portfolioData = {
    totalValue: 1000000,
    totalReturn: 0.15,
    dailyChange: 0.02,
    activePositions: 8,
    winningPositions: 5
  }

  // 模拟新闻数据
  const latestNews = [
    {
      id: '1',
      title: 'A股三大指数集体收涨',
      source: '同花顺',
      time: '2小时前',
      category: 'market'
    },
    {
      id: '2',
      title: '新能源汽车板块表现强势',
      source: '东方财富',
      time: '3小时前',
      category: 'sector'
    }
  ]

  // 模拟推送数据
  const recentPushes = [
    {
      id: '1',
      type: 'alert',
      title: '平安银行价格预警',
      content: '突破16.50元',
      time: '30分钟前',
      read: true
    },
    {
      id: '2',
      type: 'news',
      title: '重要财经新闻',
      content: '央行发布货币政策报告',
      time: '1小时前',
      read: false
    }
  ]

  const loadSystemInfo = async () => {
    try {
      const response = await apiService.getSystemInfo()
      if (response.success) {
        setSystemInfo(response.data)
      }
    } catch (error) {
      console.error('加载系统信息失败:', error)
    }
  }

  const loadStocks = async (keyword: string = '') => {
    try {
      const response = await apiService.searchStocks(keyword, 10, 0)
      if (response.success) {
        setStocks(response.data.stocks)
      }
    } catch (error) {
      console.error('加载股票列表失败:', error)
    }
  }

  const loadSignals = async () => {
    try {
      const response = await apiService.getTechnicalSignals('000001')
      if (response.success) {
        setSignals(response.data.signals || [])
      }
    } catch (error) {
      console.error('加载技术信号失败:', error)
    }
  }

  const handleSearch = (value: string) => {
    setSearchKeyword(value)
    loadStocks(value)
  }

  const handleBackup = async () => {
    setLoading(true)
    try {
      const response = await apiService.backupData()
      if (response.success) {
        message.success('数据备份成功')
      } else {
        message.error('数据备份失败')
      }
    } catch (error) {
      message.error('数据备份失败')
    } finally {
      setLoading(false)
    }
  }

  const stockColumns: ColumnsType<StockBasicInfo> = [
    {
      title: '股票代码',
      dataIndex: 'code',
      key: 'code',
      render: (text) => <Text strong>{text}</Text>
    },
    {
      title: '股票名称',
      dataIndex: 'name',
      key: 'name'
    },
    {
      title: '行业',
      dataIndex: 'industry',
      key: 'industry',
      render: (text) => <Tag color="blue">{text}</Tag>
    },
    {
      title: '市场',
      dataIndex: 'market',
      key: 'market',
      render: (text) => <Tag color="green">{text}</Tag>
    },
    {
      title: '操作',
      key: 'action',
      render: () => (
        <Space size="middle">
          <Button type="link" size="small">查看详情</Button>
          <Button type="link" size="small">技术分析</Button>
        </Space>
      )
    }
  ]

  const getSignalColor = (strength: string) => {
    switch (strength) {
      case 'STRONG_BUY': return 'green'
      case 'BUY': return 'lime'
      case 'HOLD': return 'orange'
      case 'SELL': return 'red'
      case 'STRONG_SELL': return 'red'
      default: return 'default'
    }
  }

  const getSignalIcon = (strength: string) => {
    if (strength.includes('BUY')) return '📈'
    if (strength.includes('SELL')) return '📉'
    return '➡️'
  }

  return (
    <div style={{ padding: '24px', background: '#f5f5f5', minHeight: '100vh' }}>
      {/* 系统状态卡片 */}
      {systemInfo && (
        <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="系统状态"
                value={systemInfo.status}
                prefix={<DatabaseOutlined />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="股票数量"
                value={systemInfo.database?.stats?.stock_basic || 0}
                prefix={<LineChartOutlined />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="技术信号"
                value={systemInfo.database?.stats?.technical_signals || 0}
                prefix={<SignalFilled />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="数据库大小"
                value={systemInfo.database_size}
                prefix={<DatabaseOutlined />}
              />
            </Card>
          </Col>
        </Row>
      )}

      <Row gutter={[16, 16]}>
        {/* 股票列表 */}
        <Col xs={24} lg={16}>
          <Card
            title="股票列表"
            extra={
              <Space>
                <Input.Search
                  placeholder="搜索股票"
                  style={{ width: 200 }}
                  onSearch={handleSearch}
                  enterButton={<SearchOutlined />}
                />
                <Button icon={<ReloadOutlined />} onClick={() => loadStocks(searchKeyword)}>
                  刷新
                </Button>
                <Button type="primary" icon={<PlusOutlined />}>
                  添加股票
                </Button>
              </Space>
            }
          >
            <Table
              columns={stockColumns}
              dataSource={stocks}
              rowKey="code"
              pagination={false}
              size="small"
            />
          </Card>
        </Col>

        {/* 技术信号 */}
        <Col xs={24} lg={8}>
          <Card
            title="最新技术信号"
            extra={
              <Button icon={<ReloadOutlined />} onClick={loadSignals}>
                刷新
              </Button>
            }
          >
            <List
              dataSource={signals}
              renderItem={(signal) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={
                      <Avatar style={{ backgroundColor: getSignalColor(signal.strength) }}>
                        {getSignalIcon(signal.strength)}
                      </Avatar>
                    }
                    title={
                      <Space>
                        <Text strong>{signal.code}</Text>
                        <Tag color={getSignalColor(signal.strength)}>
                          {signal.strength}
                        </Tag>
                      </Space>
                    }
                    description={
                      <div>
                        <Text type="secondary">{signal.signal_type}</Text>
                        <br />
                        <Text>{signal.description}</Text>
                        <br />
                        <Progress
                          percent={Math.round(signal.confidence * 100)}
                          size="small"
                          style={{ marginTop: '4px' }}
                        />
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>

      {/* 操作按钮 */}
      <Row style={{ marginTop: '24px' }}>
        <Col span={24}>
          <Card title="数据管理">
            <Space size="large">
              <Button
                type="primary"
                icon={<DatabaseOutlined />}
                loading={loading}
                onClick={handleBackup}
              >
                备份数据
              </Button>
              <Button icon={<ReloadOutlined />} onClick={loadSystemInfo}>
                刷新系统信息
              </Button>
              <Button icon={<LineChartOutlined />}>
                信号分析
              </Button>
              <Button
                icon={<SettingOutlined />}
                onClick={() => navigate('/signal-config')}
              >
                信号配置
              </Button>
              <Button
                icon={<DatabaseOutlined />}
                onClick={() => navigate('/data-sync')}
              >
                数据同步
              </Button>
              <Button
                icon={<ImportOutlined />}
                onClick={() => navigate('/data-import-export')}
              >
                导入导出
              </Button>
              <Button
                icon={<DashboardOutlined />}
                onClick={() => navigate('/data-quality')}
              >
                数据质量
              </Button>
              <Button icon={<PlusOutlined />}>
                添加自选股
              </Button>
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Dashboard