import React, { useState, useEffect } from 'react'
import {
  Card,
  Row,
  Col,
  Table,
  Button,
  Space,
  Input,
  InputNumber,
  Switch,
  Modal,
  Form,
  message,
  Typography,
  Tag,
  Tabs,
  Divider,
  Popconfirm
} from 'antd'
import {
  SettingOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SaveOutlined,
  ReloadOutlined,
  CalculatorOutlined
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import apiService, { SignalConfig, SignalCombo } from '../services/api'

const { Title, Text } = Typography
const { TabPane } = Tabs

const SignalConfigPage: React.FC = () => {
  const [signalConfigs, setSignalConfigs] = useState<SignalConfig[]>([])
  const [signalCombos, setSignalCombos] = useState<SignalCombo[]>([])
  const [loading, setLoading] = useState(false)
  const [editModalVisible, setEditModalVisible] = useState(false)
  const [comboModalVisible, setComboModalVisible] = useState(false)
  const [editingConfig, setEditingConfig] = useState<SignalConfig | null>(null)
  const [editingCombo, setEditingCombo] = useState<SignalCombo | null>(null)
  const [form] = Form.useForm()
  const [comboForm] = Form.useForm()

  useEffect(() => {
    loadSignalConfigs()
    loadSignalCombos()
  }, [])

  const loadSignalConfigs = async () => {
    try {
      const response = await apiService.getSignalConfigs()
      if (response.success) {
        setSignalConfigs(response.data)
      }
    } catch (error) {
      console.error('加载信号配置失败:', error)
      message.error('加载信号配置失败')
    }
  }

  const loadSignalCombos = async () => {
    try {
      const response = await apiService.getSignalCombos()
      if (response.success) {
        setSignalCombos(response.data)
      }
    } catch (error) {
      console.error('加载信号组合失败:', error)
      message.error('加载信号组合失败')
    }
  }

  const handleEditConfig = (config: SignalConfig) => {
    setEditingConfig(config)
    form.setFieldsValue(config)
    setEditModalVisible(true)
  }

  const handleSaveConfig = async () => {
    if (!editingConfig) return

    try {
      const values = await form.validateFields()
      const updatedConfig = { ...editingConfig, ...values }

      const response = await apiService.updateSignalConfig(updatedConfig)
      if (response.success) {
        message.success('信号配置更新成功')
        setEditModalVisible(false)
        setEditingConfig(null)
        loadSignalConfigs()
      } else {
        message.error('信号配置更新失败')
      }
    } catch (error) {
      console.error('更新信号配置失败:', error)
      message.error('更新信号配置失败')
    }
  }

  const handleEditCombo = (combo: SignalCombo) => {
    setEditingCombo(combo)
    comboForm.setFieldsValue({
      name: combo.name,
      description: combo.description,
      enabled: combo.enabled,
      signals: combo.signals
    })
    setComboModalVisible(true)
  }

  const handleSaveCombo = async () => {
    if (!editingCombo) return

    try {
      const values = await comboForm.validateFields()
      const updatedCombo = {
        ...editingCombo,
        ...values,
        signals: values.signals || editingCombo.signals
      }

      const response = await apiService.updateSignalCombo(updatedCombo)
      if (response.success) {
        message.success('信号组合更新成功')
        setComboModalVisible(false)
        setEditingCombo(null)
        loadSignalCombos()
      } else {
        message.error('信号组合更新失败')
      }
    } catch (error) {
      console.error('更新信号组合失败:', error)
      message.error('更新信号组合失败')
    }
  }

  const handleCalculateScore = async (comboID: number, comboName: string) => {
    try {
      setLoading(true)
      const response = await apiService.calculateComboScore(comboID, '000001')
      if (response.success) {
        const { score } = response.data
        message.success(`${comboName} 组合分数: ${score.toFixed(2)}`)
      }
    } catch (error) {
      console.error('计算组合分数失败:', error)
      message.error('计算组合分数失败')
    } finally {
      setLoading(false)
    }
  }

  const configColumns: ColumnsType<SignalConfig> = [
    {
      title: '信号类型',
      dataIndex: 'signal_type',
      key: 'signal_type',
      render: (text) => <Text strong>{text}</Text>
    },
    {
      title: '权重',
      dataIndex: 'weight',
      key: 'weight',
      render: (text) => <Tag color="blue">{text}</Tag>
    },
    {
      title: '状态',
      dataIndex: 'enabled',
      key: 'enabled',
      render: (enabled) => (
        <Tag color={enabled ? 'green' : 'red'}>
          {enabled ? '启用' : '禁用'}
        </Tag>
      )
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description'
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEditConfig(record)}
          >
            编辑
          </Button>
        </Space>
      )
    }
  ]

  const comboColumns: ColumnsType<SignalCombo> = [
    {
      title: '组合名称',
      dataIndex: 'name',
      key: 'name',
      render: (text) => <Text strong>{text}</Text>
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description'
    },
    {
      title: '信号数量',
      dataIndex: 'signals',
      key: 'signal_count',
      render: (signals) => <Tag color="orange">{signals.length}</Tag>
    },
    {
      title: '状态',
      dataIndex: 'enabled',
      key: 'enabled',
      render: (enabled) => (
        <Tag color={enabled ? 'green' : 'red'}>
          {enabled ? '启用' : '禁用'}
        </Tag>
      )
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEditCombo(record)}
          >
            编辑
          </Button>
          <Button
            type="link"
            size="small"
            icon={<CalculatorOutlined />}
            loading={loading}
            onClick={() => handleCalculateScore(record.id, record.name)}
          >
            计算分数
          </Button>
        </Space>
      )
    }
  ]

  return (
    <div style={{ padding: '24px', background: '#f5f5f5', minHeight: '100vh' }}>
      <Title level={2}>
        <SettingOutlined /> 信号配置管理
      </Title>

      <Tabs defaultActiveKey="configs">
        <TabPane tab="信号配置" key="configs">
          <Card
            title="信号权重配置"
            extra={
              <Button
                icon={<ReloadOutlined />}
                onClick={loadSignalConfigs}
              >
                刷新
              </Button>
            }
          >
            <Table
              columns={configColumns}
              dataSource={signalConfigs}
              rowKey="id"
              pagination={false}
              size="small"
            />
          </Card>
        </TabPane>

        <TabPane tab="信号组合" key="combos">
          <Card
            title="信号组合策略"
            extra={
              <Button
                icon={<ReloadOutlined />}
                onClick={loadSignalCombos}
              >
                刷新
              </Button>
            }
          >
            <Table
              columns={comboColumns}
              dataSource={signalCombos}
              rowKey="id"
              pagination={false}
              size="small"
              expandable={{
                expandedRowRender: (record) => (
                  <div style={{ margin: 0 }}>
                    <Title level={5}>包含信号:</Title>
                    <Row gutter={[16, 16]}>
                      {record.signals.map((signal, index) => (
                        <Col span={8} key={index}>
                          <Card size="small">
                            <Text strong>{signal.signal_type}</Text>
                            <br />
                            <Text type="secondary">权重: {signal.weight}</Text>
                            <br />
                            <Tag color={signal.enabled ? 'green' : 'red'}>
                              {signal.enabled ? '启用' : '禁用'}
                            </Tag>
                          </Card>
                        </Col>
                      ))}
                    </Row>
                  </div>
                ),
                rowExpandable: record => record.signals.length > 0
              }}
            />
          </Card>
        </TabPane>
      </Tabs>

      {/* 编辑信号配置模态框 */}
      <Modal
        title="编辑信号配置"
        open={editModalVisible}
        onOk={handleSaveConfig}
        onCancel={() => setEditModalVisible(false)}
        footer={[
          <Button key="cancel" onClick={() => setEditModalVisible(false)}>
            取消
          </Button>,
          <Button key="save" type="primary" icon={<SaveOutlined />} onClick={handleSaveConfig}>
            保存
          </Button>
        ]}
      >
        <Form form={form} layout="vertical">
          <Form.Item label="信号类型" name="signal_type">
            <Input disabled />
          </Form.Item>
          <Form.Item
            label="权重"
            name="weight"
            rules={[{ required: true, message: '请输入权重' }]}
          >
            <InputNumber min={0} max={5} step={0.1} precision={1} />
          </Form.Item>
          <Form.Item label="状态" name="enabled" valuePropName="checked">
            <Switch checkedChildren="启用" unCheckedChildren="禁用" />
          </Form.Item>
          <Form.Item label="描述" name="description">
            <Input.TextArea rows={3} />
          </Form.Item>
        </Form>
      </Modal>

      {/* 编辑信号组合模态框 */}
      <Modal
        title="编辑信号组合"
        open={comboModalVisible}
        onOk={handleSaveCombo}
        onCancel={() => setComboModalVisible(false)}
        width={800}
        footer={[
          <Button key="cancel" onClick={() => setComboModalVisible(false)}>
            取消
          </Button>,
          <Button key="save" type="primary" icon={<SaveOutlined />} onClick={handleSaveCombo}>
            保存
          </Button>
        ]}
      >
        <Form form={comboForm} layout="vertical">
          <Form.Item
            label="组合名称"
            name="name"
            rules={[{ required: true, message: '请输入组合名称' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item label="描述" name="description">
            <Input.TextArea rows={3} />
          </Form.Item>
          <Form.Item label="状态" name="enabled" valuePropName="checked">
            <Switch checkedChildren="启用" unCheckedChildren="禁用" />
          </Form.Item>
          <Divider>包含信号</Divider>
          <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
            {editingCombo?.signals.map((signal, index) => (
              <Card key={index} size="small" style={{ marginBottom: '8px' }}>
                <Row justify="space-between" align="middle">
                  <Col>
                    <Text strong>{signal.signal_type}</Text>
                    <br />
                    <Text type="secondary">{signal.description}</Text>
                  </Col>
                  <Col>
                    <InputNumber
                      min={0}
                      max={5}
                      step={0.1}
                      precision={1}
                      defaultValue={signal.weight}
                      onChange={(value) => {
                        const updatedSignals = [...editingCombo.signals]
                        updatedSignals[index].weight = value || 0
                        setEditingCombo({ ...editingCombo, signals: updatedSignals })
                      }}
                    />
                    <Switch
                      style={{ marginLeft: '8px' }}
                      defaultChecked={signal.enabled}
                      onChange={(checked) => {
                        const updatedSignals = [...editingCombo.signals]
                        updatedSignals[index].enabled = checked
                        setEditingCombo({ ...editingCombo, signals: updatedSignals })
                      }}
                    />
                  </Col>
                </Row>
              </Card>
            ))}
          </div>
        </Form>
      </Modal>
    </div>
  )
}

export default SignalConfigPage