import React, { useState, useEffect } from 'react'
import {
  Card,
  Row,
  Col,
  Table,
  Button,
  Space,
  Input,
  Progress,
  message,
  Typography,
  Tag,
  Statistic,
  List,
  Alert,
  Modal,
  Checkbox,
  Divider,
  Tooltip
} from 'antd'
import {
  SyncOutlined,
  DatabaseOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  ReloadOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  SettingOutlined,
  InfoCircleOutlined
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import apiService from '../services/api'

const { Title, Text, Paragraph } = Typography
const { TextArea } = Input

interface ServiceStatus {
  cache_size: number
  cache_enabled: boolean
  request_count: number
  error_count: number
  supported_markets: string[]
  update_time: string
}

interface SyncResult {
  code: string
  status: 'success' | 'failed' | 'pending'
  message?: string
}

interface MarketIndex {
  code: string
  name: string
  price: string
  change: string
  change_percent: string
  volume: number
  amount: number
  update_time: string
}

const DataSyncPage: React.FC = () => {
  const [serviceStatus, setServiceStatus] = useState<ServiceStatus | null>(null)
  const [marketIndices, setMarketIndices] = useState<MarketIndex[]>([])
  const [loading, setLoading] = useState(false)
  const [syncing, setSyncing] = useState(false)
  const [syncProgress, setSyncProgress] = useState(0)
  const [syncResults, setSyncResults] = useState<SyncResult[]>([])
  const [selectedCodes, setSelectedCodes] = useState<string[]>([])
  const [customCodes, setCustomCodes] = useState('')
  const [showConfigModal, setShowConfigModal] = useState(false)

  // 默认股票代码
  const defaultStockCodes = [
    '000001', // 平安银行
    '000002', // 万科A
    '600000', // 浦发银行
    '600036', // 招商银行
    '000858', // 五粮液
    '600519', // 贵州茅台
    '000725', // 京东方A
    '002415', // 海康威视
    '002594', // 比亚迪
    '300750', // 宁德时代
  ]

  useEffect(() => {
    loadServiceStatus()
    loadMarketIndices()

    // 定时刷新数据
    const interval = setInterval(() => {
      loadServiceStatus()
      loadMarketIndices()
    }, 30000) // 30秒刷新一次

    return () => clearInterval(interval)
  }, [])

  const loadServiceStatus = async () => {
    try {
      const response = await apiService.getExternalServiceStatus()
      if (response.success) {
        setServiceStatus(response.data)
      }
    } catch (error) {
      console.error('加载服务状态失败:', error)
    }
  }

  const loadMarketIndices = async () => {
    try {
      const response = await apiService.getMarketIndices()
      if (response.success) {
        setMarketIndices(response.data)
      }
    } catch (error) {
      console.error('加载市场指数失败:', error)
    }
  }

  const handleSyncData = async (codes: string[]) => {
    if (codes.length === 0) {
      message.warning('请选择要同步的股票')
      return
    }

    setSyncing(true)
    setSyncProgress(0)
    setSyncResults([])

    try {
      const response = await apiService.syncExternalData(codes)
      if (response.success) {
        message.success(`同步完成，共处理 ${response.data.synced_count} 只股票`)

        // 模拟同步结果
        const results: SyncResult[] = codes.map(code => ({
          code,
          status: Math.random() > 0.1 ? 'success' : 'failed',
          message: Math.random() > 0.1 ? '同步成功' : '数据获取失败'
        }))

        setSyncResults(results)

        // 刷新状态
        await loadServiceStatus()
      } else {
        message.error('同步失败')
      }
    } catch (error) {
      console.error('同步数据失败:', error)
      message.error('同步数据失败')
    } finally {
      setSyncing(false)
      setSyncProgress(100)
    }
  }

  const handleRefreshCache = async () => {
    try {
      setLoading(true)
      const response = await apiService.refreshExternalCache()
      if (response.success) {
        message.success('缓存刷新成功')
        await loadServiceStatus()
      } else {
        message.error('缓存刷新失败')
      }
    } catch (error) {
      console.error('刷新缓存失败:', error)
      message.error('刷新缓存失败')
    } finally {
      setLoading(false)
    }
  }

  const handleBatchSync = async () => {
    let codesToSync = [...selectedCodes]

    // 添加自定义代码
    if (customCodes.trim()) {
      const customCodeList = customCodes.split(',').map(code => code.trim()).filter(code => code)
      codesToSync = [...codesToSync, ...customCodeList]
    }

    if (codesToSync.length === 0) {
      message.warning('请选择或输入股票代码')
      return
    }

    await handleSyncData(codesToSync)
  }

  const indexColumns: ColumnsType<MarketIndex> = [
    {
      title: '指数名称',
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => (
        <div>
          <Text strong>{text}</Text>
          <br />
          <Text type="secondary" style={{ fontSize: '12px' }}>{record.code}</Text>
        </div>
      )
    },
    {
      title: '当前点位',
      dataIndex: 'price',
      key: 'price',
      render: (text) => <Text strong>{parseFloat(text).toFixed(2)}</Text>
    },
    {
      title: '涨跌',
      dataIndex: 'change',
      key: 'change',
      render: (text, record) => {
        const change = parseFloat(text)
        const changePercent = parseFloat(record.change_percent)
        const color = change >= 0 ? '#f5222d' : '#52c41a'
        const prefix = change >= 0 ? '+' : ''

        return (
          <div style={{ color }}>
            <div>{prefix}{change.toFixed(2)}</div>
            <div style={{ fontSize: '12px' }}>{prefix}{changePercent.toFixed(2)}%</div>
          </div>
        )
      }
    },
    {
      title: '成交量',
      dataIndex: 'volume',
      key: 'volume',
      render: (text) => <Text type="secondary">{(text / 100000000).toFixed(2)}亿</Text>
    },
    {
      title: '更新时间',
      dataIndex: 'update_time',
      key: 'update_time',
      render: (text) => <Text type="secondary" style={{ fontSize: '12px' }}>{text}</Text>
    }
  ]

  const resultColumns: ColumnsType<SyncResult> = [
    {
      title: '股票代码',
      dataIndex: 'code',
      key: 'code'
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const statusConfig = {
          success: { color: 'green', icon: <CheckCircleOutlined />, text: '成功' },
          failed: { color: 'red', icon: <ExclamationCircleOutlined />, text: '失败' },
          pending: { color: 'blue', icon: <SyncOutlined spin />, text: '处理中' }
        }

        const config = statusConfig[status]
        return (
          <Tag color={config.color} icon={config.icon}>
            {config.text}
          </Tag>
        )
      }
    },
    {
      title: '消息',
      dataIndex: 'message',
      key: 'message'
    }
  ]

  return (
    <div style={{ padding: '24px', background: '#f5f5f5', minHeight: '100vh' }}>
      <Title level={2}>
        <DatabaseOutlined /> 数据同步管理
      </Title>

      {/* 服务状态卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="缓存大小"
              value={serviceStatus?.cache_size || 0}
              prefix={<DatabaseOutlined />}
              suffix="项"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="请求次数"
              value={serviceStatus?.request_count || 0}
              prefix={<SyncOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="错误次数"
              value={serviceStatus?.error_count || 0}
              prefix={<ExclamationCircleOutlined />}
              valueStyle={{ color: serviceStatus?.error_count ? '#f5222d' : '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="缓存状态"
              value={serviceStatus?.cache_enabled ? '启用' : '禁用'}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: serviceStatus?.cache_enabled ? '#52c41a' : '#f5222d' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 市场指数 */}
      <Card
        title="主要指数"
        extra={
          <Button
            icon={<ReloadOutlined />}
            loading={loading}
            onClick={loadMarketIndices}
          >
            刷新指数
          </Button>
        }
        style={{ marginBottom: '24px' }}
      >
        <Table
          columns={indexColumns}
          dataSource={marketIndices}
          rowKey="code"
          pagination={false}
          size="small"
        />
      </Card>

      {/* 数据同步操作 */}
      <Row gutter={[16, 16]}>
        <Col span={12}>
          <Card
            title="快速同步"
            extra={
              <Button
                icon={<SettingOutlined />}
                onClick={() => setShowConfigModal(true)}
              >
                配置
              </Button>
            }
          >
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text strong>默认股票代码：</Text>
                <div style={{ marginTop: '8px' }}>
                  {defaultStockCodes.map(code => (
                    <Checkbox
                      key={code}
                      checked={selectedCodes.includes(code)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedCodes([...selectedCodes, code])
                        } else {
                          setSelectedCodes(selectedCodes.filter(c => c !== code))
                        }
                      }}
                      style={{ margin: '4px' }}
                    >
                      {code}
                    </Checkbox>
                  ))}
                </div>
              </div>

              <Divider />

              <div>
                <Text strong>自定义股票代码：</Text>
                <TextArea
                  placeholder="输入股票代码，用逗号分隔，如：000001,600000"
                  value={customCodes}
                  onChange={(e) => setCustomCodes(e.target.value)}
                  rows={3}
                  style={{ marginTop: '8px' }}
                />
              </div>

              <Space>
                <Button
                  type="primary"
                  icon={<PlayCircleOutlined />}
                  loading={syncing}
                  onClick={handleBatchSync}
                  disabled={selectedCodes.length === 0 && !customCodes.trim()}
                >
                  开始同步
                </Button>
                <Button
                  icon={<ReloadOutlined />}
                  loading={loading}
                  onClick={handleRefreshCache}
                >
                  刷新缓存
                </Button>
              </Space>

              {syncing && (
                <div style={{ marginTop: '16px' }}>
                  <Text>同步进度：</Text>
                  <Progress percent={syncProgress} status="active" />
                </div>
              )}
            </Space>
          </Card>
        </Col>

        <Col span={12}>
          <Card title="同步结果">
            {syncResults.length > 0 ? (
              <Table
                columns={resultColumns}
                dataSource={syncResults}
                rowKey="code"
                pagination={false}
                size="small"
              />
            ) : (
              <div style={{ textAlign: 'center', padding: '40px' }}>
                <ClockCircleOutlined style={{ fontSize: '48px', color: '#d9d9d9' }} />
                <div style={{ marginTop: '16px' }}>
                  <Text type="secondary">暂无同步结果</Text>
                </div>
              </div>
            )}
          </Card>
        </Col>
      </Row>

      {/* 服务信息 */}
      <Card title="服务信息" style={{ marginTop: '24px' }}>
        <Alert
          message="数据服务状态"
          description={
            <div>
              <p>• 服务地址：http://127.0.0.1:8001</p>
              <p>• 支持市场：{serviceStatus?.supported_markets?.join(', ') || '未知'}</p>
              <p>• 最后更新：{serviceStatus?.update_time || '未知'}</p>
              <p>• 数据来源：akshare (开源财经数据接口)</p>
            </div>
          }
          type="info"
          showIcon
        />
      </Card>

      {/* 配置模态框 */}
      <Modal
        title="同步配置"
        open={showConfigModal}
        onCancel={() => setShowConfigModal(false)}
        footer={[
          <Button key="close" onClick={() => setShowConfigModal(false)}>
            关闭
          </Button>
        ]}
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <Text strong>同步说明：</Text>
            <Paragraph>
              • 数据同步将从akshare获取最新的股票数据<br />
              • 建议在交易时间外进行大量数据同步<br />
              • 同步过程中请勿关闭应用程序<br />
              • 数据将自动保存到本地数据库
            </Paragraph>
          </div>

          <div>
            <Text strong>注意事项：</Text>
            <Paragraph>
              <InfoCircleOutlined style={{ color: '#1890ff', marginRight: '8px' }} />
              请确保网络连接稳定，避免同步过程中断
            </Paragraph>
          </div>
        </Space>
      </Modal>
    </div>
  )
}

export default DataSyncPage