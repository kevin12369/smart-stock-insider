import React, { useState, useEffect } from 'react';
import {
  Card,
  Typography,
  Tag,
  Button,
  Space,
  Avatar,
  Divider,
  Row,
  Col,
  Statistic,
  Timeline,
  Tooltip,
  Image,
  Skeleton,
  Alert,
  Progress,
  List
} from 'antd';
import {
  ShareAltOutlined,
  HeartOutlined,
  MessageOutlined,
  CalendarOutlined,
  UserOutlined,
  EyeOutlined,
  TrendingUpOutlined,
  TrendingDownOutlined,
  MinusOutlined,
  LinkOutlined,
  ClockCircleOutlined,
  BookmarkOutlined
} from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';

import { api } from '@/services/api';
import { formatDateTime, formatRelativeTime } from '@/utils/format';

const { Title, Text, Paragraph } = Typography;

interface NewsDetail {
  id: number;
  title: string;
  summary: string;
  content: string;
  source: string;
  author?: string;
  publish_time?: string;
  url: string;
  image_url?: string;
  category?: string;
  tags: string[];
  keywords: string[];
  mentioned_stocks: string[];
  relevance_score: number;
  created_at?: string;
  sentiment?: {
    sentiment: string;
    confidence: number;
    score: number;
    keywords: string[];
    aspects: Record<string, string>;
  };
}

const NewsDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [liked, setLiked] = useState(false);
  const [bookmarked, setBookmarked] = useState(false);

  // 获取新闻详情
  const {
    data: newsDetail,
    isLoading,
    error,
    refetch
  } = useQuery({
    queryKey: ['news-detail', id],
    queryFn: async () => {
      if (!id) throw new Error('新闻ID不能为空');
      const response = await api.get(`/api/news/${id}`);
      return response.data;
    },
    enabled: !!id
  });

  // 获取相关新闻
  const { data: relatedNews = [] } = useQuery({
    queryKey: ['related-news', newsDetail?.mentioned_stocks?.[0]],
    queryFn: async () => {
      if (!newsDetail?.mentioned_stocks?.length) return [];
      const stockCode = newsDetail.mentioned_stocks[0];
      const response = await api.get(`/api/news/stock/${stockCode}?days=7&limit=5`);
      return response.data.data || [];
    },
    enabled: !!newsDetail?.mentioned_stocks?.length
  });

  // 处理点赞
  const handleLike = () => {
    setLiked(!liked);
    // 这里可以调用API保存用户偏好
  };

  // 处理收藏
  const handleBookmark = () => {
    setBookmarked(!bookmarked);
    // 这里可以调用API保存用户收藏
  };

  // 处理分享
  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: newsDetail?.title,
        text: newsDetail?.summary,
        url: window.location.href
      });
    } else {
      // 复制链接到剪贴板
      navigator.clipboard.writeText(window.location.href);
    }
  };

  // 渲染情感分析
  const renderSentimentAnalysis = () => {
    if (!newsDetail?.sentiment) return null;

    const { sentiment, confidence, score, keywords, aspects } = newsDetail.sentiment;

    const sentimentConfig = {
      positive: { color: 'green', icon: <TrendingUpOutlined />, text: '利好' },
      negative: { color: 'red', icon: <TrendingDownOutlined />, text: '利空' },
      neutral: { color: 'default', icon: <MinusOutlined />, text: '中性' }
    };

    const config = sentimentConfig[sentiment as keyof typeof sentimentConfig] || sentimentConfig.neutral;

    return (
      <Card title="情感分析" className="mb-4">
        <Row gutter={16}>
          <Col span={8}>
            <Statistic
              title="情感倾向"
              value={config.text}
              prefix={config.icon}
              valueStyle={{ color: config.color }}
            />
          </Col>
          <Col span={8}>
            <Statistic
              title="情感强度"
              value={Math.abs(score) * 100}
              suffix="%"
              precision={1}
              valueStyle={{ color: config.color }}
            />
          </Col>
          <Col span={8}>
            <Statistic
              title="置信度"
              value={confidence * 100}
              suffix="%"
              precision={1}
            />
          </Col>
        </Row>

        {/* 情感关键词 */}
        {keywords && keywords.length > 0 && (
          <div className="mt-4">
            <Text strong>情感关键词：</Text>
            <div className="flex flex-wrap gap-2 mt-2">
              {keywords.map((keyword, index) => (
                <Tag key={index} color={config.color}>
                  {keyword}
                </Tag>
              ))}
            </div>
          </div>
        )}

        {/* 方面情感分析 */}
        {aspects && Object.keys(aspects).length > 0 && (
          <div className="mt-4">
            <Text strong>方面情感：</Text>
            <div className="mt-2">
              {Object.entries(aspects).map(([aspect, sentiment]) => (
                <div key={aspect} className="flex items-center justify-between py-1">
                  <Text>{aspect}:</Text>
                  <Tag color={sentiment === 'positive' ? 'green' : sentiment === 'negative' ? 'red' : 'default'}>
                    {sentiment === 'positive' ? '积极' : sentiment === 'negative' ? '消极' : '中性'}
                  </Tag>
                </div>
              ))}
            </div>
          </div>
        )}
      </Card>
    );
  };

  // 渲染相关信息
  const renderRelatedInfo = () => {
    return (
      <Card title="相关信息" className="mb-4">
        <Row gutter={16}>
          <Col span={12}>
            <Statistic
              title="新闻来源"
              value={newsDetail?.source}
              prefix={<MessageOutlined />}
            />
          </Col>
          <Col span={12}>
            <Statistic
              title="相关度评分"
              value={newsDetail?.relevance_score * 100 || 0}
              suffix="%"
              precision={1}
              prefix={<TrendingUpOutlined />}
            />
          </Col>
        </Row>

        {newsDetail?.publish_time && (
          <Row gutter={16} className="mt-4">
            <Col span={12}>
              <Statistic
                title="发布时间"
                value={formatRelativeTime(newsDetail.publish_time)}
                prefix={<ClockCircleOutlined />}
              />
            </Col>
            <Col span={12}>
              <Statistic
                title="分类"
                value={newsDetail?.category || '未分类'}
                prefix={<BookmarkOutlined />}
              />
            </Col>
          </Row>
        )}
      </Card>
    );
  };

  // 渲染相关股票
  const renderRelatedStocks = () => {
    if (!newsDetail?.mentioned_stocks?.length) return null;

    return (
      <Card title="相关股票" className="mb-4">
        <div className="flex flex-wrap gap-2">
          {newsDetail.mentioned_stocks.map((stock, index) => (
            <Tag key={index} color="orange" className="text-base">
              {stock}
            </Tag>
          ))}
        </div>
      </Card>
    );
  };

  // 渲染相关新闻
  const renderRelatedNews = () => {
    if (!relatedNews.length) return null;

    return (
      <Card title="相关新闻" className="mb-4">
        <List
          dataSource={relatedNews}
          renderItem={(item: any) => (
            <List.Item
              className="cursor-pointer hover:bg-gray-50"
              onClick={() => navigate(`/news/${item.id}`)}
            >
              <List.Item.Meta
                title={
                  <div className="flex items-center justify-between">
                    <Text className="line-clamp-1">{item.title}</Text>
                    <Text type="secondary" className="text-xs">
                      {formatRelativeTime(item.publish_time)}
                    </Text>
                  </div>
                }
                description={
                  <Text className="text-sm text-gray-600 line-clamp-2">
                    {item.summary}
                  </Text>
                }
              />
            </List.Item>
          )}
        />
      </Card>
    );
  };

  if (isLoading) {
    return (
      <div className="p-6">
        <Skeleton active paragraph={{ rows: 10 }} />
      </div>
    );
  }

  if (error || !newsDetail) {
    return (
      <div className="p-6">
        <Alert
          message="加载失败"
          description="新闻详情加载失败，请重试或检查新闻ID是否正确"
          type="error"
          showIcon
          action={
            <Button size="small" onClick={() => refetch()}>
              重试
            </Button>
          }
        />
      </div>
    );
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* 面包屑导航 */}
      <div className="mb-6">
        <Button type="text" onClick={() => navigate('/news')}>
          ← 返回新闻列表
        </Button>
      </div>

      {/* 主要内容区域 */}
      <Row gutter={[24, 16]}>
        <Col xs={24} lg={16}>
          {/* 新闻标题和基本信息 */}
          <Card className="mb-4">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <Title level={2} className="mb-2">
                  {newsDetail.title}
                </Title>
                <div className="flex items-center space-x-4 text-sm text-gray-600">
                  <span className="flex items-center">
                    <MessageOutlined className="mr-1" />
                    {newsDetail.source}
                  </span>
                  {newsDetail.author && (
                    <span className="flex items-center">
                      <UserOutlined className="mr-1" />
                      {newsDetail.author}
                    </span>
                  )}
                  {newsDetail.publish_time && (
                    <span className="flex items-center">
                      <CalendarOutlined className="mr-1" />
                      {formatDateTime(newsDetail.publish_time)}
                    </span>
                  )}
                </div>
              </div>
              <Space>
                <Tooltip title="分享">
                  <Button
                    type="text"
                    icon={<ShareAltOutlined />}
                    onClick={handleShare}
                  />
                </Tooltip>
                <Tooltip title={liked ? "取消点赞" : "点赞"}>
                  <Button
                    type="text"
                    icon={<HeartOutlined />}
                    className={liked ? 'text-red-500' : ''}
                    onClick={handleLike}
                  />
                </Tooltip>
                <Tooltip title={bookmarked ? "取消收藏" : "收藏"}>
                  <Button
                    type="text"
                    icon={<BookmarkOutlined />}
                    className={bookmarked ? 'text-blue-500' : ''}
                    onClick={handleBookmark}
                  />
                </Tooltip>
                <Button
                  type="text"
                  icon={<LinkOutlined />}
                  onClick={() => window.open(newsDetail.url, '_blank')}
                >
                  原文链接
                </Button>
              </Space>
            </div>

            {/* 分类和标签 */}
            <div className="flex items-center space-x-2 mb-4">
              {newsDetail.category && (
                <Tag color="blue">{newsDetail.category}</Tag>
              )}
              {newsDetail.tags?.map((tag, index) => (
                <Tag key={index}>{tag}</Tag>
              ))}
            </div>

            {/* 新闻图片 */}
            {newsDetail.image_url && (
              <div className="mb-4">
                <Image
                  src={newsDetail.image_url}
                  alt={newsDetail.title}
                  style={{ width: '100%', maxHeight: 400, objectFit: 'cover' }}
                  fallback="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
                />
              </div>
            )}

            {/* 新闻摘要 */}
            {newsDetail.summary && (
              <Alert
                message="新闻摘要"
                description={newsDetail.summary}
                type="info"
                showIcon
                className="mb-4"
              />
            )}

            {/* 新闻正文 */}
            <div className="prose max-w-none">
              <Paragraph className="text-lg leading-relaxed">
                {newsDetail.content.split('\n').map((paragraph, index) => (
                  <p key={index} className="mb-4">
                    {paragraph}
                  </p>
                ))}
              </Paragraph>
            </div>
          </Card>

          {/* 关键词 */}
          {newsDetail.keywords && newsDetail.keywords.length > 0 && (
            <Card title="关键词" className="mb-4">
              <div className="flex flex-wrap gap-2">
                {newsDetail.keywords.map((keyword, index) => (
                  <Tag key={index} color="blue">
                    {keyword}
                  </Tag>
                ))}
              </div>
            </Card>
          )}
        </Col>

        <Col xs={24} lg={8}>
          {/* 侧边栏信息 */}
          {renderSentimentAnalysis()}
          {renderRelatedInfo()}
          {renderRelatedStocks()}
          {renderRelatedNews()}

          {/* 免责声明 */}
          <Card title="温馨提示" className="mb-4">
            <Alert
              message="投资风险提示"
              description="本新闻信息仅供参考，不构成投资建议。投资有风险，入市需谨慎。请结合自身情况做出投资决策。"
              type="warning"
              showIcon
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default NewsDetail;