import React, { useState } from 'react';
import {
  Modal,
  Button,
  Form,
  Select,
  DatePicker,
  Switch,
  Space,
  Typography,
  Card,
  Progress,
  Alert,
  Checkbox,
  Radio,
  Divider,
  Row,
  Col,
  Statistic
} from 'antd';
import {
  FileTextOutlined,
  DownloadOutlined,
  EyeOutlined,
  LoadingOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import { useMutation, useQuery } from '@tanstack/react-query';
import dayjs from 'dayjs';

import { api } from '@/services/api';
import { formatDateTime } from '@/utils/format';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { RangePicker } = DatePicker;

interface AIReportGeneratorProps {
  visible: boolean;
  onClose: () => void;
  defaultSymbol?: string;
}

const AIReportGenerator: React.FC<AIReportGeneratorProps> = ({
  visible,
  onClose,
  defaultSymbol = ''
}) => {
  const [form] = Form.useForm();
  const [reportFormat, setReportFormat] = useState('markdown');
  const [reportType, setReportType] = useState('comprehensive');
  const [selectedRoles, setSelectedRoles] = useState<string[]>([]);
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs] | null>(null);
  const [includeCharts, setIncludeCharts] = useState(true);
  const [includeHistory, setIncludeHistory] = useState(true);
  const [includeSuggestions, setIncludeSuggestions] = useState(true);

  // 获取AI分析历史
  const { data: analysisHistory = [], isLoading: historyLoading } = useQuery({
    queryKey: ['ai-analysis-history'],
    queryFn: async () => {
      const response = await api.get('/api/ai/history', {
        params: { limit: 100 }
      });
      return response.data.data || [];
    },
    enabled: visible,
  });

  // 获取可用的分析师角色
  const { data: availableRoles = [] } = useQuery({
    queryKey: ['ai-roles'],
    queryFn: async () => {
      const response = await api.get('/api/ai/roles');
      return response.data.roles || [];
    },
    enabled: visible,
  });

  // 生成报告
  const reportMutation = useMutation({
    mutationFn: async (values: any) => {
      const params = {
        symbol: values.symbol,
        format: reportFormat,
        report_type: reportType,
        roles: selectedRoles,
        date_range: dateRange ? [dateRange[0].toISOString(), dateRange[1].toISOString()] : null,
        include_charts: includeCharts,
        include_history: includeHistory,
        include_suggestions: includeSuggestions,
        analysis_ids: values.analysis_ids || null
      };

      const response = await api.post('/api/ai/export', params);
      return response.data;
    },
    onSuccess: (data, variables) => {
      // 下载报告
      const blob = new Blob([data], {
        type: reportFormat === 'markdown' ? 'text/markdown' : 'text/html'
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${variables.symbol}_AI分析报告_${dayjs().format('YYYY-MM-DD')}.${reportFormat}`;
      link.click();
      URL.revokeObjectURL(url);

      Modal.success({
        title: '报告生成成功',
        content: 'AI分析报告已生成并开始下载',
      });
    },
    onError: (error: any) => {
      Modal.error({
        title: '报告生成失败',
        content: error.response?.data?.message || error.message,
      });
    }
  });

  // 处理表单提交
  const handleSubmit = async (values: any) => {
    if (selectedRoles.length === 0) {
      Modal.warning({
        title: '请选择分析师',
        content: '请至少选择一个分析师角色来生成报告',
      });
      return;
    }

    reportMutation.mutate(values);
  };

  // 获取统计信息
  const getStatistics = () => {
    if (!analysisHistory.length) return null;

    const symbolAnalysis = analysisHistory.reduce((acc: any, item: any) => {
      if (!acc[item.symbol]) {
        acc[item.symbol] = { count: 0, roles: [] };
      }
      acc[item.symbol].count++;
      if (!acc[item.symbol].roles.includes(item.role)) {
        acc[item.symbol].roles.push(item.role);
      }
      return acc;
    }, {});

    const totalAnalyses = analysisHistory.length;
    const totalSymbols = Object.keys(symbolAnalysis).length;
    const avgConfidence = analysisHistory.reduce((sum: number, item: any) =>
      sum + (item.confidence || 0), 0) / totalAnalyses;

    return {
      totalAnalyses,
      totalSymbols,
      avgConfidence,
      symbolAnalysis
    };
  };

  const statistics = getStatistics();

  const roleOptions = availableRoles.map((role: any) => ({
    label: (
      <div className="flex items-center space-x-2">
        <span>{role.name}</span>
        <Text type="secondary" className="text-xs">{role.description}</Text>
      </div>
    ),
    value: role.value
  }));

  return (
    <Modal
      title={
        <div className="flex items-center space-x-2">
          <FileTextOutlined />
          <span>AI分析报告生成器</span>
        </div>
      }
      open={visible}
      onCancel={onClose}
      width={700}
      footer={[
        <Button key="cancel" onClick={onClose}>
          取消
        </Button>,
        <Button
          key="preview"
          icon={<EyeOutlined />}
          onClick={() => form.submit()}
        >
          预览报告
        </Button>,
        <Button
          key="generate"
          type="primary"
          icon={<DownloadOutlined />}
          loading={reportMutation.isLoading}
          onClick={() => form.submit()}
        >
          生成并下载
        </Button>
      ]}
      destroyOnClose
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={{
          symbol: defaultSymbol,
          report_type: 'comprehensive'
        }}
      >
        {/* 统计信息 */}
        {statistics && (
          <Card className="mb-4" size="small">
            <Title level={5}>分析统计</Title>
            <Row gutter={16}>
              <Col span={8}>
                <Statistic
                  title="总分析次数"
                  value={statistics.totalAnalyses}
                  prefix={<FileTextOutlined />}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="分析股票数"
                  value={statistics.totalSymbols}
                  prefix={<FileTextOutlined />}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="平均置信度"
                  value={statistics.avgConfidence * 100}
                  suffix="%"
                  precision={1}
                />
              </Col>
            </Row>
          </Card>
        )}

        {/* 基本配置 */}
        <Card className="mb-4" size="small" title="基本配置">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="股票代码"
                name="symbol"
                rules={[{ required: true, message: '请输入股票代码' }]}
              >
                <Select
                  placeholder="选择或输入股票代码"
                  showSearch
                  allowClear
                  options={statistics ? Object.keys(statistics.symbolAnalysis).map(symbol => ({
                    label: `${symbol} (${statistics.symbolAnalysis[symbol].count}次分析)`,
                    value: symbol
                  })) : []}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="报告格式">
                <Radio.Group value={reportFormat} onChange={(e) => setReportFormat(e.target.value)}>
                  <Radio.Button value="markdown">Markdown</Radio.Button>
                  <Radio.Button value="html">HTML</Radio.Button>
                </Radio.Group>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="报告类型">
                <Radio.Group value={reportType} onChange={(e) => setReportType(e.target.value)}>
                  <Radio.Button value="comprehensive">综合报告</Radio.Button>
                  <Radio.Button value="summary">简要报告</Radio.Button>
                </Radio.Group>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="时间范围">
                <RangePicker
                  value={dateRange}
                  onChange={setDateRange}
                  format="YYYY-MM-DD"
                  placeholder={['开始日期', '结束日期']}
                />
              </Form.Item>
            </Col>
          </Row>
        </Card>

        {/* 分析师选择 */}
        <Card className="mb-4" size="small" title="分析师选择">
          <Form.Item label="选择分析师角色">
            <Checkbox.Group
              value={selectedRoles}
              onChange={setSelectedRoles}
            >
              <Row>
                {roleOptions.map((option) => (
                  <Col span={12} key={option.value} className="mb-2">
                    <Checkbox value={option.value}>
                      {option.label}
                    </Checkbox>
                  </Col>
                ))}
              </Row>
            </Checkbox.Group>
          </Form.Item>

          <div className="flex justify-between">
            <Button
              size="small"
              onClick={() => setSelectedRoles(availableRoles.map((r: any) => r.value))}
            >
              全选
            </Button>
            <Button
              size="small"
              onClick={() => setSelectedRoles([])}
            >
              清空
            </Button>
          </div>
        </Card>

        {/* 内容选项 */}
        <Card className="mb-4" size="small" title="内容选项">
          <Row gutter={16}>
            <Col span={8}>
              <Space direction="vertical">
                <Checkbox
                  checked={includeCharts}
                  onChange={(e) => setIncludeCharts(e.target.checked)}
                >
                  包含图表
                </Checkbox>
                <Checkbox
                  checked={includeHistory}
                  onChange={(e) => setIncludeHistory(e.target.checked)}
                >
                  包含历史记录
                </Checkbox>
                <Checkbox
                  checked={includeSuggestions}
                  onChange={(e) => setIncludeSuggestions(e.target.checked)}
                >
                  包含投资建议
                </Checkbox>
              </Space>
            </Col>
            <Col span={16}>
              <Alert
                message="报告内容说明"
                description={
                  <div className="text-sm">
                    <p>• <strong>包含图表</strong>: 生成分析结果的数据可视化图表</p>
                    <p>• <strong>包含历史记录</strong>: 展示相关的历史分析记录</p>
                    <p>• <strong>包含投资建议</strong>: 提供基于分析结果的具体建议</p>
                  </div>
                }
                type="info"
                showIcon
              />
            </Col>
          </Row>
        </Card>

        {/* 预览区域 */}
        <Card size="small" title="报告预览">
          <div className="p-4 bg-gray-50 rounded">
            <Title level={4}>
              {form.getFieldValue('symbol') || '股票代码'} - AI投资分析报告
            </Title>
            <Text type="secondary">
              生成时间: {formatDateTime(new Date())}
            </Text>
            <Divider />
            <Paragraph>
              本报告基于智股通AI分析师团队的专业分析，整合了{selectedRoles.length}个分析师角色的观点。
            </Paragraph>

            {selectedRoles.length > 0 && (
              <div>
                <Text strong>包含的分析师：</Text>
                <div className="mt-2">
                  {selectedRoles.map(role => {
                    const roleInfo = availableRoles.find((r: any) => r.value === role);
                    return roleInfo ? (
                      <Tag key={role} color="blue" className="mb-1">
                        {roleInfo.name}
                      </Tag>
                    ) : null;
                  })}
                </div>
              </div>
            )}
          </div>
        </Card>

        {/* 生成进度 */}
        {reportMutation.isLoading && (
          <Card size="small" className="mt-4">
            <div className="flex items-center space-x-3">
              <LoadingOutlined className="text-blue-500" />
              <div className="flex-1">
                <Text>正在生成AI分析报告...</Text>
                <Progress percent={66} showInfo={false} className="mt-2" />
              </div>
            </div>
          </Card>
        )}
      </Form>

      {/* 报告说明 */}
      <Alert
        className="mt-4"
        message="报告生成说明"
        description={
          <div className="text-sm">
            <p>• AI分析报告基于智股通的多角色AI分析师系统生成</p>
            <p>• 报告内容仅供参考，不构成投资建议</p>
            <p>• 投资有风险，入市需谨慎，请结合自身情况做出决策</p>
          </div>
        }
        type="warning"
        showIcon
      />
    </Modal>
  );
};

export default AIReportGenerator;