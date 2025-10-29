import React, { useState } from 'react';
import {
  Card,
  Button,
  Avatar,
  Typography,
  Space,
  Tag,
  Divider,
  Row,
  Col,
  Statistic,
  Progress,
  Tooltip,
  List,
  Rate,
  Empty,
  Badge
} from 'antd';
import {
  RobotOutlined,
  MessageOutlined,
  StarOutlined,
  TrendingUpOutlined,
  AlertOutlined,
  BulbOutlined,
  HistoryOutlined,
  ExpandOutlined,
  TeamOutlined
} from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';

import AIAnalysisDialog from './AIAnalysisDialog';
import { api } from '@/services/api';
import { formatDateTime, formatPercent } from '@/utils/format';

const { Title, Text, Paragraph } = Typography;

interface AIAnalysisPanelProps {
  symbol: string;
  companyName?: string;
  onAnalysisComplete?: (result: any) => void;
}

// 分析师角色配置
const ANALYST_CONFIG = {
  technical_analyst: {
    name: '技术分析师',
    icon: '📈',
    color: '#1890ff',
    description: '基于技术指标和价格走势分析'
  },
  fundamental_analyst: {
    name: '基本面分析师',
    icon: '💼',
    color: '#52c41a',
    description: '关注公司财务和行业状况'
  },
  news_analyst: {
    name: '新闻分析师',
    icon: '📰',
    color: '#fa8c16',
    description: '基于市场情绪和政策变化'
  },
  risk_analyst: {
    name: '风控分析师',
    icon: '🛡️',
    color: '#f5222d',
    description: '专注风险评估和控制策略'
  }
};

const AIAnalysisPanel: React.FC<AIAnalysisPanelProps> = ({
  symbol,
  companyName = '',
  onAnalysisComplete
}) => {
  const [dialogVisible, setDialogVisible] = useState(false);
  const [selectedRole, setSelectedRole] = useState<string>('');

  // 获取最近的AI分析历史
  const { data: recentAnalysis = [], isLoading: historyLoading } = useQuery({
    queryKey: ['ai-analysis-history', symbol],
    queryFn: async () => {
      const response = await api.get('/api/ai/history', {
        params: { symbol, limit: 10 }
      });
      return response.data.data || [];
    },
    enabled: !!symbol,
  });

  // 获取AI服务健康状态
  const { data: healthStatus } = useQuery({
    queryKey: ['ai-health'],
    queryFn: async () => {
      const response = await api.get('/api/ai/health');
      return response.data;
    },
    refetchInterval: 60000, // 1分钟刷新一次
  });

  // 快速分析
  const handleQuickAnalysis = (role: string, question: string) => {
    setSelectedRole(role);
    setDialogVisible(true);
  };

  // 综合分析
  const handleComprehensiveAnalysis = () => {
    setSelectedRole('all');
    setDialogVisible(true);
  };

  // 统计分析结果
  const getAnalysisStats = () => {
    const roleStats: Record<string, { count: number; avgConfidence: number }> = {};

    recentAnalysis.forEach((analysis: any) => {
      if (!roleStats[analysis.role]) {
        roleStats[analysis.role] = { count: 0, avgConfidence: 0 };
      }
      roleStats[analysis.role].count++;
      roleStats[analysis.role].avgConfidence += analysis.confidence || 0;
    });

    // 计算平均置信度
    Object.keys(roleStats).forEach(role => {
      if (roleStats[role].count > 0) {
        roleStats[role].avgConfidence /= roleStats[role].count;
      }
    });

    return roleStats;
  };

  const analysisStats = getAnalysisStats();

  return (
    <>
      <Card
        title={
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <RobotOutlined className="text-blue-500" />
              <span>AI投资分析师</span>
              {healthStatus?.status === 'healthy' && (
                <Badge status="success" text="在线" />
              )}
            </div>
            <Tooltip title="展开详细分析">
              <Button
                type="text"
                size="small"
                icon={<ExpandOutlined />}
                onClick={() => setDialogVisible(true)}
              />
            </Tooltip>
          </div>
        }
        extra={
          <Button
            type="primary"
            icon={<TeamOutlined />}
            onClick={handleComprehensiveAnalysis}
          >
            综合分析
          </Button>
        }
        className="h-full"
      >
        <div className="space-y-4">
          {/* 股票信息 */}
          <div className="p-3 bg-blue-50 rounded">
            <div className="flex items-center justify-between">
              <div>
                <Title level={5} className="mb-1">
                  {symbol} {companyName && `- ${companyName}`}
                </Title>
                <Text type="secondary" className="text-sm">
                  AI智能投资分析助手
                </Text>
              </div>
              <Avatar
                style={{ backgroundColor: '#1890ff' }}
                icon={<RobotOutlined />}
                size="large"
              />
            </div>
          </div>

          {/* 快速分析按钮 */}
          <div>
            <Title level={5} className="mb-3">快速分析</Title>
            <Row gutter={[8, 8]}>
              {Object.entries(ANALYST_CONFIG).map(([key, config]) => (
                <Col span={12} key={key}>
                  <Button
                    block
                    className="h-auto py-3"
                    onClick={() => handleQuickAnalysis(key, `请对${symbol}进行${config.name}分析`)}
                  >
                    <div className="flex flex-col items-center space-y-1">
                      <span className="text-lg">{config.icon}</span>
                      <Text className="text-xs">{config.name}</Text>
                    </div>
                  </Button>
                </Col>
              ))}
            </Row>
          </div>

          <Divider />

          {/* 分析统计 */}
          {recentAnalysis.length > 0 && (
            <div>
              <Title level={5} className="mb-3 flex items-center">
                <HistoryOutlined className="mr-2" />
                最近分析
              </Title>

              <Row gutter={16} className="mb-3">
                <Col span={8}>
                  <Statistic
                    title="总分析次数"
                    value={recentAnalysis.length}
                    prefix={<MessageOutlined />}
                    valueStyle={{ fontSize: '16px' }}
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="平均置信度"
                    value={recentAnalysis.reduce((sum: number, item: any) => sum + (item.confidence || 0), 0) / recentAnalysis.length * 100}
                    suffix="%"
                    precision={1}
                    prefix={<StarOutlined />}
                    valueStyle={{ fontSize: '16px' }}
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="活跃分析师"
                    value={Object.keys(analysisStats).length}
                    prefix={<TeamOutlined />}
                    valueStyle={{ fontSize: '16px' }}
                  />
                </Col>
              </Row>

              {/* 各角色分析统计 */}
              {Object.entries(analysisStats).map(([role, stats]) => {
                const config = ANALYST_CONFIG[role as keyof typeof ANALYST_CONFIG];
                return (
                  <div key={role} className="mb-3 p-2 border rounded">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <span>{config.icon}</span>
                        <Text strong className="text-sm">{config.name}</Text>
                        <Tag color={config.color}>{stats.count}次</Tag>
                      </div>
                      <Text className="text-xs">
                        置信度 {(stats.avgConfidence * 100).toFixed(0)}%
                      </Text>
                    </div>
                    <Progress
                      percent={stats.avgConfidence * 100}
                      strokeColor={config.color}
                      showInfo={false}
                      size="small"
                    />
                  </div>
                );
              })}
            </div>
          )}

          {/* 最近分析记录 */}
          {recentAnalysis.length > 0 && (
            <div>
              <Title level={5} className="mb-3">分析记录</Title>
              <List
                size="small"
                dataSource={recentAnalysis.slice(0, 3)}
                renderItem={(item: any) => {
                  const config = ANALYST_CONFIG[item.role as keyof typeof ANALYST_CONFIG];
                  return (
                    <List.Item
                      className="cursor-pointer hover:bg-gray-50"
                      onClick={() => setDialogVisible(true)}
                    >
                      <List.Item.Meta
                        avatar={
                          <Avatar style={{ backgroundColor: config.color }}>
                            {config.icon}
                          </Avatar>
                        }
                        title={
                          <div className="flex items-center justify-between">
                            <span className="text-sm">{config.name}</span>
                            <div className="flex items-center space-x-2">
                              {item.confidence && (
                                <Rate
                                  disabled
                                  count={5}
                                  value={item.confidence * 5}
                                  className="text-xs"
                                />
                              )}
                              <Text type="secondary" className="text-xs">
                                {formatDateTime(item.created_at)}
                              </Text>
                            </div>
                          </div>
                        }
                        description={
                          <div>
                            <Text className="text-sm" ellipsis={{ tooltip: true }}>
                              {item.question}
                            </Text>
                            <div className="flex items-center mt-1">
                              {item.confidence && (
                                <Tag color="blue" className="text-xs">
                                  置信度 {(item.confidence * 100).toFixed(0)}%
                                </Tag>
                              )}
                            </div>
                          </div>
                        }
                      />
                    </List.Item>
                  );
                }}
              />
            </div>
          )}

          {/* 空状态 */}
          {recentAnalysis.length === 0 && !historyLoading && (
            <Empty
              image={Empty.PRESENTED_IMAGE_SIMPLE}
              description={
                <div>
                  <Text type="secondary">暂无分析记录</Text>
                  <br />
                  <Text type="secondary" className="text-sm">
                    点击上方按钮开始AI分析
                  </Text>
                </div>
              }
            />
          )}

          {/* AI服务状态 */}
          {healthStatus && (
            <div className="p-3 bg-gray-50 rounded">
              <div className="flex items-center justify-between text-xs">
                <Space>
                  <Badge
                    status={healthStatus.status === 'healthy' ? 'success' : 'error'}
                    text={healthStatus.status === 'healthy' ? 'AI服务正常' : 'AI服务异常'}
                  />
                  <Text type="secondary">
                    模型: {healthStatus.model_name || 'GLM-4.5-Flash'}
                  </Text>
                </Space>
                <Text type="secondary">
                  更新: {formatDateTime(healthStatus.timestamp)}
                </Text>
              </div>
            </div>
          )}
        </div>
      </Card>

      {/* AI分析对话框 */}
      <AIAnalysisDialog
        visible={dialogVisible}
        onClose={() => setDialogVisible(false)}
        defaultSymbol={symbol}
        defaultRole={selectedRole || 'technical_analyst'}
      />
    </>
  );
};

export default AIAnalysisPanel;