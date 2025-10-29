import React, { useState } from 'react';
import {
  Card,
  Typography,
  Tag,
  Rate,
  Button,
  Space,
  Collapse,
  Descriptions,
  Alert,
  Progress,
  Divider,
  List,
  Avatar,
  Tooltip,
  Badge,
  Row,
  Col,
  Statistic
} from 'antd';
import {
  StarOutlined,
  BulbOutlined,
  InfoCircleOutlined,
  ExpandOutlined,
  DownloadOutlined,
  ShareAltOutlined,
  LikeOutlined,
  DislikeOutlined,
  CheckCircleOutlined,
  WarningOutlined,
  RiseOutlined,
  FallOutlined
} from '@ant-design/icons';
import { formatDateTime, formatPercent } from '@/utils/format';

const { Title, Text, Paragraph } = Typography;
const { Panel } = Collapse;

interface AIAnalysisResultProps {
  data: {
    role: string;
    symbol: string;
    question: string;
    answer: string;
    confidence: number;
    reasoning?: string;
    suggestions?: string[];
    metadata?: any;
    created_at?: string;
  };
  compact?: boolean;
  showActions?: boolean;
  onFeedback?: (rating: number, feedback: string) => void;
  onExport?: () => void;
  onShare?: () => void;
}

// 分析师角色配置
const ANALYST_CONFIG = {
  technical_analyst: {
    name: '技术分析师',
    icon: '📈',
    color: '#1890ff',
    avatar: <Avatar style={{ backgroundColor: '#1890ff' }}>📈</Avatar>
  },
  fundamental_analyst: {
    name: '基本面分析师',
    icon: '💼',
    color: '#52c41a',
    avatar: <Avatar style={{ backgroundColor: '#52c41a' }}>💼</Avatar>
  },
  news_analyst: {
    name: '新闻分析师',
    icon: '📰',
    color: '#fa8c16',
    avatar: <Avatar style={{ backgroundColor: '#fa8c16' }}>📰</Avatar>
  },
  risk_analyst: {
    name: '风控分析师',
    icon: '🛡️',
    color: '#f5222d',
    avatar: <Avatar style={{ backgroundColor: '#f5222d' }}>🛡️</Avatar>
  }
};

const AIAnalysisResult: React.FC<AIAnalysisResultProps> = ({
  data,
  compact = false,
  showActions = true,
  onFeedback,
  onExport,
  onShare
}) => {
  const [expanded, setExpanded] = useState(false);
  const [feedbackRating, setFeedbackRating] = useState(0);
  const [showFeedbackForm, setShowFeedbackForm] = useState(false);

  const roleConfig = ANALYST_CONFIG[data.role as keyof typeof ANALYST_CONFIG];

  // 获取置信度颜色
  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return '#52c41a';
    if (confidence >= 0.6) return '#fa8c16';
    return '#f5222d';
  };

  // 获取置信度等级
  const getConfidenceLevel = (confidence: number) => {
    if (confidence >= 0.8) return '高';
    if (confidence >= 0.6) return '中';
    return '低';
  };

  // 处理反馈
  const handleFeedback = (rating: number) => {
    setFeedbackRating(rating);
    if (onFeedback) {
      onFeedback(rating, '');
    }
    setShowFeedbackForm(false);
  };

  // 渲染关键指标
  const renderKeyMetrics = () => {
    const metrics = [];

    // 置信度指标
    metrics.push(
      <Col span={8} key="confidence">
        <Statistic
          title="分析置信度"
          value={data.confidence * 100}
          suffix="%"
          precision={1}
          valueStyle={{ color: getConfidenceColor(data.confidence), fontSize: compact ? '14px' : '16px' }}
          prefix={<StarOutlined />}
        />
      </Col>
    );

    // 如果有元数据，添加其他指标
    if (data.metadata) {
      if (data.metadata.tokens_used) {
        metrics.push(
          <Col span={8} key="tokens">
            <Statistic
              title="使用Token"
              value={data.metadata.tokens_used}
              valueStyle={{ fontSize: compact ? '14px' : '16px' }}
            />
          </Col>
        );
      }

      if (data.metadata.processing_time) {
        metrics.push(
          <Col span={8} key="time">
            <Statistic
              title="处理时间"
              value={data.metadata.processing_time}
              suffix="秒"
              precision={1}
              valueStyle={{ fontSize: compact ? '14px' : '16px' }}
            />
          </Col>
        );
      }
    }

    return metrics.length > 0 ? <Row gutter={16}>{metrics}</Row> : null;
  };

  // 渲染建议列表
  const renderSuggestions = () => {
    if (!data.suggestions || data.suggestions.length === 0) return null;

    return (
      <div className="mt-4">
        <Title level={5} className="flex items-center">
          <BulbOutlined className="mr-2 text-yellow-500" />
          投资建议
        </Title>
        <List
          size="small"
          dataSource={data.suggestions}
          renderItem={(suggestion: string, index: number) => (
            <List.Item>
              <div className="flex items-start space-x-2">
                <Badge count={index + 1} style={{ backgroundColor: roleConfig.color }} />
                <Text className="flex-1">{suggestion}</Text>
              </div>
            </List.Item>
          )}
        />
      </div>
    );
  };

  if (compact) {
    return (
      <Card size="small" className="mb-2">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              {roleConfig.avatar}
              <Text strong>{roleConfig.name}</Text>
              <Tag color={roleConfig.color}>{data.symbol}</Tag>
              <Tag color={getConfidenceColor(data.confidence)}>
                {getConfidenceLevel(data.confidence)}置信度
              </Tag>
            </div>
            <Paragraph ellipsis={{ rows: 2, expandable: true }} className="text-sm">
              {data.answer}
            </Paragraph>
          </div>
          <div className="flex flex-col items-end space-y-2 ml-4">
            <Button
              type="text"
              size="small"
              icon={<ExpandOutlined />}
              onClick={() => setExpanded(!expanded)}
            />
            {showActions && (
              <Space>
                <Button type="text" size="small" icon={<LikeOutlined />} />
                <Button type="text" size="small" icon={<ShareAltOutlined />} />
              </Space>
            )}
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card
      title={
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {roleConfig.avatar}
            <div>
              <Title level={4} className="mb-0">
                {roleConfig.name}分析报告
              </Title>
              <Text type="secondary" className="text-sm">
                股票代码: {data.symbol} | {data.created_at && formatDateTime(data.created_at)}
              </Text>
            </div>
          </div>
          <Space>
            <Tag color={roleConfig.color}>{roleConfig.icon} {roleConfig.name}</Tag>
            <Tag color={getConfidenceColor(data.confidence)}>
              置信度: {getConfidenceLevel(data.confidence)} ({(data.confidence * 100).toFixed(0)}%)
            </Tag>
          </Space>
        </div>
      }
      extra={
        showActions && (
          <Space>
            <Tooltip title="导出报告">
              <Button
                type="text"
                icon={<DownloadOutlined />}
                onClick={onExport}
              />
            </Tooltip>
            <Tooltip title="分享">
              <Button
                type="text"
                icon={<ShareAltOutlined />}
                onClick={onShare}
              />
            </Tooltip>
            <Divider type="vertical" />
            <Space>
              <Tooltip title="有用">
                <Button
                  type={feedbackRating > 3 ? "primary" : "text"}
                  size="small"
                  icon={<LikeOutlined />}
                  onClick={() => handleFeedback(5)}
                />
              </Tooltip>
              <Tooltip title="无用">
                <Button
                  type={feedbackRating > 0 && feedbackRating <= 2 ? "primary" : "text"}
                  size="small"
                  icon={<DislikeOutlined />}
                  onClick={() => handleFeedback(1)}
                />
              </Tooltip>
            </Space>
          </Space>
        )
      }
      className="w-full"
    >
      <div className="space-y-4">
        {/* 关键指标 */}
        {renderKeyMetrics()}

        <Divider />

        {/* 分析问题 */}
        <div>
          <Title level={5} className="text-blue-600">
            <InfoCircleOutlined className="mr-2" />
            分析问题
          </Title>
          <div className="p-3 bg-blue-50 rounded">
            <Text>{data.question}</Text>
          </div>
        </div>

        {/* 分析结果 */}
        <div>
          <Title level={5}>
            <CheckCircleOutlined className="mr-2 text-green-500" />
            分析结论
          </Title>
          <div className="p-4 bg-gray-50 rounded">
            <Paragraph className="mb-0">
              {data.answer}
            </Paragraph>
          </div>
        </div>

        {/* 推理过程 */}
        {data.reasoning && (
          <Collapse ghost>
            <Panel
              header={
                <Title level={5} className="mb-0">
                  <WarningOutlined className="mr-2 text-orange-500" />
                  分析逻辑与推理过程
                </Title>
              }
              key="reasoning"
            >
              <div className="p-4 bg-orange-50 rounded">
                <Paragraph className="mb-0">
                  {data.reasoning}
                </Paragraph>
              </div>
            </Panel>
          </Collapse>
        )}

        {/* 投资建议 */}
        {renderSuggestions()}

        {/* 置信度详情 */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <Title level={5} className="mb-0">分析置信度</Title>
            <Tag color={getConfidenceColor(data.confidence)}>
              {getConfidenceLevel(data.confidence)}
            </Tag>
          </div>
          <Progress
            percent={data.confidence * 100}
            strokeColor={getConfidenceColor(data.confidence)}
            showInfo={false}
          />
          <div className="flex justify-between mt-1">
            <Text type="secondary" className="text-xs">低置信度</Text>
            <Text type="secondary" className="text-xs">高置信度</Text>
          </div>
        </div>

        {/* 元数据信息 */}
        {data.metadata && (
          <Collapse ghost>
            <Panel header="技术信息" key="metadata">
              <Descriptions size="small" column={2}>
                {data.metadata.model_name && (
                  <Descriptions.Item label="使用模型">
                    {data.metadata.model_name}
                  </Descriptions.Item>
                )}
                {data.metadata.tokens_used && (
                  <Descriptions.Item label="Token使用量">
                    {data.metadata.tokens_used}
                  </Descriptions.Item>
                )}
                {data.metadata.processing_time && (
                  <Descriptions.Item label="处理时间">
                    {data.metadata.processing_time.toFixed(2)}秒
                  </Descriptions.Item>
                )}
                <Descriptions.Item label="分析时间">
                  {data.created_at && formatDateTime(data.created_at)}
                </Descriptions.Item>
              </Descriptions>
            </Panel>
          </Collapse>
        )}

        {/* 免责声明 */}
        <Alert
          message="投资风险提示"
          description="本分析报告由AI生成，仅供参考，不构成投资建议。投资有风险，入市需谨慎。请结合自身风险承受能力和投资目标做出决策。"
          type="warning"
          showIcon
          className="mt-4"
        />
      </div>
    </Card>
  );
};

export default AIAnalysisResult;