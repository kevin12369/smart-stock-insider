import React, { useState, useEffect } from 'react'
import {
  Card,
  Row,
  Col,
  Table,
  Button,
  Space,
  Input,
  DatePicker,
  Select,
  Upload,
  message,
  Typography,
  Tag,
  Progress,
  Modal,
  Form,
  Checkbox,
  Divider,
  Alert,
  Statistic,
  List,
  Tooltip
} from 'antd'
import {
  ExportOutlined,
  ImportOutlined,
  DownloadOutlined,
  UploadOutlined,
  FileTextOutlined,
  DatabaseOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  SyncOutlined,
  InfoCircleOutlined,
  FolderOpenOutlined
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import type { UploadFile } from 'antd/es/upload/interface'
import dayjs, { Dayjs } from 'antd-picker-dayjs'
import apiService from '../services/api'

const { Title, Text, Paragraph } = Typography
const { RangePicker } = DatePicker
const { Option } = Select
const { TextArea } = Input

interface ExportRequest {
  dataType: string
  stockCodes: string
  startDate: string
  endDate: string
  format: string
  outputPath: string
  includeHeaders: boolean
}

interface ImportRequest {
  filePath: string
  dataType: string
  overwrite: boolean
}

interface ExportResult {
  success: boolean
  message: string
  file_path: string
  record_count: number
  file_size: number
  export_time: string
  data_type: string
}

interface ImportResult {
  success: boolean
  message: string
  total_records: number
  success_count: number
  error_count: number
  duplicate_count: number
  import_time: string
  errors?: string[]
}

const DataImportExportPage: React.FC = () => {
  const [exportForm] = Form.useForm()
  const [importForm] = Form.useForm()

  const [loading, setLoading] = useState(false)
  const [exportProgress, setExportProgress] = useState(0)
  const [importProgress, setImportProgress] = useState(0)
  const [exportResults, setExportResults] = useState<ExportResult[]>([])
  const [importResults, setImportResults] = useState<ImportResult[]>([])
  const [templateModalVisible, setTemplateModalVisible] = useState(false)
  const [previewModalVisible, setPreviewModalVisible] = useState(false)
  const [templateContent, setTemplateContent] = useState<string>('')
  const [uploadFileList, setUploadFileList] = useState<UploadFile[]>([])

  // 数据类型选项
  const dataTypes = [
    { value: 'stock_basic', label: '股票基本信息' },
    { value: 'stock_daily', label: '日线数据' },
    { value: 'signals', label: '技术信号数据' },
    { value: 'all', label: '全部数据' }
  ]

  // 格式选项
  const formats = [
    { value: 'csv', label: 'CSV格式' },
    { value: 'json', label: 'JSON格式' }
  ]

  // 导出结果列定义
  const exportColumns: ColumnsType<ExportResult> = [
    {
      title: '导出时间',
      dataIndex: 'export_time',
      key: 'export_time',
      width: 180
    },
    {
      title: '数据类型',
      dataIndex: 'data_type',
      key: 'data_type',
      render: (text) => {
        const type = dataTypes.find(t => t.value === text)
        return <Tag color="blue">{type?.label || text}</Tag>
      }
    },
    {
      title: '记录数',
      dataIndex: 'record_count',
      key: 'record_count',
      render: (text) => <Text strong>{text.toLocaleString()}</Text>
    },
    {
      title: '文件大小',
      dataIndex: 'file_size',
      key: 'file_size',
      render: (text) => {
        const size = text / 1024 / 1024
        return <Text>{size.toFixed(2)} MB</Text>
      }
    },
    {
      title: '状态',
      dataIndex: 'success',
      key: 'success',
      render: (success) => (
        <Tag color={success ? 'green' : 'red'} icon={success ? <CheckCircleOutlined /> : <ExclamationCircleOutlined />}>
          {success ? '成功' : '失败'}
        </Tag>
      )
    },
    {
      title: '文件路径',
      dataIndex: 'file_path',
      key: 'file_path',
      render: (text) => (
        <Tooltip title={text}>
          <Text ellipsis style={{ maxWidth: '200px' }}>{text}</Text>
        </Tooltip>
      )
    }
  ]

  // 导入结果列定义
  const importColumns: ColumnsType<ImportResult> = [
    {
      title: '导入时间',
      dataIndex: 'import_time',
      key: 'import_time',
      width: 180
    },
    {
      title: '总记录数',
      dataIndex: 'total_records',
      key: 'total_records',
      render: (text) => <Text strong>{text.toLocaleString()}</Text>
    },
    {
      title: '成功数',
      dataIndex: 'success_count',
      key: 'success_count',
      render: (text) => <Text style={{ color: '#52c41a' }}>{text.toLocaleString()}</Text>
    },
    {
      title: '失败数',
      dataIndex: 'error_count',
      key: 'error_count',
      render: (text) => <Text style={{ color: '#f5222d' }}>{text.toLocaleString()}</Text>
    },
    {
      title: '重复数',
      dataIndex: 'duplicate_count',
      key: 'duplicate_count',
      render: (text) => <Text style={{ color: '#fa8c16' }}>{text.toLocaleString()}</Text>
    },
    {
      title: '状态',
      dataIndex: 'success',
      key: 'success',
      render: (success) => (
        <Tag color={success ? 'green' : 'red'} icon={success ? <CheckCircleOutlined /> : <ExclamationCircleOutlined />}>
          {success ? '成功' : '失败'}
        </Tag>
      )
    }
  ]

  // 处理导出
  const handleExport = async (values: any) => {
    setLoading(true)
    setExportProgress(0)

    try {
      // 模拟导出进度
      const progressInterval = setInterval(() => {
        setExportProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return 90
          }
          return prev + 10
        })
      }, 200)

      const response = await apiService.exportData(
        values.dataType,
        values.stockCodes || '',
        values.startDate ? values.startDate.format('YYYY-MM-DD') : '',
        values.endDate ? values.endDate.format('YYYY-MM-DD') : '',
        values.format,
        values.outputPath || `exports/stock_data_${values.dataType}_${Date.now()}.${values.format}`,
        values.includeHeaders
      )

      clearInterval(progressInterval)
      setExportProgress(100)

      if (response.success) {
        message.success('导出成功')
        const result = response.data as ExportResult
        setExportResults([result, ...exportResults.slice(0, 9)]) // 保留最近10条记录
      } else {
        message.error('导出失败')
      }
    } catch (error) {
      console.error('导出失败:', error)
      message.error('导出失败')
    } finally {
      setLoading(false)
      setTimeout(() => setExportProgress(0), 2000)
    }
  }

  // 处理导入
  const handleImport = async (values: any) => {
    if (uploadFileList.length === 0) {
      message.warning('请选择要导入的文件')
      return
    }

    setLoading(true)
    setImportProgress(0)

    try {
      // 模拟导入进度
      const progressInterval = setInterval(() => {
        setImportProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return 90
          }
          return prev + 10
        })
      }, 300)

      const filePath = uploadFileList[0].response?.filePath || uploadFileList[0].name || ''

      const response = await apiService.importData(
        filePath,
        values.dataType,
        values.overwrite
      )

      clearInterval(progressInterval)
      setImportProgress(100)

      if (response.success) {
        message.success('导入成功')
        const result = response.data as ImportResult
        setImportResults([result, ...importResults.slice(0, 9)]) // 保留最近10条记录
      } else {
        message.error('导入失败')
      }
    } catch (error) {
      console.error('导入失败:', error)
      message.error('导入失败')
    } finally {
      setLoading(false)
      setTimeout(() => setImportProgress(0), 2000)
      setUploadFileList([])
    }
  }

  // 获取模板
  const handleGetTemplate = async (dataType: string, format: string) => {
    try {
      const response = await apiService.getExportTemplate(dataType, format)
      if (response.success) {
        const { template, filename } = response.data
        setTemplateContent(template)
        setTemplateModalVisible(true)

        // 下载模板文件
        const blob = new Blob([template], { type: format === 'csv' ? 'text/csv' : 'application/json' })
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = filename
        link.click()
        URL.revokeObjectURL(url)

        message.success(`模板下载成功: ${filename}`)
      }
    } catch (error) {
      console.error('获取模板失败:', error)
      message.error('获取模板失败')
    }
  }

  // 文件上传前的处理
  const beforeUpload = (file: UploadFile) => {
    const isValidFormat = file.name.endsWith('.csv') || file.name.endsWith('.json')
    if (!isValidFormat) {
      message.error('只支持CSV和JSON格式的文件')
      return false
    }

    const isLt10M = file.size! / 1024 / 1024 < 10
    if (!isLt10M) {
      message.error('文件大小不能超过10MB')
      return false
    }

    // 模拟文件上传
    setTimeout(() => {
      setUploadFileList([{
        ...file,
        status: 'done',
        response: { filePath: file.name }
      }])
    }, 1000)

    return false // 阻止默认上传行为
  }

  return (
    <div style={{ padding: '24px', background: '#f5f5f5', minHeight: '100vh' }}>
      <Title level={2}>
        <DatabaseOutlined /> 数据导入导出
      </Title>

      {/* 统计信息 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="导出次数"
              value={exportResults.length}
              prefix={<ExportOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="导入次数"
              value={importResults.length}
              prefix={<ImportOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="总导出记录"
              value={exportResults.reduce((sum, r) => sum + r.record_count, 0)}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="总导入记录"
              value={importResults.reduce((sum, r) => sum + r.success_count, 0)}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 导出功能 */}
      <Card
        title="数据导出"
        extra={
          <Button
            icon={<DownloadOutlined />}
            onClick={() => setPreviewModalVisible(true)}
          >
            导入模板
          </Button>
        }
        style={{ marginBottom: '24px' }}
      >
        <Form
          form={exportForm}
          layout="vertical"
          onFinish={handleExport}
          initialValues={{
            format: 'csv',
            includeHeaders: true,
            outputPath: 'exports/stock_data.csv'
          }}
        >
          <Row gutter={[16, 16]}>
            <Col span={8}>
              <Form.Item
                label="数据类型"
                name="dataType"
                rules={[{ required: true, message: '请选择数据类型' }]}
              >
                <Select placeholder="选择要导出的数据类型">
                  {dataTypes.map(type => (
                    <Option key={type.value} value={type.value}>{type.label}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="导出格式"
                name="format"
                rules={[{ required: true, message: '请选择导出格式' }]}
              >
                <Select placeholder="选择导出格式">
                  {formats.map(format => (
                    <Option key={format.value} value={format.value}>{format.label}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="输出路径"
                name="outputPath"
                rules={[{ required: true, message: '请输入输出路径' }]}
              >
                <Input placeholder="exports/stock_data.csv" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={[16, 16]}>
            <Col span={12}>
              <Form.Item label="股票代码" name="stockCodes">
                <Input placeholder="多个代码用逗号分隔，为空则导出全部" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="日期范围" name="dateRange">
                <RangePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="includeHeaders" valuePropName="checked">
            <Checkbox>包含表头</Checkbox>
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={loading} icon={<ExportOutlined />}>
                开始导出
              </Button>
              <Button
                icon={<DownloadOutlined />}
                onClick={() => {
                  const dataType = exportForm.getFieldValue('dataType')
                  const format = exportForm.getFieldValue('format')
                  if (dataType && format) {
                    handleGetTemplate(dataType, format)
                  } else {
                    message.warning('请先选择数据类型和格式')
                  }
                }}
              >
                下载模板
              </Button>
            </Space>
          </Form.Item>

          {loading && (
            <div style={{ marginTop: '16px' }}>
              <Text>导出进度：</Text>
              <Progress percent={exportProgress} status="active" />
            </div>
          )}
        </Form>
      </Card>

      {/* 导入功能 */}
      <Card title="数据导入" style={{ marginBottom: '24px' }}>
        <Form
          form={importForm}
          layout="vertical"
          onFinish={handleImport}
        >
          <Row gutter={[16, 16]}>
            <Col span={8}>
              <Form.Item
                label="数据类型"
                name="dataType"
                rules={[{ required: true, message: '请选择数据类型' }]}
              >
                <Select placeholder="选择要导入的数据类型">
                  {dataTypes.filter(t => t.value !== 'all').map(type => (
                    <Option key={type.value} value={type.value}>{type.label}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item label="选择文件">
                <Upload
                  beforeUpload={beforeUpload}
                  fileList={uploadFileList}
                  onRemove={() => setUploadFileList([])}
                  maxCount={1}
                  accept=".csv,.json"
                >
                  <Button icon={<UploadOutlined />}>选择文件</Button>
                </Upload>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="overwrite" valuePropName="checked">
                <Checkbox>覆盖现有数据</Checkbox>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} icon={<ImportOutlined />}>
              开始导入
            </Button>
          </Form.Item>

          {loading && (
            <div style={{ marginTop: '16px' }}>
              <Text>导入进度：</Text>
              <Progress percent={importProgress} status="active" />
            </div>
          )}
        </Form>

        <Alert
          message="导入说明"
          description={
            <div>
              <p>• 支持CSV和JSON格式文件</p>
              <p>• 文件大小不超过10MB</p>
              <p>• 请确保数据格式与模板一致</p>
              <p>• 建议先下载模板查看格式要求</p>
            </div>
          }
          type="info"
          showIcon
          style={{ marginTop: '16px' }}
        />
      </Card>

      {/* 导出历史 */}
      <Card title="导出历史" style={{ marginBottom: '24px' }}>
        <Table
          columns={exportColumns}
          dataSource={exportResults}
          rowKey="export_time"
          pagination={false}
          size="small"
        />
      </Card>

      {/* 导入历史 */}
      <Card title="导入历史">
        <Table
          columns={importColumns}
          dataSource={importResults}
          rowKey="import_time"
          pagination={false}
          size="small"
          expandable={{
            expandedRowRender: (record) => (
              <div>
                <Text strong>错误信息：</Text>
                {record.errors && record.errors.length > 0 ? (
                  <List
                    size="small"
                    dataSource={record.errors}
                    renderItem={(error, index) => (
                      <List.Item key={index}>
                        <Text type="danger">{error}</Text>
                      </List.Item>
                    )}
                  />
                ) : (
                  <Text type="secondary">无错误信息</Text>
                )}
              </div>
            ),
            rowExpandable: record => record.errors && record.errors.length > 0
          }}
        />
      </Card>

      {/* 模板预览模态框 */}
      <Modal
        title="导入模板"
        open={templateModalVisible}
        onCancel={() => setTemplateModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setTemplateModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={800}
      >
        <Alert
          message="模板说明"
          description="这是标准的数据导入模板，请按照此格式准备您的数据文件"
          type="info"
          showIcon
          style={{ marginBottom: '16px' }}
        />
        <TextArea
          value={templateContent}
          rows={20}
          readOnly
          style={{ fontFamily: 'monospace' }}
        />
      </Modal>

      {/* 导入模板模态框 */}
      <Modal
        title="导入模板下载"
        open={previewModalVisible}
        onCancel={() => setPreviewModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setPreviewModalVisible(false)}>
            关闭
          </Button>
        ]}
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <Text strong>选择模板类型：</Text>
            <div style={{ marginTop: '16px' }}>
              {dataTypes.filter(t => t.value !== 'all').map(dataType => (
                <div key={dataType.value} style={{ marginBottom: '16px' }}>
                  <Text strong>{dataType.label}</Text>
                  <div style={{ marginTop: '8px' }}>
                    {formats.map(format => (
                      <Button
                        key={format.value}
                        size="small"
                        style={{ marginRight: '8px', marginBottom: '8px' }}
                        onClick={() => handleGetTemplate(dataType.value, format.value)}
                      >
                        <DownloadOutlined />
                        {format.label}
                      </Button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <Divider />

          <Alert
            message="使用说明"
            description={
              <div>
                <p>1. 下载对应数据类型的模板文件</p>
                <p>2. 按照模板格式填写您的数据</p>
                <p>3. 确保数据完整性和格式正确性</p>
                <p>4. 使用导入功能上传文件</p>
              </div>
            }
            type="info"
            showIcon
          />
        </Space>
      </Modal>
    </div>
  )
}

export default DataImportExportPage