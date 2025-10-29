import React, { useState } from 'react';
import {
  Modal,
  Table,
  Button,
  Space,
  Tag,
  Typography,
  Input,
  Select,
  DatePicker,
  Rate,
  Tooltip,
  Popconfirm,
  Card,
  Row,
  Col,
  Statistic,
  Empty,
  message
} from 'antd';
import {
  HistoryOutlined,
  SearchOutlined,
  DeleteOutlined,
  ExportOutlined,
  EyeOutlined,
  CalendarOutlined,
  UserOutlined,
  RobotOutlined,
  FilterOutlined,
  ClearOutlined
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import dayjs from 'dayjs';

import { api } from '@/services/api';
import { formatDateTime, formatPercent } from '@/utils/format';
import AIAnalysisResult from './AIAnalysisResult';

const { Title, Text } = Typography;
const { Search } = Input;
const { RangePicker } = DatePicker;

interface AIHistoryManagerProps {
  visible: boolean;
  onClose: () => void;
}

// 分析师角色映射
const ANALYST_ROLES = {
  technical_analyst: { name: '技术分析师', icon: '📈', color: '#1890ff' },
  fundamental_analyst: { name: '基本面分析师', icon: '💼', color: '#52c41a' },
  news_analyst: { name: '新闻分析师', icon: '📰', color: '#fa8c16' },
  risk_analyst: { name: '风控分析师', icon: '🛡️', color: '#f5222d' }
};

const AIHistoryManager: React.FC<AIHistoryManagerProps> = ({
  visible,
  onClose
}) => {
  const [searchText, setSearchText] = useState('');
  const [selectedSymbol, setSelectedSymbol] = useState('');
  const [selectedRole, setSelectedRole] = useState('');
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs] | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [selectedRecord, setSelectedRecord] = useState<any>(null);
  const [detailVisible, setDetailVisible] = useState(false);

  const queryClient = useQueryClient();

  // 获取分析历史
  const { data: historyData, isLoading: historyLoading } = useQuery({
    queryKey: ['ai-analysis-history', currentPage, pageSize, selectedSymbol, selectedRole, dateRange],
    queryFn: async () => {
      const params: any = {
        limit: pageSize,
        offset: (currentPage - 1) * pageSize
      };

      if (selectedSymbol) params.symbol = selectedSymbol;
      if (selectedRole) params.role = selectedRole;
      if (dateRange) {
        params.start_date = dateRange[0].toISOString();
        params.end_date = dateRange[1].toISOString();
      }
      if (searchText) params.search = searchText;

      const response = await api.get('/api/ai/history', { params });
      return response.data;
    },
    enabled: visible,
  });

  // 获取统计信息
  const { data: statistics } = useQuery({
    queryKey: ['ai-analysis-statistics'],
    queryFn: async () => {
      const response = await api.get('/api/ai/history', { params: { limit: 1000 } });
      const data = response.data.data || [];

      const stats = {
        total: data.length,
        byRole: {} as Record<string, number>,
        bySymbol: {} as Record<string, number>,
        avgConfidence: 0,
        recentActivity: data.slice(0, 10)
      };

      data.forEach((item: any) => {
        stats.byRole[item.role] = (stats.byRole[item.role] || 0) + 1;
        stats.bySymbol[item.symbol] = (stats.bySymbol[item.symbol] || 0) + 1;
        stats.avgConfidence += item.confidence || 0;
      });

      stats.avgConfidence = stats.total > 0 ? stats.avgConfidence / stats.total : 0;

      return stats;
    },
    enabled: visible,
  });

  // 删除记录
  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/api/ai/history/${id}`);
    },
    onSuccess: () => {
      message.success('删除成功');
      queryClient.invalidateQueries({ queryKey: ['ai-analysis-history'] });
      queryClient.invalidateQueries({ queryKey: ['ai-analysis-statistics'] });
    },
    onError: (error: any) => {
      message.error(`删除失败: ${error.message}`);
    }
  });

  // 清空筛选条件
  const handleClearFilters = () => {
    setSearchText('');
    setSelectedSymbol('');
    setSelectedRole('');
    setDateRange(null);
    setCurrentPage(1);
  };

  // 查看详情
  const handleViewDetail = (record: any) => {
    setSelectedRecord(record);
    setDetailVisible(true);
  };

  // 删除记录
  const handleDelete = (id: number) => {
    deleteMutation.mutate(id);
  };

  // 导出数据
  const handleExport = () => {
    const data = historyData?.data || [];
    if (data.length === 0) {
      message.warning('暂无数据可导出');
      return;
    }

    const csvContent = [
      ['时间', '股票代码', '分析师', '问题', '回答', '置信度'].join(','),
      ...data.map((item: any) => [
        formatDateTime(item.created_at),
        item.symbol,
        ANALYST_ROLES[item.role as keyof typeof ANALYST_ROLES]?.name || item.role,
        `"${item.question.replace(/"/g, '""')}"`,
        `"${item.answer.replace(/"/g, '""').substring(0, 100)}..."`,
        `${(item.confidence * 100).toFixed(1)}%`
      ].join(','))
    ].join('\n');

    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `AI分析历史_${dayjs().format('YYYY-MM-DD')}.csv`;
    link.click();
    URL.revokeObjectURL(link);
  };

  // 表格列定义
  const columns = [
    {
      title: '时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      render: (text: string) => formatDateTime(text),
      sorter: true
    },
    {
      title: '股票代码',
      dataIndex: 'symbol',
      key: 'symbol',
      width: 100,
      render: (text: string) => (
        <Tag color="blue" className="font-mono">{text}</Tag>
      ),
      filterDropdown: ({ setSelectedKeys, selectedKeys, confirm }: any) => (
        <div style={{ padding: 8 }}>
          <Input
            placeholder="股票代码"
            value={selectedKeys[0]}
            onChange={(e) => setSelectedKeys(e.target.value ? [e.target.value] : [])}
            onPressEnter={() => confirm()}
            style={{ width: 200, marginBottom: 8, display: 'block' }}
          />
          <Button
            type="primary"
            onClick={() => confirm()}
            size="small"
            style={{ width: 90, marginRight: 8 }}
          >
            筛选
          </Button>
          <Button
            onClick={() => setSelectedKeys([])}
            size="small"
            style={{ width: 90 }}
          >
            重置
          </Button>
        </div>
      )
    },
    {
      title: '分析师',
      dataIndex: 'role',
      key: 'role',
      width: 120,
      render: (role: string) => {
        const roleInfo = ANALYST_ROLES[role as keyof typeof ANALYST_ROLES];
        return roleInfo ? (
          <Tag color={roleInfo.color}>
            {roleInfo.icon} {roleInfo.name}
          </Tag>
        ) : role;
      },
      filters: Object.entries(ANALYST_ROLES).map(([key, value]) => ({
        text: `${value.icon} ${value.name}`,
        value: key
      }))
    },
    {
      title: '问题',
      dataIndex: 'question',
      key: 'question',
      ellipsis: true,
      render: (text: string) => (
        <Tooltip title={text}>
          <Text className="text-sm">{text}</Text>
        </Tooltip>
      )
    },
    {
      title: '回答预览',
      dataIndex: 'answer',
      key: 'answer',
      width: 200,
      ellipsis: true,
      render: (text: string) => (
        <Tooltip title={text}>
          <Text className="text-sm text-gray-600">{text.substring(0, 50)}...</Text>
        </Tooltip>
      )
    },
    {
      title: '置信度',
      dataIndex: 'confidence',
      key: 'confidence',
      width: 100,
      render: (confidence: number) => (
        <div className="flex items-center space-x-1">
          <Rate
            disabled
            count={5}
            value={confidence * 5}
            className="text-xs"
          />
          <Text className="text-xs">{(confidence * 100).toFixed(0)}%</Text>
        </div>
      ),
      sorter: true
    },
    {
      title: '操作',
      key: 'actions',
      width: 120,
      render: (text: any, record: any) => (
        <Space>
          <Tooltip title="查看详情">
            <Button
              type="text"
              size="small"
              icon={<EyeOutlined />}
              onClick={() => handleViewDetail(record)}
            />
          </Tooltip>
          <Popconfirm
            title="确定要删除这条记录吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Tooltip title="删除">
              <Button
                type="text"
                size="small"
                danger
                icon={<DeleteOutlined />}
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      )
    }
  ];

  return (
    <>
      <Modal
        title={
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <HistoryOutlined />
              <span>AI分析历史记录</span>
            </div>
            <Space>
              <Button
                icon={<ExportOutlined />}
                onClick={handleExport}
                disabled={!historyData?.data?.length}
              >
                导出
              </Button>
              <Button
                icon={<ClearOutlined />}
                onClick={handleClearFilters}
              >
                清空筛选
              </Button>
            </Space>
          </div>
        }
        open={visible}
        onCancel={onClose}
        width={1200}
        footer={null}
        destroyOnClose
      >
        {/* 统计信息 */}
        {statistics && (
          <Row gutter={16} className="mb-4">
            <Col span={6}>
              <Card size="small">
                <Statistic
                  title="总分析次数"
                  value={statistics.total}
                  prefix={<RobotOutlined />}
                />
              </Card>
            </Col>
            <Col span={6}>
              <Card size="small">
                <Statistic
                  title="平均置信度"
                  value={statistics.avgConfidence * 100}
                  suffix="%"
                  precision={1}
                  prefix={<UserOutlined />}
                />
              </Card>
            </Col>
            <Col span={6}>
              <Card size="small">
                <Statistic
                  title="分析股票数"
                  value={Object.keys(statistics.bySymbol).length}
                  prefix={<CalendarOutlined />}
                />
              </Card>
            </Col>
            <Col span={6}>
              <Card size="small">
                <Statistic
                  title="活跃分析师"
                  value={Object.keys(statistics.byRole).length}
                  prefix={<UserOutlined />}
                />
              </Card>
            </Col>
          </Row>
        )}

        {/* 筛选条件 */}
        <Card className="mb-4" size="small">
          <Row gutter={16} align="middle">
            <Col flex="auto">
              <Space wrap>
                <Search
                  placeholder="搜索分析内容"
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                  style={{ width: 200 }}
                  allowClear
                />
                <Input
                  placeholder="股票代码"
                  value={selectedSymbol}
                  onChange={(e) => setSelectedSymbol(e.target.value.toUpperCase())}
                  style={{ width: 120 }}
                  maxLength={6}
                />
                <Select
                  placeholder="分析师角色"
                  value={selectedRole}
                  onChange={setSelectedRole}
                  style={{ width: 150 }}
                  allowClear
                >
                  {Object.entries(ANALYST_ROLES).map(([key, value]) => (
                    <Option key={key} value={key}>
                      {value.icon} {value.name}
                    </Option>
                  ))}
                </Select>
                <RangePicker
                  value={dateRange}
                  onChange={setDateRange}
                  format="YYYY-MM-DD"
                  placeholder={['开始日期', '结束日期']}
                />
              </Space>
            </Col>
            <Col>
              <Button
                type="primary"
                icon={<SearchOutlined />}
                onClick={() => setCurrentPage(1)}
              >
                搜索
              </Button>
            </Col>
          </Row>
        </Card>

        {/* 数据表格 */}
        <Table
          columns={columns}
          dataSource={historyData?.data || []}
          loading={historyLoading}
          rowKey="id"
          pagination={{
            current: currentPage,
            pageSize: pageSize,
            total: historyData?.total || 0,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) =>
              `第 ${range[0]}-${range[1]} 条，共 ${total} 条记录`,
            onChange: (page, size) => {
              setCurrentPage(page);
              setPageSize(size);
            }
          }}
          size="small"
          scroll={{ x: 1000 }}
        />

        {/* 空状态 */}
        {!historyLoading && (!historyData?.data || historyData.data.length === 0) && (
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description="暂无分析记录"
            className="py-8"
          />
        )}
      </Modal>

      {/* 详情弹窗 */}
      <Modal
        title="分析详情"
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        width={800}
        footer={null}
        destroyOnClose
      >
        {selectedRecord && (
          <AIAnalysisResult
            data={selectedRecord}
            showActions={false}
          />
        )}
      </Modal>
    </>
  );
};

export default AIHistoryManager;