import React, { useState, useEffect } from 'react'
import {
  Card,
  Row,
  Col,
  Table,
  Button,
  Space,
  Tag,
  Typography,
  Modal,
  Form,
  Input,
  InputNumber,
  Select,
  message,
  Tabs,
  Statistic
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
  TrophyOutlined,
  DollarOutlined,
  RiseOutlined,
  FallOutlined,
  LineChartOutlined
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'

const { Title, Text } = Typography
const { TabPane } = Tabs
const { Option } = Select

// 投资组合接口定义
interface Portfolio {
  id: string
  user_id: string
  name: string
  description: string
  total_value: number
  cash_amount: number
  currency: string
  risk_level: string
  created_at: string
  updated_at: string
}

interface Position {
  id: string
  portfolio_id: string
  stock_code: string
  stock_name: string
  quantity: number
  avg_cost: number
  current_price: number
  market_value: number
  unrealized_pnl: number
  unrealized_pct: number
  weight: number
  sector: string
  industry: string
  created_at: string
}

interface Transaction {
  id: string
  portfolio_id: string
  position_id: string
  stock_code: string
  stock_name: string
  transaction_type: string
  quantity: number
  price: number
  amount: number
  fee: number
  tax: number
  executed_at: string
  created_at: string
}

const PortfolioManager: React.FC = () => {
  const [portfolios, setPortfolios] = useState<Portfolio[]>([])
  const [positions, setPositions] = useState<Position[]>([])
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [selectedPortfolio, setSelectedPortfolio] = useState<Portfolio | null>(null)
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [positionModalVisible, setPositionModalVisible] = useState(false)
  const [activeTab, setActiveTab] = useState('portfolios')
  const [form] = Form.useForm()
  const [positionForm] = Form.useForm()

  useEffect(() => {
    loadPortfolios()
  }, [])

  const loadPortfolios = async () => {
    try {
      setLoading(true)
      // 模拟API调用
      const mockPortfolios: Portfolio[] = [
        {
          id: 'portfolio_001',
          user_id: 'user_001',
          name: '智股通组合',
          description: '精选价值股组合',
          total_value: 1000000,
          cash_amount: 50000,
          currency: 'CNY',
          risk_level: 'moderate',
          created_at: '2024-01-01 10:00:00',
          updated_at: '2024-01-15 15:30:00'
        },
        {
          id: 'portfolio_002',
          user_id: 'user_001',
          name: '成长股组合',
          description: '高成长科技股组合',
          total_value: 500000,
          cash_amount: 25000,
          currency: 'CNY',
          risk_level: 'high',
          created_at: '2024-01-05 09:00:00',
          updated_at: '2024-01-15 14:20:00'
        }
      ]
      setPortfolios(mockPortfolios)
    } catch (error) {
      message.error('加载投资组合失败')
    } finally {
      setLoading(false)
    }
  }

  const loadPositions = async (portfolioId: string) => {
    try {
      setLoading(true)
      // 模拟API调用
      const mockPositions: Position[] = [
        {
          id: 'position_001',
          portfolio_id: portfolioId,
          stock_code: '000001',
          stock_name: '平安银行',
          quantity: 1000,
          avg_cost: 15.50,
          current_price: 16.80,
          market_value: 16800,
          unrealized_pnl: 1300,
          unrealized_pct: 0.084,
          weight: 0.0168,
          sector: '金融',
          industry: '银行',
          created_at: '2024-01-10 09:30:00'
        },
        {
          id: 'position_002',
          portfolio_id: portfolioId,
          stock_code: '000002',
          stock_name: '万科A',
          quantity: 500,
          avg_cost: 18.20,
          current_price: 19.50,
          market_value: 9750,
          unrealized_pnl: 650,
          unrealized_pct: 0.071,
          weight: 0.0098,
          sector: '房地产',
          industry: '房地产开发',
          created_at: '2024-01-08 14:15:00'
        }
      ]
      setPositions(mockPositions)
    } catch (error) {
      message.error('加载持仓信息失败')
    } finally {
      setLoading(false)
    }
  }

  const loadTransactions = async (portfolioId: string) => {
    try {
      setLoading(true)
      // 模拟API调用
      const mockTransactions: Transaction[] = [
        {
          id: 'transaction_001',
          portfolio_id: portfolioId,
          position_id: 'position_001',
          stock_code: '000001',
          stock_name: '平安银行',
          transaction_type: 'buy',
          quantity: 1000,
          price: 15.50,
          amount: 15500,
          fee: 7.75,
          tax: 0,
          executed_at: '2024-01-10 09:30:00',
          created_at: '2024-01-10 09:30:00'
        },
        {
          id: 'transaction_002',
          portfolio_id: portfolioId,
          position_id: 'position_002',
          stock_code: '000002',
          stock_name: '万科A',
          transaction_type: 'buy',
          quantity: 500,
          price: 18.20,
          amount: 9100,
          fee: 4.55,
          tax: 0,
          executed_at: '2024-01-08 14:15:00',
          created_at: '2024-01-08 14:15:00'
        }
      ]
      setTransactions(mockTransactions)
    } catch (error) {
      message.error('加载交易记录失败')
    } finally {
      setLoading(false)
    }
  }

  const handlePortfolioSelect = (portfolio: Portfolio) => {
    setSelectedPortfolio(portfolio)
    loadPositions(portfolio.id)
    loadTransactions(portfolio.id)
  }

  const handleCreatePortfolio = async (values: any) => {
    try {
      setLoading(true)
      console.log('创建投资组合:', values)
      message.success('投资组合创建成功')
      setModalVisible(false)
      form.resetFields()
      loadPortfolios()
    } catch (error) {
      message.error('创建投资组合失败')
    } finally {
      setLoading(false)
    }
  }

  const handleAddPosition = async (values: any) => {
    try {
      setLoading(true)
      console.log('添加持仓:', values)
      message.success('持仓添加成功')
      setPositionModalVisible(false)
      positionForm.resetFields()
      if (selectedPortfolio) {
        loadPositions(selectedPortfolio.id)
      }
    } catch (error) {
      message.error('添加持仓失败')
    } finally {
      setLoading(false)
    }
  }

  const portfolioColumns: ColumnsType<Portfolio> = [
    {
      title: '组合名称',
      dataIndex: 'name',
      key: 'name',
      render: (text) => <Text strong>{text}</Text>
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true
    },
    {
      title: '总价值',
      dataIndex: 'total_value',
      key: 'total_value',
      render: (value) => `¥${value.toLocaleString()}`
    },
    {
      title: '现金',
      dataIndex: 'cash_amount',
      key: 'cash_amount',
      render: (value) => `¥${value.toLocaleString()}`
    },
    {
      title: '风险等级',
      dataIndex: 'risk_level',
      key: 'risk_level',
      render: (level) => {
        const colorMap: Record<string, string> = {
          'low': 'green',
          'moderate': 'orange',
          'high': 'red',
          'very_high': 'red'
        }
        const textMap: Record<string, string> = {
          'low': '低风险',
          'moderate': '中风险',
          'high': '高风险',
          'very_high': '极高风险'
        }
        return <Tag color={colorMap[level]}>{textMap[level]}</Tag>
      }
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (time) => new Date(time).toLocaleDateString()
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Button type="link" size="small" onClick={() => handlePortfolioSelect(record)}>
            查看详情
          </Button>
          <Button type="link" size="small" icon={<EditOutlined />}>
            编辑
          </Button>
          <Button type="link" size="small" danger icon={<DeleteOutlined />}>
            删除
          </Button>
        </Space>
      )
    }
  ]

  const positionColumns: ColumnsType<Position> = [
    {
      title: '股票代码',
      dataIndex: 'stock_code',
      key: 'stock_code',
      render: (text) => <Text strong>{text}</Text>
    },
    {
      title: '股票名称',
      dataIndex: 'stock_name',
      key: 'stock_name'
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      key: 'quantity',
      render: (value) => value.toLocaleString()
    },
    {
      title: '成本价',
      dataIndex: 'avg_cost',
      key: 'avg_cost',
      render: (value) => `¥${value.toFixed(2)}`
    },
    {
      title: '现价',
      dataIndex: 'current_price',
      key: 'current_price',
      render: (value) => `¥${value.toFixed(2)}`
    },
    {
      title: '市值',
      dataIndex: 'market_value',
      key: 'market_value',
      render: (value) => `¥${value.toLocaleString()}`
    },
    {
      title: '盈亏',
      dataIndex: 'unrealized_pnl',
      key: 'unrealized_pnl',
      render: (value, record) => (
        <Text type={value >= 0 ? 'success' : 'danger'}>
          {value >= 0 ? '+' : ''}{value.toFixed(2)} ({(record.unrealized_pct * 100).toFixed(2)}%)
        </Text>
      )
    },
    {
      title: '行业',
      dataIndex: 'industry',
      key: 'industry',
      render: (text) => <Tag color="blue">{text}</Tag>
    }
  ]

  const transactionColumns: ColumnsType<Transaction> = [
    {
      title: '股票代码',
      dataIndex: 'stock_code',
      key: 'stock_code',
      render: (text) => <Text strong>{text}</Text>
    },
    {
      title: '股票名称',
      dataIndex: 'stock_name',
      key: 'stock_name'
    },
    {
      title: '交易类型',
      dataIndex: 'transaction_type',
      key: 'transaction_type',
      render: (type) => {
        const typeMap: Record<string, { color: string; text: string }> = {
          'buy': { color: 'green', text: '买入' },
          'sell': { color: 'red', text: '卖出' },
          'dividend': { color: 'blue', text: '分红' },
          'split': { color: 'orange', text: '拆股' }
        }
        return <Tag color={typeMap[type].color}>{typeMap[type].text}</Tag>
      }
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      key: 'quantity',
      render: (value) => value.toLocaleString()
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      render: (value) => `¥${value.toFixed(2)}`
    },
    {
      title: '金额',
      dataIndex: 'amount',
      key: 'amount',
      render: (value) => `¥${value.toLocaleString()}`
    },
    {
      title: '手续费',
      dataIndex: 'fee',
      key: 'fee',
      render: (value) => `¥${value.toFixed(2)}`
    },
    {
      title: '交易时间',
      dataIndex: 'executed_at',
      key: 'executed_at',
      render: (time) => new Date(time).toLocaleString()
    }
  ]

  const calculatePortfolioStats = () => {
    if (!selectedPortfolio || positions.length === 0) {
      return { totalValue: 0, totalPnL: 0, totalReturn: 0 }
    }

    const totalValue = positions.reduce((sum, pos) => sum + pos.market_value, 0) + selectedPortfolio.cash_amount
    const totalCost = positions.reduce((sum, pos) => sum + (pos.avg_cost * pos.quantity), 0)
    const totalPnL = positions.reduce((sum, pos) => sum + pos.unrealized_pnl, 0)
    const totalReturn = totalCost > 0 ? (totalPnL / totalCost) * 100 : 0

    return { totalValue, totalPnL, totalReturn }
  }

  const stats = calculatePortfolioStats()

  return (
    <div style={{ padding: '24px', background: '#f5f5f5', minHeight: '100vh' }}>
      <Title level={2} style={{ marginBottom: '24px' }}>
        <TrophyOutlined /> 投资组合管理
      </Title>

      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane tab="投资组合列表" key="portfolios">
          <Card
            title="我的投资组合"
            extra={
              <Space>
                <Button icon={<ReloadOutlined />} onClick={loadPortfolios}>
                  刷新
                </Button>
                <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalVisible(true)}>
                  创建组合
                </Button>
              </Space>
            }
          >
            <Table
              columns={portfolioColumns}
              dataSource={portfolios}
              rowKey="id"
              loading={loading}
              pagination={false}
            />
          </Card>
        </TabPane>

        <TabPane tab="持仓详情" key="positions" disabled={!selectedPortfolio}>
          {selectedPortfolio && (
            <>
              <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
                <Col xs={24} sm={8}>
                  <Card>
                    <Statistic
                      title="总资产"
                      value={stats.totalValue}
                      prefix={<DollarOutlined />}
                      precision={2}
                      suffix="¥"
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={8}>
                  <Card>
                    <Statistic
                      title="总盈亏"
                      value={stats.totalPnL}
                      prefix={stats.totalPnL >= 0 ? <RiseOutlined /> : <FallOutlined />}
                      precision={2}
                      suffix="¥"
                      valueStyle={{ color: stats.totalPnL >= 0 ? '#3f8600' : '#cf1322' }}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={8}>
                  <Card>
                    <Statistic
                      title="总收益率"
                      value={stats.totalReturn}
                      prefix={<LineChartOutlined />}
                      precision={2}
                      suffix="%"
                      valueStyle={{ color: stats.totalReturn >= 0 ? '#3f8600' : '#cf1322' }}
                    />
                  </Card>
                </Col>
              </Row>

              <Card
                title={`${selectedPortfolio.name} - 持仓明细`}
                extra={
                  <Button type="primary" icon={<PlusOutlined />} onClick={() => setPositionModalVisible(true)}>
                    添加持仓
                  </Button>
                }
              >
                <Table
                  columns={positionColumns}
                  dataSource={positions}
                  rowKey="id"
                  loading={loading}
                  pagination={false}
                />
              </Card>
            </>
          )}
        </TabPane>

        <TabPane tab="交易记录" key="transactions" disabled={!selectedPortfolio}>
          {selectedPortfolio && (
            <Card title={`${selectedPortfolio.name} - 交易记录`}>
              <Table
                columns={transactionColumns}
                dataSource={transactions}
                rowKey="id"
                loading={loading}
                pagination={{
                  pageSize: 20,
                  showSizeChanger: true,
                  showQuickJumper: true
                }}
              />
            </Card>
          )}
        </TabPane>
      </Tabs>

      {/* 创建投资组合模态框 */}
      <Modal
        title="创建投资组合"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => form.submit()}
        confirmLoading={loading}
      >
        <Form form={form} layout="vertical" onFinish={handleCreatePortfolio}>
          <Form.Item
            name="name"
            label="组合名称"
            rules={[{ required: true, message: '请输入组合名称' }]}
          >
            <Input placeholder="请输入组合名称" />
          </Form.Item>
          <Form.Item name="description" label="组合描述">
            <Input.TextArea rows={3} placeholder="请输入组合描述" />
          </Form.Item>
          <Form.Item
            name="total_value"
            label="初始资金"
            rules={[{ required: true, message: '请输入初始资金' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              placeholder="请输入初始资金"
              min={0}
              precision={2}
              prefix="¥"
            />
          </Form.Item>
          <Form.Item
            name="risk_level"
            label="风险等级"
            rules={[{ required: true, message: '请选择风险等级' }]}
          >
            <Select placeholder="请选择风险等级">
              <Option value="low">低风险</Option>
              <Option value="moderate">中风险</Option>
              <Option value="high">高风险</Option>
              <Option value="very_high">极高风险</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* 添加持仓模态框 */}
      <Modal
        title="添加持仓"
        open={positionModalVisible}
        onCancel={() => setPositionModalVisible(false)}
        onOk={() => positionForm.submit()}
        confirmLoading={loading}
      >
        <Form form={positionForm} layout="vertical" onFinish={handleAddPosition}>
          <Form.Item
            name="stock_code"
            label="股票代码"
            rules={[{ required: true, message: '请输入股票代码' }]}
          >
            <Input placeholder="请输入股票代码" />
          </Form.Item>
          <Form.Item
            name="stock_name"
            label="股票名称"
            rules={[{ required: true, message: '请输入股票名称' }]}
          >
            <Input placeholder="请输入股票名称" />
          </Form.Item>
          <Form.Item
            name="quantity"
            label="买入数量"
            rules={[{ required: true, message: '请输入买入数量' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              placeholder="请输入买入数量"
              min={1}
              precision={0}
            />
          </Form.Item>
          <Form.Item
            name="avg_cost"
            label="成本价"
            rules={[{ required: true, message: '请输入成本价' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              placeholder="请输入成本价"
              min={0}
              precision={2}
              prefix="¥"
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default PortfolioManager