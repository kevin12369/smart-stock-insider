import React, { useState } from 'react';
import {
  Card,
  Typography,
  Tag,
  Button,
  Space,
  List,
  Avatar,
  Tooltip,
  Statistic,
  Row,
  Col,
  Badge,
  Progress,
  Empty,
  Divider
} from 'antd';
import {
  MessageOutlined,
  ReloadOutlined,
  EyeOutlined,
  TrendingUpOutlined,
  TrendingDownOutlined,
  MinusOutlined,
  MoreOutlined,
  SearchOutlined
} from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';

import NewsList from './NewsList';
import { api } from '@/services/api';
import { formatRelativeTime } from '@/utils/format';

// 获取当前用户ID（暂时使用模拟数据）
const getCurrentUserId = () => {
  return 'user_001'; // 从用户服务获取实际用户ID
};

const { Title, Text, Paragraph } = Typography;

interface NewsPanelProps {
  stockCode?: string;
  height?: string | number;
  showHeader?: boolean;
  limit?: number;
}

interface NewsItem {
  id: number;
  title: string;
  summary: string;
  source: string;
  publish_time: string;
  category?: string;
  mentioned_stocks: string[];
  relevance_score: number;
}

const NewsPanel: React.FC<NewsPanelProps> = ({
  stockCode,
  height = 400,
  showHeader = true,
  limit = 8
}) => {
  const navigate = useNavigate();
  const [showFullList, setShowFullList] = useState(false);
  const [showRecommendations, setShowRecommendations] = useState(false);

  // 获取股票相关新闻
  const {
    data: stockNews = [],
    isLoading: newsLoading,
    refetch: refetchNews
  } = useQuery({
    queryKey: ['stock-news', stockCode, limit],
    queryFn: async () => {
      if (!stockCode) return [];
      const response = await api.get(`/api/news/stock/${stockCode}?days=7&limit=${limit}`);
      return response.data.data || [];
    },
    enabled: !!stockCode,
    refetchInterval: 300000 // 5分钟刷新
  });

  // 获取最新新闻统计
  const { data: newsStats } = useQuery({
    queryKey: ['news-statistics'],
    queryFn: async () => {
      const response = await api.get('/api/news/statistics');
      return response.data;
    },
    refetchInterval: 600000 // 10分钟刷新
  });

  // 获取情感分析摘要
  const { data: sentimentSummary } = useQuery({
    queryKey: ['sentiment-summary', stockCode],
    queryFn: async () => {
      if (!stockCode) return null;
      const response = await api.get('/api/news/sentiment/summary', {
        params: { stock_code: stockCode, days: 7 }
      });
      return response.data;
    },
    enabled: !!stockCode,
    refetchInterval: 300000 // 5分钟刷新
  });

  // 获取个性化推荐
  const {
    data: recommendations = [],
    isLoading: recommendationsLoading,
    refetch: refetchRecommendations
  } = useQuery({
    queryKey: ['personalized-recommendations', getCurrentUserId()],
    queryFn: async () => {
      const response = await api.post('/api/news/recommendations', {
        user_id: getCurrentUserId(),
        limit: limit
      });
      return response.data;
    },
    enabled: !stockCode && showRecommendations,
    refetchInterval: 600000 // 10分钟刷新
  });

  // 处理新闻点击
  const handleNewsClick = (news: NewsItem) => {
    navigate(`/news/${news.id}`);
  };

  // 处理查看全部
  const handleViewAll = () => {
    navigate('/news');
  };

  // 处理用户反馈
  const handleUserFeedback = async (newsId: number, feedbackType: string) => {
    try {
      await api.post('/api/news/feedback', {
        user_id: getCurrentUserId(),
        news_id: newsId,
        feedback_type: feedbackType
      });
      // 刷新推荐
      refetchRecommendations();
    } catch (error) {
      console.error('更新用户反馈失败:', error);
    }
  };

  // 渲染新闻条目（简化版）
  const renderNewsItem = (item: NewsItem | any) => {
    // 简单的情感判断（基于关键词）
    const getSentiment = () => {
      const positiveWords = ['上涨', '利好', '增长', '突破', '看好'];
      const negativeWords = ['下跌', '利空', '下滑', '跌破', '看空'];

      const title = item.title.toLowerCase();
      if (positiveWords.some(word => title.includes(word))) {
        return { color: 'green', icon: <TrendingUpOutlined />, text: '利好' };
      }
      if (negativeWords.some(word => title.includes(word))) {
        return { color: 'red', icon: <TrendingDownOutlined />, text: '利空' };
      }
      return { color: 'default', icon: <MinusOutlined />, text: '中性' };
    };

    const sentiment = getSentiment();
    const isRecommendation = item.recommendation_score !== undefined;

    return (
      <List.Item
        key={item.id}
        className="cursor-pointer hover:bg-gray-50 transition-colors py-2"
        onClick={() => handleNewsClick(item)}
        actions={[
          <Tooltip title="查看详情">
            <Button type="text" size="small" icon={<EyeOutlined />} />
          </Tooltip>,
          ...(isRecommendation ? [
            <Tooltip title="点赞">
              <Button
                type="text"
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  handleUserFeedback(item.id, 'like');
                }}
              >
                👍
              </Button>
            </Tooltip>,
            <Tooltip title="不感兴趣">
              <Button
                type="text"
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  handleUserFeedback(item.id, 'dislike');
                }}
              >
                👎
              </Button>
            </Tooltip>
          ] : [])
        ]}
      >
        <List.Item.Meta
          avatar={
            <Avatar
              style={{ backgroundColor: isRecommendation ? '#52c41a' : '#1890ff' }}
              icon={isRecommendation ? '🎯' : <MessageOutlined />}
              size="small"
            />
          }
          title={
            <div className="space-y-1">
              <Title level={5} className="mb-0 !text-sm line-clamp-1">
                {item.title}
                {isRecommendation && (
                  <Tag color="gold" size="small" className="ml-2">
                    推荐 {Math.round(item.recommendation_score * 100)}%
                  </Tag>
                )}
              </Title>
              <div className="flex items-center space-x-2 text-xs text-gray-500">
                <span>{item.source}</span>
                <span>•</span>
                <span>{formatRelativeTime(item.publish_time)}</span>
                {item.category && (
                  <>
                    <span>•</span>
                    <Tag color="blue" size="small">{item.category}</Tag>
                  </>
                )}
                <span>•</span>
                <Tag color={sentiment.color} size="small" icon={sentiment.icon}>
                  {sentiment.text}
                </Tag>
                {item.mentioned_stocks?.length > 0 && (
                  <Badge count={item.mentioned_stocks.length} color="orange">
                    <Tag color="orange" size="small">相关</Tag>
                  </Badge>
                )}
              </div>
              {isRecommendation && item.recommendation_reasons?.length > 0 && (
                <div className="flex items-center space-x-1 text-xs text-blue-600">
                  <span>推荐理由:</span>
                  {item.recommendation_reasons.slice(0, 2).map((reason: string, index: number) => (
                    <Tag key={index} color="blue" size="small">{reason}</Tag>
                  ))}
                </div>
              )}
            </div>
          }
          description={
            <Text className="text-xs text-gray-600 line-clamp-2">
              {item.summary}
            </Text>
          }
        />
      </List.Item>
    );
  };

  if (showHeader && !stockCode) {
    // 通用新闻面板（无股票代码）
    return (
      <Card
        title={
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <MessageOutlined className="text-blue-500" />
              <span>{showRecommendations ? '个性化推荐' : '市场资讯'}</span>
            </div>
            <Space>
              {!showRecommendations && (
                <Button
                  type="text"
                  size="small"
                  icon={<ReloadOutlined />}
                  onClick={() => refetchNews()}
                  loading={newsLoading}
                />
              )}
              <Button
                type="text"
                size="small"
                icon={<SearchOutlined />}
                onClick={() => navigate('/news')}
              >
                搜索
              </Button>
              <Button
                type="text"
                size="small"
                onClick={() => setShowRecommendations(!showRecommendations)}
              >
                {showRecommendations ? '最新资讯' : '推荐'}
              </Button>
            </Space>
          </div>
        }
        className="h-full"
        bodyStyle={{ padding: 0, height: 'calc(100% - 60px)', overflow: 'hidden' }}
      >
        <div className="h-full overflow-y-auto">
          {recommendationsLoading ? (
            <div className="flex items-center justify-center h-32">
              <span>加载推荐中...</span>
            </div>
          ) : showRecommendations && recommendations.length > 0 ? (
            <List
              dataSource={recommendations}
              renderItem={renderNewsItem}
              split={false}
              size="small"
            />
          ) : !showRecommendations ? (
            <div className="p-4">
              <Empty
                description="请选择股票查看相关新闻或开启个性化推荐"
                className="h-full flex items-center justify-center"
                image={Empty.PRESENTED_IMAGE_SIMPLE}
              >
                <Button type="primary" onClick={() => navigate('/news')}>
                  浏览所有新闻
                </Button>
              </Empty>
            </div>
          ) : (
            <div className="p-4">
              <Empty
                description="暂无推荐内容"
                image={Empty.PRESENTED_IMAGE_SIMPLE}
              >
                <Button type="primary" onClick={() => setShowRecommendations(false)}>
                  查看最新资讯
                </Button>
              </Empty>
            </div>
          )}
        </div>
      </Card>
    );
  }

  return (
    <Card
      title={
        showHeader ? (
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <MessageOutlined className="text-blue-500" />
              <span>
                {stockCode ? `${stockCode} 相关新闻` : '最新资讯'}
              </span>
              {stockNews.length > 0 && (
                <Badge count={stockNews.length} color="blue" />
              )}
            </div>
            <Space>
              {stockCode && (
                <Button
                  type="text"
                  size="small"
                  icon={<ReloadOutlined />}
                  onClick={() => refetchNews()}
                  loading={newsLoading}
                />
              )}
              <Button
                type="text"
                size="small"
                icon={<MoreOutlined />}
                onClick={() => setShowFullList(!showFullList)}
              >
                {showFullList ? '收起' : '展开'}
              </Button>
            </Space>
          </div>
        ) : null
      }
      className="h-full"
      bodyStyle={{ padding: 0, height: showHeader ? 'calc(100% - 60px)' : '100%', overflow: 'hidden' }}
    >
      <div className="h-full overflow-y-auto">
        {/* 统计信息 */}
        {stockCode && newsStats && (
          <div className="p-4 border-b">
            <Row gutter={16}>
              <Col span={12}>
                <Statistic
                  title="7日新闻"
                  value={stockNews.length}
                  prefix={<MessageOutlined />}
                  valueStyle={{ fontSize: '14px' }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="今日更新"
                  value={newsStats?.today_news || 0}
                  prefix={<TrendingUpOutlined />}
                  valueStyle={{ fontSize: '14px' }}
                />
              </Col>
            </Row>

            {/* 情感分析摘要 */}
            {sentimentSummary && (
              <div className="mt-3">
                <div className="flex items-center justify-between text-xs text-gray-600 mb-2">
                  <span>情感分布</span>
                  <span>总计: {sentimentSummary.total_news}条</span>
                </div>
                <div className="flex space-x-2">
                  <Progress
                    percent={sentimentSummary.sentiment_percentages.positive}
                    strokeColor="#52c41a"
                    showInfo={false}
                    size="small"
                    className="flex-1"
                  />
                  <Progress
                    percent={sentimentSummary.sentiment_percentages.negative}
                    strokeColor="#ff4d4f"
                    showInfo={false}
                    size="small"
                    className="flex-1"
                  />
                  <Progress
                    percent={sentimentSummary.sentiment_percentages.neutral}
                    strokeColor="#d9d9d9"
                    showInfo={false}
                    size="small"
                    className="flex-1"
                  />
                </div>
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span className="text-green-500">
                    利好 {sentimentSummary.sentiment_percentages.positive.toFixed(1)}%
                  </span>
                  <span className="text-red-500">
                    利空 {sentimentSummary.sentiment_percentages.negative.toFixed(1)}%
                  </span>
                  <span>
                    中性 {sentimentSummary.sentiment_percentages.neutral.toFixed(1)}%
                  </span>
                </div>
              </div>
            )}
          </div>
        )}

        {/* 新闻列表 */}
        <div className="p-4">
          {newsLoading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="p-3 border rounded animate-pulse">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-full"></div>
                </div>
              ))}
            </div>
          ) : stockNews.length > 0 ? (
            <List
              dataSource={stockNews}
              renderItem={renderNewsItem}
              split={false}
              size="small"
            />
          ) : (
            <Empty
              description="暂无相关新闻"
              image={Empty.PRESENTED_IMAGE_SIMPLE}
              className="py-8"
            >
              <Button type="primary" onClick={() => navigate('/news')}>
                浏览所有新闻
              </Button>
            </Empty>
          )}

          {/* 查看更多按钮 */}
          {stockNews.length > 0 && !showFullList && (
            <div className="text-center mt-4">
              <Button type="text" onClick={handleViewAll}>
                查看更多新闻
              </Button>
            </div>
          )}
        </div>
      </div>
    </Card>
  );
};

export default NewsPanel;