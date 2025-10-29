import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Button,
  Spin,
  Timeline,
  Tag,
  Progress,
  Space,
  Alert,
  Divider,
  Typography,
  Avatar,
  Badge,
  Tooltip,
  message
} from 'antd';
import {
  RobotOutlined,
  BulbOutlined,
  FireOutlined,
  SafetyCertificateOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  InfoCircleOutlined,
  TrophyOutlined,
  ThunderboltOutlined,
  TeamOutlined
} from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

const { Title, Text, Paragraph } = Typography;

interface Expert {
  id: string;
  name: string;
  description: string;
  specialties: string[];
  confidence: number;
  available: boolean;
}

interface ExpertOpinion {
  expert_type: string;
  score: number;
  signal: string;
  analysis: any;
  confidence: number;
  timestamp: string;
  key_insights: string[];
}

interface MeetingResult {
  symbol: string;
  meeting_timestamp: string;
  expert_opinions: ExpertOpinion[];
  consolidated_analysis: any;
  final_recommendation: any;
  meeting_status: string;
}

const ExpertAvatar = ({ expertType }: { expertType: string }) => {
  const icons = {
    technical: <BulbOutlined style={{ color: '#1890ff' }} />,
    fundamental: <TrophyOutlined style={{ color: '#52c41a' }} />,
    news: <FireOutlined style={{ color: '#fa8c16' }} />,
    risk: <SafetyCertificateOutlined style={{ color: '#f5222d' }} />
  };

  return icons[expertType as keyof typeof icons] || <RobotOutlined />;
};

const ExpertCard = ({
  expert,
  opinion,
  isAnalyzing,
  onDetailsClick
}: {
  expert: Expert;
  opinion?: ExpertOpinion;
  isAnalyzing: boolean;
  onDetailsClick: () => void;
}) => {
  const getSignalColor = (signal: string) => {
    const colors: Record<string, string> = {
      '买入': '#f5222d',
      '强烈买入': '#cf1322',
      '持有': '#52c41a',
      '卖出': '#1890ff',
      '强烈卖出': '#2f54eb'
    };
    return colors[signal] || '#8c8c8c';
  };

  const getScoreColor = (score: number) => {
    if (score >= 8) return '#52c41a';
    if (score >= 6) return '#faad14';
    if (score >= 4) return '#fa8c16';
    return '#f5222d';
  };

  return (
    <Card
      hoverable
      className="h-full"
      extra={
        <Button type="text" size="small" onClick={onDetailsClick}>
          查看详情
        </Button>
      }
    >
      <div className="flex items-center mb-4">
        <Avatar icon={<ExpertAvatar expertType={expert.id} />} className="mr-3" />
        <div className="flex-1">
          <Title level={5} className="mb-1">{expert.name}</Title>
          <Text type="secondary" className="text-xs">
            置信度: {expert.confidence * 100}%
          </Text>
        </div>
        {expert.available && (
          <Badge status="success" text="可用" />
        )}
      </div>

      {isAnalyzing ? (
        <div className="text-center py-8">
          <Spin size="large" />
          <div className="mt-4">
            <Text type="secondary">分析中...</Text>
          </div>
        </div>
      ) : opinion ? (
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <Text strong>综合评分</Text>
            <Tag color={getScoreColor(opinion.score)}>
              {opinion.score}/10
            </Tag>
          </div>

          <div className="flex justify-between items-center">
            <Text strong>投资信号</Text>
            <Tag color={getSignalColor(opinion.signal)}>
              {opinion.signal}
            </Tag>
          </div>

          <div className="flex justify-between items-center">
            <Text strong>分析置信度</Text>
            <Progress
              percent={opinion.confidence * 100}
              size="small"
              strokeColor={{
                '0%': '#8c8c8c',
                '100%': '#1890ff',
              }}
            />
          </div>

          <div className="mt-3">
            <Text type="secondary" className="text-xs">关键洞察:</Text>
            <ul className="mt-1 space-y-1">
              {opinion.key_insights?.slice(0, 2).map((insight, index) => (
                <li key={index} className="text-xs text-gray-600">
                  • {insight}
                </li>
              ))}
            </ul>
          </div>
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          <ExclamationCircleOutlined className="text-2xl mb-2" />
          <Text type="secondary">等待分析</Text>
        </div>
      )}
    </Card>
  );
};

const MeetingTimeline = ({ opinions }: { opinions: ExpertOpinion[] }) => {
  return (
    <Timeline className="mt-6">
      {opinions.map((opinion, index) => (
        <Timeline.Item
          key={opinion.expert_type}
          dot={<Avatar size="small" icon={<ExpertAvatar expertType={opinion.expert_type} />} />}
        >
          <div>
            <Text strong>
              {opinion.expert_type === 'technical' && '技术面分析师'}
              {opinion.expert_type === 'fundamental' && '基本面分析师'}
              {opinion.expert_type === 'news' && '新闻分析师'}
              {opinion.expert_type === 'risk' && '风控分析师'}
            </Text>
            <div className="mt-1">
              <Text>评分: {opinion.score}/10 | 信号: {opinion.signal}</Text>
            </div>
          </div>
        </Timeline.Item>
      ))}
    </Timeline>
  );
};

const FinalRecommendation = ({ recommendation }: { recommendation: any }) => {
  if (!recommendation) return null;

  const getRecommendationColor = (rec: string) => {
    const colors: Record<string, string> = {
      '强烈买入': '#cf1322',
      '买入': '#f5222d',
      '持有': '#52c41a',
      '卖出': '#1890ff',
      '强烈卖出': '#2f54eb'
    };
    return colors[rec] || '#8c8c8c';
  };

  return (
    <Card title="最终投资建议" className="mt-6">
      <Row gutter={16}>
        <Col span={8}>
          <div className="text-center">
            <Title level={2} style={{ color: getRecommendationColor(recommendation.recommendation) }}>
              {recommendation.recommendation}
            </Title>
            <div className="mt-2">
              <Text type="secondary">置信度: {(recommendation.confidence * 100).toFixed(0)}%</Text>
            </div>
          </div>
        </Col>
        <Col span={16}>
          <div className="space-y-2">
            <div>
              <Text strong>目标价格: </Text>
              <Text code>¥{recommendation.target_price?.toFixed(2) || 'N/A'}</Text>
            </div>
            <div>
              <Text strong>建议仓位: </Text>
              <Text code>{recommendation.position_size || 'N/A'}</Text>
            </div>
            <div>
              <Text strong>止损价格: </Text>
              <Text code>¥{recommendation.stop_loss?.toFixed(2) || 'N/A'}</Text>
            </div>
          </div>
        </Col>
      </Row>

      <Divider />

      <div>
        <Title level={5}>投资理由</Title>
        <ul className="mt-2 space-y-1">
          {recommendation.key_reasons?.map((reason: string, index: number) => (
            <li key={index} className="text-sm">
              {reason}
            </li>
          ))}
        </ul>
      </div>

      {recommendation.risk_factors && recommendation.risk_factors.length > 0 && (
        <div className="mt-4">
          <Title level={5}>风险因素</Title>
          <ul className="mt-2 space-y-1">
            {recommendation.risk_factors.map((risk: string, index: number) => (
              <li key={index} className="text-sm text-orange-600">
                ⚠️ {risk}
              </li>
            ))}
          </ul>
        </div>
      )}

      <Alert
        message={recommendation.disclaimer}
        type="info"
        showIcon
        className="mt-4"
      />
    </Card>
  );
};

export const ExpertRoundTable: React.FC<{ symbol: string }> = ({ symbol }) => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [selectedExpert, setSelectedExpert] = useState<string | null>(null);
  const [meetingResult, setMeetingResult] = useState<MeetingResult | null>(null);

  // 获取专家列表
  const {
    data: experts,
    isLoading: expertsLoading
  } = useQuery<Expert[]>({
    queryKey: ['experts'],
    queryFn: async () => {
      const response = await axios.get('/api/expert-roundtable/experts');
      return response.data.experts;
    }
  });

  // 启动专家圆桌会议
  const startRoundTable = async () => {
    setIsAnalyzing(true);
    setMeetingResult(null);

    try {
      message.loading('专家圆桌会议开始，请稍候...');

      const response = await axios.post('/api/expert-roundtable/full-analysis', {
        symbol: symbol
      });

      if (response.data.success) {
        setMeetingResult(response.data.data);
        message.success('专家圆桌会议分析完成！');
      } else {
        message.error('分析失败，请重试');
      }
    } catch (error) {
      console.error('专家圆桌会议失败:', error);
      message.error('专家圆桌会议失败，请检查网络连接');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // 快速分析
  const quickAnalysis = async (expertType: string) => {
    try {
      message.loading(`${expertType}分析中...`);

      const response = await axios.post(
        `/api/expert-roundtable/quick-analysis?symbol=${symbol}`
      );

      if (response.data.success) {
        message.success(`${expertType}分析完成`);
        setSelectedExpert(expertType);
      }
    } catch (error) {
      console.error('快速分析失败:', error);
      message.error('分析失败，请重试');
    }
  };

  return (
    <div className="expert-round-table">
      {/* 头部控制区 */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <Title level={3}>专家圆桌会议</Title>
          <Text type="secondary">
            股票代码: {symbol}
          </Text>
        </div>
        <Space>
          <Button
            type="primary"
            icon={<PlayCircleOutlined />}
            onClick={startRoundTable}
            loading={isAnalyzing}
            disabled={!experts || experts.length === 0}
          >
            {isAnalyzing ? '分析中...' : '启动圆桌会议'}
          </Button>
        </Space>
      </div>

      {/* 专家团队介绍 */}
      <Card title="专家团队" className="mb-6">
        <Row gutter={16}>
          {experts?.map((expert) => (
            <Col span={6} key={expert.id} className="mb-4">
              <div className="text-center">
                <Avatar
                  icon={<ExpertAvatar expertType={expert.id} />}
                  size={64}
                  className="mb-2"
                />
                <Title level={5}>{expert.name}</Title>
                <Text type="secondary" className="text-sm mb-2">
                  {expert.description}
                </Text>
                <div className="flex flex-wrap gap-1 justify-center mb-2">
                  {expert.specialties.slice(0, 3).map((specialty) => (
                    <Tag key={specialty} size="small">
                      {specialty}
                    </Tag>
                  ))}
                </div>
                <Button
                  size="small"
                  onClick={() => quickAnalysis(expert.id)}
                  loading={isAnalyzing && selectedExpert === expert.id}
                >
                  快速分析
                </Button>
              </div>
            </Col>
          ))}
        </Row>
      </Card>

      {/* 分析状态展示 */}
      {isAnalyzing && (
        <Card className="mb-6">
          <div className="text-center py-8">
            <Spin size="large" />
            <div className="mt-4">
              <Title level={4}>专家圆桌会议进行中...</Title>
              <Text type="secondary">
                四位专家正在从不同角度分析股票 {symbol}
              </Text>
            </div>
            <Progress
              percent={66}
              status="active"
              strokeColor={{
                '0%': '#108ee9',
                '100%': '#87d068',
              }}
              className="mt-4"
            />
          </div>
        </Card>
      )}

      {/* 分析结果展示 */}
      {meetingResult && !isAnalyzing && (
        <div className="space-y-6">
          {/* 专家观点卡片 */}
          <Row gutter={16}>
            {meetingResult.expert_opinions?.map((opinion) => {
              const expert = experts?.find(e => e.id === opinion.expert_type);
              return (
                <Col span={6} key={opinion.expert_type}>
                  <ExpertCard
                    expert={expert!}
                    opinion={opinion}
                    isAnalyzing={false}
                    onDetailsClick={() => {
                      message.info(`${expert?.name}的详细分析`);
                    }}
                  />
                </Col>
              );
            })}
          </Row>

          {/* 会议时间线 */}
          <Card title="专家观点交锋" className="mb-6">
            <MeetingTimeline opinions={meetingResult.expert_opinions} />
          </Card>

          {/* 最终建议 */}
          <FinalRecommendation recommendation={meetingResult.final_recommendation} />

          {/* 分析信息 */}
          <Card title="会议信息" className="text-xs">
            <p>
              <strong>股票代码:</strong> {meetingResult.symbol}<br/>
              <strong>会议时间:</strong> {meetingResult.meeting_timestamp}<br/>
              <strong>分析状态:</strong> {meetingResult.meeting_status}
            </p>
          </Card>
        </div>
      )}

      {/* 空状态 */}
      {!isAnalyzing && !meetingResult && (
        <Card className="text-center py-16">
          <TeamOutlined className="text-6xl mb-4 text-gray-400" />
          <Title level={4} type="secondary">准备开始专家圆桌会议</Title>
          <Paragraph type="secondary">
            四位专业分析师将从技术面、基本面、新闻面和风控角度
            为您提供全方位的投资分析建议
          </Paragraph>
          <Space className="mt-6">
            <Button
              type="primary"
              size="large"
              icon={<PlayCircleOutlined />}
              onClick={startRoundTable}
            >
              开始专家圆桌会议
            </Button>
          </Space>
        </Card>
      )}
    </div>
  );
};