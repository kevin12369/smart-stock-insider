import React, { useState, useEffect } from 'react'
import {
  Card,
  Row,
  Col,
  List,
  Tag,
  Button,
  Space,
  Switch,
  Typography,
  Badge,
  Statistic,
  Progress,
  Form,
  Input,
  Select,
  InputNumber,
  TimePicker,
  message,
  Modal,
  Divider,
  Tabs,
  Table,
  Tooltip
} from 'antd'
import {
  BellOutlined,
  SettingOutlined,
  EyeOutlined,
  DeleteOutlined,
  PlusOutlined,
  ReloadOutlined,
  SendOutlined,
  WifiOutlined,
  MobileOutlined,
  DesktopOutlined,
  NotificationOutlined,
  ExclamationCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import dayjs from 'dayjs'
import apiService from '../services/api'

const { Title, Text, Paragraph } = Typography
const { TabPane } = Tabs
const { Option } = Select
const RangePicker = TimePicker.RangePicker

// 推送通知接口定义
interface PushSubscription {
  id: string
  user_id: string
  device_type: string
  device_token: string
  subscriptions: string[]
  enabled: boolean
  preferences: {
    news?: {
      enabled: boolean
      categories: string[]
      frequency: string
      max_per_day: number
    }
    alerts?: {
      enabled: boolean
      types: string[]
      urgency: string[]
    }
    analysis?: {
      enabled: boolean
      reports: string[]
      frequency: string
    }
  }
  is_active: boolean
  last_activity_at: string
  created_at: string
}

interface PushMessage {
  id: string
  type: string
  title: string
  content: string
  summary: string
  url?: string
  category: string
  priority: string
  tags: string[]
  target: {
    user_ids?: string[]
    stock_codes?: string[]
    sectors?: string[]
  }
  data?: any
  created_at: string
  delivered: boolean
  read: boolean
  clicked: boolean
  delivered_at?: string
  read_at?: string
  clicked_at?: string
}

interface PushAnalytics {
  date: string
  total_messages: number
  news_messages: number
  alert_messages: number
  analysis_messages: number
  portfolio_messages: number
  success_rate: number
  read_rate: number
  click_rate: number
  device_breakdown: {
    web: number
    mobile: number
    desktop: number
  }
}

const PushNotification: React.FC = () => {
  const [subscriptions, setSubscriptions] = useState<PushSubscription[]>([])
  const [messages, setMessages] = useState<PushMessage[]>([])
  const [analytics, setAnalytics] = useState<PushAnalytics | null>(null)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('messages')
  const [settingsVisible, setSettingsVisible] = useState(false)
  const [sendModalVisible, setSendModalVisible] = useState(false)
  const [form] = Form.useForm()
  const [settingsForm] = Form.useForm()

  useEffect(() => {
    loadSubscriptions()
    loadMessages()
    loadAnalytics()
  }, [])

  const loadSubscriptions = async () => {
    try {
      setLoading(true)
      // 模拟API调用
      const mockSubscriptions: PushSubscription[] = [
        {
          id: 'sub_001',
          user_id: 'user_001',
          device_type: 'web',
          device_token: 'web_token_abc123',
          subscriptions: ['news', 'alerts', 'analysis'],
          enabled: true,
          preferences: {
            news: {
              enabled: true,
              categories: ['breaking', 'major'],
              frequency: 'realtime',
              max_per_day: 20
            },
            alerts: {
              enabled: true,
              types: ['price', 'volume', 'technical'],
              urgency: ['high', 'critical']
            },
            analysis: {
              enabled: true,
              reports: ['daily', 'weekly'],
              frequency: 'daily'
            }
          },
          is_active: true,
          last_activity_at: new Date().toISOString(),
          created_at: '2024-01-01T10:00:00Z'
        },
        {
          id: 'sub_002',
          user_id: 'user_001',
          device_type: 'mobile',
          device_token: 'mobile_token_def456',
          subscriptions: ['news', 'alerts'],
          enabled: true,
          preferences: {
            news: {
              enabled: true,
              categories: ['breaking', 'major'],
              frequency: 'realtime',
              max_per_day: 15
            },
            alerts: {
              enabled: true,
              types: ['price', 'technical'],
              urgency: ['high', 'critical']
            }
          },
          is_active: true,
          last_activity_at: new Date().toISOString(),
          created_at: '2024-01-05T14:30:00Z'
        }
      ]
      setSubscriptions(mockSubscriptions)
    } catch (error) {
      message.error('加载订阅信息失败')
    } finally {
      setLoading(false)
    }
  }

  const loadMessages = async () => {
    try {
      setLoading(true)
      // 模拟API调用
      const mockMessages: PushMessage[] = [
        {
          id: 'msg_001',
          type: 'news',
          title: '📰 平安银行 重要通知',
          content: '平安银行发布2024年业绩预告，净利润同比增长15%，超出市场预期。',
          summary: '平安银行: 平安银行发布2024年业绩预告',
          url: 'https://example.com/news/001',
          category: '财经',
          priority: 'high',
          tags: ['urgent', 'market'],
          target: {
            user_ids: ['user_001'],
            stock_codes: ['000001'],
            sectors: ['金融']
          },
          data: {
            news_id: 'news_123456',
            importance: 0.9,
            urgency: 'high'
          },
          created_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
          delivered: true,
          read: true,
          clicked: false,
          delivered_at: new Date(Date.now() - 29 * 60 * 1000).toISOString(),
          read_at: new Date(Date.now() - 25 * 60 * 1000).toISOString()
        },
        {
          id: 'msg_002',
          type: 'alert',
          title: '💰 万科A 价格预警',
          content: '当前价格：¥19.50\n目标价格：¥20.00\n变动：+7.14%',
          summary: '万科A: 价格突破19.50元',
          category: 'alert',
          priority: 'medium',
          tags: ['price', 'breakthrough'],
          target: {
            user_ids: ['user_001'],
            stock_codes: ['000002']
          },
          data: {
            stock_code: '000002',
            current_price: 19.50,
            target_price: 20.00,
            change_pct: 0.0714
          },
          created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
          delivered: true,
          read: true,
          clicked: true,
          delivered_at: new Date(Date.now() - 1.9 * 60 * 60 * 1000).toISOString(),
          read_at: new Date(Date.now() - 1.8 * 60 * 60 * 1000).toISOString(),
          clicked_at: new Date(Date.now() - 1.5 * 60 * 60 * 1000).toISOString()
        }
      ]
      setMessages(mockMessages)
    } catch (error) {
      message.error('加载推送消息失败')
    } finally {
      setLoading(false)
    }
  }

  const loadAnalytics = async () => {
    try {
      // 模拟API调用
      const mockAnalytics: PushAnalytics = {
        date: new Date().toISOString().split('T')[0],
        total_messages: 1250,
        news_messages: 800,
        alert_messages: 300,
        analysis_messages: 100,
        portfolio_messages: 50,
        success_rate: 0.92,
        read_rate: 0.45,
        click_rate: 0.12,
        device_breakdown: {
          web: 400,
          mobile: 300,
          desktop: 150
        }
      }
      setAnalytics(mockAnalytics)
    } catch (error) {
      console.error('加载分析数据失败:', error)
    }
  }

  const handleSendMessage = async (values: any) => {
    try {
      setLoading(true)
      console.log('发送推送消息:', values)
      message.success('推送消息发送成功')
      setSendModalVisible(false)
      form.resetFields()
      loadMessages()
    } catch (error) {
      message.error('发送推送消息失败')
    } finally {
      setLoading(false)
    }
  }

  const handleUpdateSettings = async (values: any) => {
    try {
      setLoading(true)
      console.log('更新推送设置:', values)
      message.success('推送设置更新成功')
      setSettingsVisible(false)
      settingsForm.resetFields()
      loadSubscriptions()
    } catch (error) {
      message.error('更新推送设置失败')
    } finally {
      setLoading(false)
    }
  }

  const handleToggleSubscription = async (subscriptionId: string, enabled: boolean) => {
    try {
      console.log('切换订阅状态:', subscriptionId, enabled)
      message.success('订阅状态更新成功')
      loadSubscriptions()
    } catch (error) {
      message.error('更新订阅状态失败')
    }
  }

  const getDeviceIcon = (deviceType: string) => {
    const iconMap: Record<string, React.ReactNode> = {
      'web': <DesktopOutlined />,
      'mobile': <MobileOutlined />,
      'desktop': <DesktopOutlined />
    }
    return iconMap[deviceType] || <WifiOutlined />
  }

  const getPriorityColor = (priority: string) => {
    const colorMap: Record<string, string> = {
      'high': 'red',
      'medium': 'orange',
      'low': 'blue'
    }
    return colorMap[priority] || 'default'
  }

  const getStatusIcon = (message: PushMessage) => {
    if (message.clicked) return <CheckCircleOutlined style={{ color: '#52c41a' }} />
    if (message.read) return <EyeOutlined style={{ color: '#1890ff' }} />
    if (message.delivered) return <CheckCircleOutlined style={{ color: '#52c41a' }} />
    return <ClockCircleOutlined style={{ color: '#d9d9d9' }} />
  }

  const messageColumns: ColumnsType<PushMessage> = [
    {
      title: '状态',
      dataIndex: 'delivered',
      key: 'status',
      width: 80,
      render: (_, record) => (
        <Tooltip title={getStatusIcon(record)}>
          {getStatusIcon(record)}
        </Tooltip>
      )
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 100,
      render: (type) => {
        const typeMap: Record<string, { color: string; text: string }> = {
          'news': { color: 'blue', text: '新闻' },
          'alert': { color: 'orange', text: '预警' },
          'analysis': { color: 'green', text: '分析' },
          'portfolio': { color: 'purple', text: '组合' }
        }
        const typeInfo = typeMap[type]
        return <Tag color={typeInfo.color}>{typeInfo.text}</Tag>
      }
    },
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true
    },
    {
      title: '摘要',
      dataIndex: 'summary',
      key: 'summary',
      ellipsis: true
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      width: 100,
      render: (priority) => (
        <Tag color={getPriorityColor(priority)}>
          {priority === 'high' ? '高' : priority === 'medium' ? '中' : '低'}
        </Tag>
      )
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (time) => new Date(time).toLocaleString()
    }
  ]

  return (
    <div style={{ padding: '24px', background: '#f5f5f5', minHeight: '100vh' }}>
      <Title level={2} style={{ marginBottom: '24px' }}>
        <BellOutlined /> 推送通知中心
      </Title>

      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane tab="推送消息" key="messages">
          <Card
            title="消息列表"
            extra={
              <Space>
                <Button icon={<ReloadOutlined />} onClick={loadMessages} loading={loading}>
                  刷新
                </Button>
                <Button type="primary" icon={<SendOutlined />} onClick={() => setSendModalVisible(true)}>
                  发送消息
                </Button>
              </Space>
            }
          >
            <Table
              columns={messageColumns}
              dataSource={messages}
              rowKey="id"
              loading={loading}
              pagination={{
                pageSize: 20,
                showSizeChanger: true,
                showQuickJumper: true
              }}
            />
          </Card>
        </TabPane>

        <TabPane tab="订阅管理" key="subscriptions">
          <Card
            title="设备订阅"
            extra={
              <Space>
                <Button icon={<ReloadOutlined />} onClick={loadSubscriptions} loading={loading}>
                  刷新
                </Button>
                <Button icon={<SettingOutlined />} onClick={() => setSettingsVisible(true)}>
                  推送设置
                </Button>
              </Space>
            }
          >
            <List
              dataSource={subscriptions}
              renderItem={(subscription) => (
                <List.Item
                  style={{
                    padding: '16px',
                    borderRadius: '8px',
                    marginBottom: '12px',
                    backgroundColor: '#fff',
                    border: '1px solid #f0f0f0'
                  }}
                  actions={[
                    <Switch
                      checked={subscription.enabled}
                      onChange={(checked) => handleToggleSubscription(subscription.id, checked)}
                    />,
                    <Button type="link" icon={<SettingOutlined />}>
                      配置
                    </Button>,
                    <Button type="link" danger icon={<DeleteOutlined />}>
                      删除
                    </Button>
                  ]}
                >
                  <List.Item.Meta
                    avatar={
                      <Avatar
                        style={{ backgroundColor: subscription.is_active ? '#52c41a' : '#d9d9d9' }}
                        icon={getDeviceIcon(subscription.device_type)}
                      />
                    }
                    title={
                      <Space>
                        <Text strong>
                          {subscription.device_type === 'web' ? 'Web端' :
                           subscription.device_type === 'mobile' ? '移动端' : '桌面端'}
                        </Text>
                        <Badge
                          status={subscription.is_active ? 'success' : 'default'}
                          text={subscription.is_active ? '活跃' : '非活跃'}
                        />
                      </Space>
                    }
                    description={
                      <Space direction="vertical" style={{ width: '100%' }}>
                        <Text type="secondary">
                          订阅类型: {subscription.subscriptions.join(', ')}
                        </Text>
                        <Text type="secondary">
                          最后活跃: {new Date(subscription.last_activity_at).toLocaleString()}
                        </Text>
                        {subscription.preferences.news && (
                          <div>
                            <Text strong>新闻推送: </Text>
                            <Text type="secondary">
                              {subscription.preferences.news.categories.join(', ')} |
                              {subscription.preferences.news.frequency} |
                              最多{subscription.preferences.news.max_per_day}条/天
                            </Text>
                          </div>
                        )}
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </TabPane>

        <TabPane tab="统计分析" key="analytics">
          {analytics && (
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={12} md={6}>
                <Card>
                  <Statistic
                    title="总推送数"
                    value={analytics.total_messages}
                    prefix={<NotificationOutlined />}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Card>
                  <Statistic
                    title="送达率"
                    value={analytics.success_rate * 100}
                    precision={1}
                    suffix="%"
                    prefix={<CheckCircleOutlined />}
                    valueStyle={{ color: analytics.success_rate > 0.9 ? '#3f8600' : '#cf1322' }}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Card>
                  <Statistic
                    title="阅读率"
                    value={analytics.read_rate * 100}
                    precision={1}
                    suffix="%"
                    prefix={<EyeOutlined />}
                    valueStyle={{ color: analytics.read_rate > 0.5 ? '#3f8600' : '#faad14' }}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Card>
                  <Statistic
                    title="点击率"
                    value={analytics.click_rate * 100}
                    precision={1}
                    suffix="%"
                    prefix={<BellOutlined />}
                    valueStyle={{ color: analytics.click_rate > 0.1 ? '#3f8600' : '#faad14' }}
                  />
                </Card>
              </Col>

              <Col xs={24} lg={12}>
                <Card title="消息类型分布">
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <div>
                      <Text>新闻消息: </Text>
                      <Progress
                        percent={(analytics.news_messages / analytics.total_messages) * 100}
                        status="active"
                        showInfo={false}
                        strokeColor="#1890ff"
                        style={{ width: '200px' }}
                      />
                      <Text style={{ marginLeft: '8px' }}>
                        {analytics.news_messages}条 ({((analytics.news_messages / analytics.total_messages) * 100).toFixed(1)}%)
                      </Text>
                    </div>
                    <div>
                      <Text>预警消息: </Text>
                      <Progress
                        percent={(analytics.alert_messages / analytics.total_messages) * 100}
                        status="active"
                        showInfo={false}
                        strokeColor="#faad14"
                        style={{ width: '200px' }}
                      />
                      <Text style={{ marginLeft: '8px' }}>
                        {analytics.alert_messages}条 ({((analytics.alert_messages / analytics.total_messages) * 100).toFixed(1)}%)
                      </Text>
                    </div>
                    <div>
                      <Text>分析消息: </Text>
                      <Progress
                        percent={(analytics.analysis_messages / analytics.total_messages) * 100}
                        status="active"
                        showInfo={false}
                        strokeColor="#52c41a"
                        style={{ width: '200px' }}
                      />
                      <Text style={{ marginLeft: '8px' }}>
                        {analytics.analysis_messages}条 ({((analytics.analysis_messages / analytics.total_messages) * 100).toFixed(1)}%)
                      </Text>
                    </div>
                    <div>
                      <Text>组合消息: </Text>
                      <Progress
                        percent={(analytics.portfolio_messages / analytics.total_messages) * 100}
                        status="active"
                        showInfo={false}
                        strokeColor="#722ed1"
                        style={{ width: '200px' }}
                      />
                      <Text style={{ marginLeft: '8px' }}>
                        {analytics.portfolio_messages}条 ({((analytics.portfolio_messages / analytics.total_messages) * 100).toFixed(1)}%)
                      </Text>
                    </div>
                  </Space>
                </Card>
              </Col>

              <Col xs={24} lg={12}>
                <Card title="设备分布">
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <div>
                      <Text><DesktopOutlined /> Web端: </Text>
                      <Progress
                        percent={(analytics.device_breakdown.web / (analytics.device_breakdown.web + analytics.device_breakdown.mobile + analytics.device_breakdown.desktop)) * 100}
                        status="active"
                        showInfo={false}
                        strokeColor="#1890ff"
                        style={{ width: '200px' }}
                      />
                      <Text style={{ marginLeft: '8px' }}>
                        {analytics.device_breakdown.web}台
                      </Text>
                    </div>
                    <div>
                      <Text><MobileOutlined /> 移动端: </Text>
                      <Progress
                        percent={(analytics.device_breakdown.mobile / (analytics.device_breakdown.web + analytics.device_breakdown.mobile + analytics.device_breakdown.desktop)) * 100}
                        status="active"
                        showInfo={false}
                        strokeColor="#52c41a"
                        style={{ width: '200px' }}
                      />
                      <Text style={{ marginLeft: '8px' }}>
                        {analytics.device_breakdown.mobile}台
                      </Text>
                    </div>
                    <div>
                      <Text><DesktopOutlined /> 桌面端: </Text>
                      <Progress
                        percent={(analytics.device_breakdown.desktop / (analytics.device_breakdown.web + analytics.device_breakdown.mobile + analytics.device_breakdown.desktop)) * 100}
                        status="active"
                        showInfo={false}
                        strokeColor="#722ed1"
                        style={{ width: '200px' }}
                      />
                      <Text style={{ marginLeft: '8px' }}>
                        {analytics.device_breakdown.desktop}台
                      </Text>
                    </div>
                  </Space>
                </Card>
              </Col>
            </Row>
          )}
        </TabPane>
      </Tabs>

      {/* 发送消息模态框 */}
      <Modal
        title="发送推送消息"
        open={sendModalVisible}
        onCancel={() => setSendModalVisible(false)}
        onOk={() => form.submit()}
        confirmLoading={loading}
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={handleSendMessage}>
          <Form.Item
            name="type"
            label="消息类型"
            rules={[{ required: true, message: '请选择消息类型' }]}
          >
            <Select placeholder="选择消息类型">
              <Option value="news">新闻</Option>
              <Option value="alert">预警</Option>
              <Option value="analysis">分析</Option>
              <Option value="portfolio">投资组合</Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="title"
            label="消息标题"
            rules={[{ required: true, message: '请输入消息标题' }]}
          >
            <Input placeholder="请输入消息标题" />
          </Form.Item>
          <Form.Item
            name="content"
            label="消息内容"
            rules={[{ required: true, message: '请输入消息内容' }]}
          >
            <Input.TextArea rows={4} placeholder="请输入消息内容" />
          </Form.Item>
          <Form.Item name="url" label="链接地址">
            <Input placeholder="可选：点击消息后跳转的链接" />
          </Form.Item>
          <Form.Item
            name="priority"
            label="优先级"
            rules={[{ required: true, message: '请选择优先级' }]}
          >
            <Select placeholder="选择优先级">
              <Option value="high">高</Option>
              <Option value="medium">中</Option>
              <Option value="low">低</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* 推送设置模态框 */}
      <Modal
        title="推送设置"
        open={settingsVisible}
        onCancel={() => setSettingsVisible(false)}
        onOk={() => settingsForm.submit()}
        confirmLoading={loading}
        width={600}
      >
        <Form form={settingsForm} layout="vertical" onFinish={handleUpdateSettings}>
          <Form.Item label="新闻推送设置">
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item name={['news', 'enabled']} valuePropName="checked">
                  <Switch checkedChildren="启用" unCheckedChildren="禁用" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name={['news', 'frequency']}>
                  <Select placeholder="推送频率">
                    <Option value="realtime">实时</Option>
                    <Option value="hourly">每小时</Option>
                    <Option value="daily">每日</Option>
                  </Select>
                </Form.Item>
              </Col>
            </Row>
          </Form.Item>
          <Form.Item label="预警推送设置">
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item name={['alerts', 'enabled']} valuePropName="checked">
                  <Switch checkedChildren="启用" unCheckedChildren="禁用" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name={['alerts', 'min_urgency']}>
                  <Select placeholder="最低紧急程度">
                    <Option value="low">低</Option>
                    <Option value="medium">中</Option>
                    <Option value="high">高</Option>
                    <Option value="critical">紧急</Option>
                  </Select>
                </Form.Item>
              </Col>
            </Row>
          </Form.Item>
          <Form.Item label="勿扰时段">
            <Form.Item name="quiet_hours">
              <RangePicker
                format="HH:mm"
                placeholder={['开始时间', '结束时间']}
              />
            </Form.Item>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default PushNotification