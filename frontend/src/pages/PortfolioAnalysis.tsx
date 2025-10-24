import React, { useState, useEffect } from 'react'
import {
  Card,
  Row,
  Col,
  Statistic,
  Table,
  Button,
  Space,
  Typography,
  Tag,
  Select,
  DatePicker,
  Progress,
  List,
  message
} from 'antd'
import {
  TrophyOutlined,
  RiseOutlined,
  FallOutlined,
  LineChartOutlined,
  PieChartOutlined,
  BarChartOutlined
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import dayjs, { Dayjs } from 'dayjs'

const { Title, Text } = Typography
const { Option } = Select
const { RangePicker } = DatePicker

// 投资组合分析数据接口
interface PortfolioAnalysis {
  portfolio_id: string
  analysis_type: string
  performance: {
    total_return: number
    annualized_return: number
    sharpe_ratio: number
    max_drawdown: number
    volatility: number
    beta: number
    alpha: number
    win_rate: number
    profit_factor: number
  }
  risk_analysis: {
    overall_risk_level: string
    volatility: number
    beta: number
    var_95: number
    concentration_score: number
    diversification_score: number
  }
  allocation: {
    by_sector: Record<string, number>
    by_industry: Record<string, number>
    by_market_cap: Record<string, number>
    concentration: {
      diversification_score: number
      top_positions: Array<{
        stock_code: string
        stock_name: string
        weight: number
        value: number
      }>
    }
    rebalancing: {
      rebalancing_needed: boolean
      recommended_actions: Array<{
        action: string
        stock_code: string
        current_weight: number
        target_weight: number
        reason: string
        priority: string
      }>
    }
  }
  recommendations: Array<{
    type: string
    title: string
    description: string
    priority: string
    actionable: boolean
  }>
  created_at: string
}

const PortfolioAnalysis: React.FC = () => {
  const [analysisData, setAnalysisData] = useState<PortfolioAnalysis | null>(null)
  const [loading, setLoading] = useState(false)
  const [selectedPortfolio, setSelectedPortfolio] = useState<string>('portfolio_001')
  const [analysisType, setAnalysisType] = useState<string>('comprehensive')
  const [benchmark, setBenchmark] = useState<string>('000300')
  const [dateRange, setDateRange] = useState<[Dayjs, Dayjs]>([
    dayjs().subtract(1, 'year'),
    dayjs()
  ])

  useEffect(() => {
    if (selectedPortfolio) {
      loadAnalysis()
    }
  }, [selectedPortfolio, analysisType, benchmark, dateRange])

  const loadAnalysis = async () => {
    try {
      setLoading(true)

      // 模拟API调用
      const mockAnalysis: PortfolioAnalysis = {
        portfolio_id: selectedPortfolio,
        analysis_type: analysisType,
        performance: {
          total_return: 0.15,
          annualized_return: 0.12,
          sharpe_ratio: 1.2,
          max_drawdown: 0.08,
          volatility: 0.18,
          beta: 1.1,
          alpha: 0.025,
          win_rate: 0.65,
          profit_factor: 1.45
        },
        risk_analysis: {
          overall_risk_level: 'medium',
          volatility: 0.18,
          beta: 1.1,
          var_95: 0.05,
          concentration_score: 0.75,
          diversification_score: 0.80
        },
        allocation: {
          by_sector: {
            '科技': 0.35,
            '金融': 0.25,
            '消费': 0.20,
            '医药': 0.20
          },
          by_industry: {
            '软件开发': 0.20,
            '银行': 0.15,
            '保险': 0.10,
            '零售': 0.15,
            '制药': 0.20,
            '生物技术': 0.10,
            '汽车制造': 0.10
          },
          by_market_cap: {
            '大盘股': 0.45,
            '中盘股': 0.35,
            '小盘股': 0.20
          },
          concentration: {
            diversification_score: 0.75,
            top_positions: [
              {
                stock_code: '000001',
                stock_name: '平安银行',
                weight: 0.12,
                value: 120000
              },
              {
                stock_code: '000002',
                stock_name: '万科A',
                weight: 0.10,
                value: 100000
              }
            ]
          },
          rebalancing: {
            rebalancing_needed: false,
            recommended_actions: []
          }
        },
        recommendations: [
          {
            type: 'risk',
            title: '适当增加科技股配置',
            description: '建议增加科技股比重以提升收益潜力',
            priority: 'medium',
            actionable: true
          },
          {
            type: 'performance',
            title: '定期进行组合再平衡',
            description: '建议每季度进行一次组合再平衡，维持目标配置比例',
            priority: 'medium',
            actionable: true
          }
        ],
        created_at: new Date().toISOString()
      }

      setAnalysisData(mockAnalysis)
    } catch (error) {
      console.error('加载分析数据失败:', error)
      message.error('加载投资组合分析失败')
    } finally {
      setLoading(false)
    }
  }

  const handleExport = () => {
    console.log('导出分析报告')
    message.success('分析报告导出成功')
  }

  const getRiskLevelColor = (level: string) => {
    const colorMap: Record<string, string> = {
      'low': '#52c41a',
      'moderate': '#faad14',
      'medium': '#faad14',
      'high': '#ff4d4f',
      'very_high': '#ff4d4f'
    }
    return colorMap[level] || '#d9d9d9'
  }

  const allocationColumns: ColumnsType<any> = [
    {
      title: '类别',
      dataIndex: 'category',
      key: 'category',
      render: (text) => <Text strong>{text}</Text>
    },
    {
      title: '配置比例',
      dataIndex: 'percentage',
      key: 'percentage',
      render: (value) => (
        <div style={{ width: '200px' }}>
          <Progress
            percent={value * 100}
            format={() => `${(value * 100).toFixed(1)}%`}
            strokeColor="#1890ff"
          />
        </div>
      )
    }
  ]

  const positionColumns: ColumnsType<any> = [
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
      title: '权重',
      dataIndex: 'weight',
      key: 'weight',
      render: (value) => `${(value * 100).toFixed(2)}%`
    },
    {
      title: '市值',
      dataIndex: 'value',
      key: 'value',
      render: (value) => `¥${value.toLocaleString()}`
    }
  ]

  if (!analysisData) {
    return (
      <div style={{ padding: '24px', textAlign: 'center' }}>
        <Button type="primary" onClick={loadAnalysis} loading={loading}>
          开始分析
        </Button>
      </div>
    )
  }

  return (
    <div style={{ padding: '24px', background: '#f5f5f5', minHeight: '100vh' }}>
      <Title level={2} style={{ marginBottom: '24px' }}>
        <BarChartOutlined /> 投资组合分析
      </Title>

      {/* 分析配置 */}
      <Card style={{ marginBottom: '24px' }}>
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} sm={6}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Text strong>选择组合</Text>
              <Select
                value={selectedPortfolio}
                onChange={setSelectedPortfolio}
                style={{ width: '100%' }}
              >
                <Option value="portfolio_001">智股通组合</Option>
                <Option value="portfolio_002">成长股组合</Option>
              </Select>
            </Space>
          </Col>
          <Col xs={24} sm={6}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Text strong>分析类型</Text>
              <Select
                value={analysisType}
                onChange={setAnalysisType}
                style={{ width: '100%' }}
              >
                <Option value="comprehensive">综合分析</Option>
                <Option value="performance">业绩分析</Option>
                <Option value="risk">风险分析</Option>
                <Option value="allocation">配置分析</Option>
              </Select>
            </Space>
          </Col>
          <Col xs={24} sm={6}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Text strong>基准指数</Text>
              <Select
                value={benchmark}
                onChange={setBenchmark}
                style={{ width: '100%' }}
              >
                <Option value="000300">沪深300</Option>
                <Option value="000905">中证500</Option>
                <Option value="399001">深证成指</Option>
              </Select>
            </Space>
          </Col>
          <Col xs={24} sm={6}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Text strong>分析时间</Text>
              <RangePicker
                value={dateRange}
                onChange={(dates) => {
  if (dates && dates[0] && dates[1]) {
    setDateRange([dates[0], dates[1]])
  }
}}
                style={{ width: '100%' }}
              />
            </Space>
          </Col>
          <Col xs={24} sm={6}>
            <Space>
              <Button icon={<BarChartOutlined />} onClick={loadAnalysis} loading={loading}>
                重新分析
              </Button>
              <Button icon={<TrophyOutlined />} onClick={handleExport}>
                导出报告
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 业绩指标 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} lg={12}>
          <Card title="业绩指标" extra={<TrophyOutlined />}>
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={12}>
                <Statistic
                  title="总收益率"
                  value={analysisData.performance.total_return * 100}
                  precision={2}
                  suffix="%"
                  prefix={analysisData.performance.total_return >= 0 ? <RiseOutlined /> : <FallOutlined />}
                  valueStyle={{ color: analysisData.performance.total_return >= 0 ? '#3f8600' : '#cf1322' }}
                />
              </Col>
              <Col xs={24} sm={12}>
                <Statistic
                  title="年化收益率"
                  value={analysisData.performance.annualized_return * 100}
                  precision={2}
                  suffix="%"
                  prefix={<LineChartOutlined />}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Col>
              <Col xs={24} sm={12}>
                <Statistic
                  title="夏普比率"
                  value={analysisData.performance.sharpe_ratio}
                  precision={2}
                  prefix={<BarChartOutlined />}
                />
              </Col>
              <Col xs={24} sm={12}>
                <Statistic
                  title="最大回撤"
                  value={analysisData.performance.max_drawdown * 100}
                  precision={2}
                  suffix="%"
                  prefix={<FallOutlined />}
                  valueStyle={{ color: '#cf1322' }}
                />
              </Col>
            </Row>
          </Card>
        </Col>

        {/* 风险分析 */}
        <Col xs={24} lg={12}>
          <Card title="风险分析" extra={<PieChartOutlined />}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text strong>整体风险等级: </Text>
                <Tag color={getRiskLevelColor(analysisData.risk_analysis.overall_risk_level)}>
                  {analysisData.risk_analysis.overall_risk_level === 'low' ? '低风险' :
                   analysisData.risk_analysis.overall_risk_level === 'medium' ? '中风险' :
                   analysisData.risk_analysis.overall_risk_level === 'high' ? '高风险' : '未知风险'}
                </Tag>
              </div>
              <Row gutter={16} style={{ marginTop: '16px' }}>
                <Col span={12}>
                  <Statistic
                    title="波动率"
                    value={analysisData.risk_analysis.volatility * 100}
                    precision={2}
                    suffix="%"
                    valueStyle={{ color: '#faad14' }}
                  />
                </Col>
                <Col span={12}>
                  <Statistic
                    title="Beta值"
                    value={analysisData.risk_analysis.beta}
                    precision={2}
                    prefix={<BarChartOutlined />}
                  />
                </Col>
              </Row>
              <Row gutter={16} style={{ marginTop: '16px' }}>
                <Col span={12}>
                  <Statistic
                    title="VaR(95%)"
                    value={analysisData.risk_analysis.var_95 * 100}
                    precision={2}
                    suffix="%"
                    prefix={<FallOutlined />}
                    valueStyle={{ color: '#faad14' }}
                  />
                </Col>
                <Col span={12}>
                  <Statistic
                    title="分散化评分"
                    value={analysisData.risk_analysis.diversification_score * 100}
                    precision={1}
                    suffix="/100"
                    prefix={<PieChartOutlined />}
                    valueStyle={{ color: '#52c41a' }}
                  />
                </Col>
              </Row>
            </Space>
          </Card>
        </Col>
      </Row>

      {/* 资产配置 */}
      <Card title="资产配置" style={{ marginBottom: '24px' }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} lg={12}>
            <Title level={4}>行业配置</Title>
            <Table
              columns={allocationColumns}
              dataSource={Object.entries(analysisData.allocation.by_sector).map(([category, percentage]) => ({
                key: category,
                category,
                percentage
              }))}
              pagination={false}
              size="small"
            />
          </Col>
          <Col xs={24} lg={12}>
            <Title level={4}>持仓集中度</Title>
            <Table
              columns={positionColumns}
              dataSource={analysisData.allocation.concentration.top_positions}
              pagination={false}
              size="small"
              title={() => <span>前十大持仓</span>}
            />
            <div style={{ marginTop: '16px' }}>
              <Text strong>分散化评分: </Text>
              <Progress
                percent={analysisData.allocation.concentration.diversification_score * 100}
                format={() => `${(analysisData.allocation.concentration.diversification_score * 100).toFixed(0)}/100`}
                strokeColor="#52c41a"
                style={{ width: '200px', marginLeft: '16px' }}
              />
            </div>
          </Col>
        </Row>
      </Card>

      {/* 投资建议 */}
      <Card title="投资建议">
        <List
          dataSource={analysisData.recommendations}
          renderItem={(item) => (
            <List.Item style={{ borderLeft: `4px solid ${
              item.priority === 'high' ? 'red' : 'orange'
            }` }}>
              <List.Item.Meta
                title={
                  <Space>
                    <Text strong>{item.title}</Text>
                    <Tag color={item.priority === 'high' ? 'red' : 'orange'}>
                      {item.priority === 'high' ? '高' : '中'}
                    </Tag>
                    {item.actionable && <Tag color="blue">可执行</Tag>}
                  </Space>
                }
                description={item.description}
              />
            </List.Item>
          )}
        />
      </Card>
    </div>
  )
}

export default PortfolioAnalysis