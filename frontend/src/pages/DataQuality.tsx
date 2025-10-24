import React, { useState, useEffect } from 'react'
import {
  Card,
  Row,
  Col,
  Table,
  Button,
  Space,
  Input,
  Select,
  message,
  Typography,
  Tag,
  Progress,
  Statistic,
  Alert,
  List,
  Modal,
  Badge
} from 'antd'
import {
  DatabaseOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  WarningOutlined,
  SearchOutlined,
  ReloadOutlined,
  EyeOutlined,
  BugOutlined,
  AlertOutlined,
  DashboardOutlined
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import apiService from '../services/api'

const { Title, Text } = Typography
const { Option } = Select

interface QualityIssue {
  id: string
  type: string
  severity: string
  stock_code: string
  data_type: string
  description: string
  value: number
  expected: string
  record_date: string
  detected_at: string
  status: string
}

interface QualityReport {
  total_records: number
  total_issues: number
  issues_by_type: Record<string, number>
  issues_by_severity: Record<string, number>
  quality_score: number
  check_date: string
  summary: string
  recommendations: string[]
}

interface QualityMetrics {
  completeness: number
  accuracy: number
  consistency: number
  timeliness: number
  validity: number
  overall_score: number
  last_checked: string
}

interface AnomalyDetection {
  stock_code: string
  detection_type: string
  anomaly_value: number
  expected_range: string
  confidence: number
  record_date: string
  description: string
  detected_at: string
}

const DataQualityPage: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [qualityReport, setQualityReport] = useState<QualityReport | null>(null)
  const [qualityMetrics, setQualityMetrics] = useState<QualityMetrics | null>(null)
  const [anomalies, setAnomalies] = useState<AnomalyDetection[]>([])
  const [selectedStockCode, setSelectedStockCode] = useState('')
  const [detectionDays, setDetectionDays] = useState(30)
  const [detailModalVisible, setDetailModalVisible] = useState(false)
  const [selectedIssue, setSelectedIssue] = useState<QualityIssue | null>(null)

  useEffect(() => {
    loadQualityReport()
    loadQualityMetrics()
  }, [])

  const loadQualityReport = async () => {
    try {
      setLoading(true)
      const response = await apiService.checkDataQuality()
      if (response.success) {
        setQualityReport(response.data)
      }
    } catch (error) {
      console.error('加载质量报告失败:', error)
      message.error('加载质量报告失败')
    } finally {
      setLoading(false)
    }
  }

  const loadQualityMetrics = async () => {
    try {
      const response = await apiService.getDataQualityMetrics()
      if (response.success) {
        setQualityMetrics(response.data)
      }
    } catch (error) {
      console.error('加载质量指标失败:', error)
      message.error('加载质量指标失败')
    }
  }

  const handleDetectAnomalies = async () => {
    if (!selectedStockCode) {
      message.warning('请输入股票代码')
      return
    }

    try {
      setLoading(true)
      const response = await apiService.detectAnomalies(selectedStockCode, detectionDays)
      if (response.success) {
        setAnomalies(response.data)
        message.success(`检测完成，发现${response.data.length}个异常`)
      }
    } catch (error) {
      console.error('异常检测失败:', error)
      message.error('异常检测失败')
    } finally {
      setLoading(false)
    }
  }

  const getSeverityColor = (severity: string) => {
    const colors = {
      low: 'blue',
      medium: 'orange',
      high: 'red',
      critical: 'red'
    }
    return colors[severity as keyof typeof colors] || 'default'
  }

  const getSeverityIcon = (severity: string) => {
    const icons = {
      low: <CheckCircleOutlined />,
      medium: <WarningOutlined />,
      high: <ExclamationCircleOutlined />,
      critical: <BugOutlined />
    }
    return icons[severity as keyof typeof icons] || <CheckCircleOutlined />
  }

  const getQualityScoreColor = (score: number) => {
    if (score >= 90) return '#52c41a'
    if (score >= 80) return '#73d13d'
    if (score >= 70) return '#faad14'
    if (score >= 60) return '#ff7a45'
    return '#f5222d'
  }

  const getAnomalyTypeLabel = (type: string) => {
    const labels = {
      price_spike: '价格异常波动',
      volume_anomaly: '成交量异常',
      gap: '价格跳空'
    }
    return labels[type as keyof typeof labels] || type
  }

  const issueColumns: ColumnsType<QualityIssue> = [
    {
      title: '问题类型',
      dataIndex: 'type',
      key: 'type',
      render: (type) => {
        const typeLabels = {
          missing_data: '缺失数据',
          outlier: '异常值',
          inconsistency: '不一致',
          duplicate: '重复数据'
        }
        return <Tag color="blue">{typeLabels[type as keyof typeof typeLabels] || type}</Tag>
      }
    },
    {
      title: '严重程度',
      dataIndex: 'severity',
      key: 'severity',
      render: (severity) => (
        <Tag color={getSeverityColor(severity)} icon={getSeverityIcon(severity)}>
          {severity.toUpperCase()}
        </Tag>
      )
    },
    {
      title: '股票代码',
      dataIndex: 'stock_code',
      key: 'stock_code'
    },
    {
      title: '数据类型',
      dataIndex: 'data_type',
      key: 'data_type'
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description'
    },
    {
      title: '异常值',
      dataIndex: 'value',
      key: 'value',
      render: (value) => <Text code>{value}</Text>
    },
    {
      title: '期望值',
      dataIndex: 'expected',
      key: 'expected',
      render: (expected) => <Text type="secondary">{expected}</Text>
    },
    {
      title: '记录日期',
      dataIndex: 'record_date',
      key: 'record_date'
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Button
          type="link"
          size="small"
          icon={<EyeOutlined />}
          onClick={() => {
            setSelectedIssue(record)
            setDetailModalVisible(true)
          }}
        >
          详情
        </Button>
      )
    }
  ]

  const anomalyColumns: ColumnsType<AnomalyDetection> = [
    {
      title: '股票代码',
      dataIndex: 'stock_code',
      key: 'stock_code',
      render: (text) => <Text strong>{text}</Text>
    },
    {
      title: '异常类型',
      dataIndex: 'detection_type',
      key: 'detection_type',
      render: (type) => <Tag color="orange">{getAnomalyTypeLabel(type)}</Tag>
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description'
    },
    {
      title: '异常值',
      dataIndex: 'anomaly_value',
      key: 'anomaly_value',
      render: (value) => <Text style={{ color: '#f5222d' }}>{value}</Text>
    },
    {
      title: '期望范围',
      dataIndex: 'expected_range',
      key: 'expected_range',
      render: (range) => <Text type="secondary">{range}</Text>
    },
    {
      title: '置信度',
      dataIndex: 'confidence',
      key: 'confidence',
      render: (confidence) => (
        <Progress
          percent={Math.round(confidence * 100)}
          size="small"
          status={confidence > 0.8 ? 'exception' : 'normal'}
        />
      )
    },
    {
      title: '记录日期',
      dataIndex: 'record_date',
      key: 'record_date'
    }
  ]

  return (
    <div style={{ padding: '24px', background: '#f5f5f5', minHeight: '100vh' }}>
      <Title level={2}>
        <DashboardOutlined /> 数据质量监控
      </Title>

      {/* 质量评分概览 */}
      {qualityMetrics && (
        <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
          <Col span={6}>
            <Card>
              <Statistic
                title="综合评分"
                value={qualityMetrics.overall_score}
                precision={1}
                suffix="%"
                valueStyle={{ color: getQualityScoreColor(qualityMetrics.overall_score) }}
                prefix={<DatabaseOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="完整性"
                value={qualityMetrics.completeness}
                precision={1}
                suffix="%"
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="准确性"
                value={qualityMetrics.accuracy}
                precision={1}
                suffix="%"
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="一致性"
                value={qualityMetrics.consistency}
                precision={1}
                suffix="%"
                valueStyle={{ color: '#722ed1' }}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* 质量报告 */}
      <Card
        title="数据质量报告"
        extra={
          <Space>
            <Button icon={<ReloadOutlined />} onClick={loadQualityReport}>
              刷新报告
            </Button>
            <Button icon={<CheckCircleOutlined />} onClick={loadQualityMetrics}>
              更新指标
            </Button>
          </Space>
        }
        style={{ marginBottom: '24px' }}
      >
        {qualityReport && (
          <div>
            <Row gutter={[16, 16]} style={{ marginBottom: '16px' }}>
              <Col span={8}>
                <Alert
                  message="质量评分"
                  description={
                    <div>
                      <div style={{ fontSize: '24px', fontWeight: 'bold', color: getQualityScoreColor(qualityReport.quality_score) }}>
                        {qualityReport.quality_score.toFixed(2)}%
                      </div>
                      <div>{qualityReport.summary}</div>
                    </div>
                  }
                  type={qualityReport.quality_score >= 80 ? 'success' : qualityReport.quality_score >= 60 ? 'warning' : 'error'}
                  showIcon
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="总记录数"
                  value={qualityReport.total_records}
                  formatter={(value) => `${Number(value).toLocaleString()}`}
                />
                <br />
                <Statistic
                  title="发现问题"
                  value={qualityReport.total_issues}
                  valueStyle={{ color: qualityReport.total_issues > 0 ? '#f5222d' : '#52c41a' }}
                />
              </Col>
              <Col span={8}>
                <div>
                  <Text strong>问题分布：</Text>
                  <div style={{ marginTop: '8px' }}>
                    {Object.entries(qualityReport.issues_by_type).map(([type, count]) => (
                      <div key={type} style={{ marginBottom: '4px' }}>
                        <Tag color="blue">{type}</Tag>
                        <Badge count={count} />
                      </div>
                    ))}
                  </div>
                </div>
              </Col>
            </Row>

            {qualityReport.recommendations.length > 0 && (
              <div>
                <Text strong>改进建议：</Text>
                <List
                  size="small"
                  dataSource={qualityReport.recommendations}
                  renderItem={(item, index) => (
                    <List.Item key={index}>
                      <Alert
                        message={item}
                        type="info"
                        showIcon={false}
                        style={{ border: 'none', padding: '4px 0' }}
                      />
                    </List.Item>
                  )}
                />
              </div>
            )}
          </div>
        )}
      </Card>

      {/* 异常检测 */}
      <Card
        title="异常数据检测"
        style={{ marginBottom: '24px' }}
      >
        <Space style={{ marginBottom: '16px' }}>
          <Input
            placeholder="输入股票代码"
            value={selectedStockCode}
            onChange={(e) => setSelectedStockCode(e.target.value.toUpperCase())}
            style={{ width: 200 }}
            prefix={<SearchOutlined />}
          />
          <Select
            value={detectionDays}
            onChange={setDetectionDays}
            style={{ width: 120 }}
          >
            <Option value={7}>7天</Option>
            <Option value={30}>30天</Option>
            <Option value={60}>60天</Option>
            <Option value={90}>90天</Option>
          </Select>
          <Button
            type="primary"
            icon={<AlertOutlined />}
            loading={loading}
            onClick={handleDetectAnomalies}
          >
            开始检测
          </Button>
        </Space>

        {anomalies.length > 0 && (
          <Table
            columns={anomalyColumns}
            dataSource={anomalies}
            rowKey={(record) => `${record.stock_code}_${record.record_date}_${record.detection_type}`}
            pagination={false}
            size="small"
          />
        )}

        {anomalies.length === 0 && selectedStockCode && !loading && (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <CheckCircleOutlined style={{ fontSize: '48px', color: '#52c41a' }} />
            <div style={{ marginTop: '16px' }}>
              <Text type="secondary">未发现异常数据</Text>
            </div>
          </div>
        )}
      </Card>

      {/* 详细问题列表 */}
      <Card title="质量问题详情">
        <Table
          columns={issueColumns}
          dataSource={[]} // TODO: 从API获取详细问题列表
          rowKey="id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true
          }}
          size="small"
        />
      </Card>

      {/* 问题详情模态框 */}
      <Modal
        title="质量问题详情"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={600}
      >
        {selectedIssue && (
          <div>
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Text strong>问题ID：</Text>
                <div>{selectedIssue.id}</div>
              </Col>
              <Col span={12}>
                <Text strong>问题类型：</Text>
                <div>{selectedIssue.type}</div>
              </Col>
              <Col span={12}>
                <Text strong>严重程度：</Text>
                <div>
                  <Tag color={getSeverityColor(selectedIssue.severity)}>
                    {selectedIssue.severity.toUpperCase()}
                  </Tag>
                </div>
              </Col>
              <Col span={12}>
                <Text strong>数据类型：</Text>
                <div>{selectedIssue.data_type}</div>
              </Col>
              <Col span={24}>
                <Text strong>描述：</Text>
                <div>{selectedIssue.description}</div>
              </Col>
              <Col span={12}>
                <Text strong>异常值：</Text>
                <div>{selectedIssue.value}</div>
              </Col>
              <Col span={12}>
                <Text strong>期望值：</Text>
                <div>{selectedIssue.expected}</div>
              </Col>
              <Col span={12}>
                <Text strong>记录日期：</Text>
                <div>{selectedIssue.record_date}</div>
              </Col>
              <Col span={12}>
                <Text strong>检测时间：</Text>
                <div>{selectedIssue.detected_at}</div>
              </Col>
            </Row>
          </div>
        )}
      </Modal>
    </div>
  )
}

export default DataQualityPage