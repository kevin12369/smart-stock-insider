import React, { useState, useEffect } from 'react';
import {
  Card,
  List,
  Typography,
  Tag,
  Space,
  Button,
  Input,
  Select,
  DatePicker,
  Row,
  Col,
  Pagination,
  Spin,
  Empty,
  Tooltip,
  Avatar,
  Badge,
  Dropdown,
  MenuProps,
  Divider,
  Statistic
} from 'antd';
import {
  SearchOutlined,
  FilterOutlined,
  ReloadOutlined,
  EyeOutlined,
  ShareAltOutlined,
  CalendarOutlined,
  HeartOutlined,
  MessageOutlined,
  TrendingUpOutlined,
  TrendingDownOutlined,
  MinusOutlined,
  MoreOutlined
} from '@ant-design/icons';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import dayjs from 'dayjs';

import { api } from '@/services/api';
import { formatDateTime, formatRelativeTime } from '@/utils/format';

const { Title, Text, Paragraph } = Typography;
const { Search } = Input;
const { Option } = Select;
const { RangePicker } = DatePicker;

interface NewsItem {
  id: number;
  title: string;
  summary: string;
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
}

interface NewsListProps {
  stockCode?: string;
  limit?: number;
  showFilters?: boolean;
  showHeader?: boolean;
  height?: string | number;
  onNewsClick?: (news: NewsItem) => void;
}

const NewsList: React.FC<NewsListProps> = ({
  stockCode,
  limit = 20,
  showFilters = true,
  showHeader = true,
  height = '600px',
  onNewsClick
}) => {
  const [searchKeyword, setSearchKeyword] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedSource, setSelectedSource] = useState('');
  const [selectedSentiment, setSelectedSentiment] = useState('');
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs] | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [sortBy, setSortBy] = useState('publish_time');
  const [sortOrder, setSortOrder] = useState('desc');

  const queryClient = useQueryClient();

  // 获取新闻列表
  const {
    data: newsData,
    isLoading,
    error,
    refetch
  } = useQuery({
    queryKey: [
      'news-list',
      {
        keyword: searchKeyword,
        category: selectedCategory,
        source: selectedSource,
        sentiment: selectedSentiment,
        dateRange: dateRange?.map(d => d.toISOString()),
        stockCode,
        page: currentPage,
        limit,
        sortBy,
        sortOrder
      }
    ],
    queryFn: async () => {
      const params = new URLSearchParams({
        limit: limit.toString(),
        offset: ((currentPage - 1) * limit).toString(),
        sort_by: sortBy,
        sort_order: sortOrder
      });

      if (searchKeyword) params.append('keyword', searchKeyword);
      if (selectedCategory) params.append('category', selectedCategory);
      if (selectedSource) params.append('source', selectedSource);
      if (selectedSentiment) params.append('sentiment', selectedSentiment);
      if (stockCode) params.append('stock_code', stockCode);
      if (dateRange) {
        params.append('start_date', dateRange[0].toISOString());
        params.append('end_date', dateRange[1].toISOString());
      }

      const response = await api.get(`/api/news/list?${params}`);
      return response.data;
    },
    refetchInterval: 300000, // 5分钟刷新
  });

  // 获取新闻分类
  const { data: categories = [] } = useQuery({
    queryKey: ['news-categories'],
    queryFn: async () => {
      const response = await api.get('/api/news/categories');
      return response.data.categories;
    }
  });

  // 获取新闻源
  const { data: sources = [] } = useQuery({
    queryKey: ['news-sources'],
    queryFn: async () => {
      const response = await api.get('/api/news/sources');
      return response.data;
    }
  });

  // 处理搜索
  const handleSearch = (value: string) => {
    setSearchKeyword(value);
    setCurrentPage(1);
  };

  // 处理筛选变化
  const handleFilterChange = (filters: any) => {
    setSelectedCategory(filters.category || '');
    setSelectedSource(filters.source || '');
    setSelectedSentiment(filters.sentiment || '');
    setDateRange(filters.dateRange || null);
    setCurrentPage(1);
  };

  // 处理排序变化
  const handleSortChange = (by: string, order: string) => {
    setSortBy(by);
    setSortOrder(order);
    setCurrentPage(1);
  };

  // 处理页码变化
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  // 刷新数据
  const handleRefresh = () => {
    refetch();
  };

  // 渲染情感标签
  const renderSentimentTag = (sentiment: string) => {
    const sentimentConfig = {
      positive: { color: 'green', icon: <TrendingUpOutlined />, text: '利好' },
      negative: { color: 'red', icon: <TrendingDownOutlined />, text: '利空' },
      neutral: { color: 'default', icon: <MinusOutlined />, text: '中性' }
    };

    const config = sentimentConfig[sentiment as keyof typeof sentimentConfig] || sentimentConfig.neutral;

    return (
      <Tag color={config.color} icon={config.icon}>
        {config.text}
      </Tag>
    );
  };

  // 渲染新闻条目
  const renderNewsItem = (item: NewsItem) => {
    const sentiment = item.tags?.find(tag => ['positive', 'negative', 'neutral'].includes(tag)) || 'neutral';

    return (
      <List.Item
        key={item.id}
        className="cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={() => onNewsClick?.(item)}
        actions={[
          <Tooltip title="查看详情">
            <Button type="text" icon={<EyeOutlined />} />
          </Tooltip>,
          <Tooltip title="分享">
            <Button type="text" icon={<ShareAltOutlined />} />
          </Tooltip>
        ]}
      >
        <List.Item.Meta
          avatar={
            <Avatar
              style={{ backgroundColor: '#1890ff' }}
              icon={<MessageOutlined />}
              src={item.image_url}
            />
          }
          title={
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Title level={5} className="mb-0 !text-base line-clamp-1">
                  {item.title}
                </Title>
                <Space>
                  {item.category && (
                    <Tag color="blue">{item.category}</Tag>
                  )}
                  {renderSentimentTag(sentiment)}
                  {item.mentioned_stocks.length > 0 && (
                    <Badge count={item.mentioned_stocks.length} color="orange">
                      <Tag color="orange">相关股票</Tag>
                    </Badge>
                  )}
                </Space>
              </div>
              <div className="flex items-center space-x-4 text-xs text-gray-500">
                <span>{item.source}</span>
                {item.publish_time && (
                  <span>{formatRelativeTime(item.publish_time)}</span>
                )}
                {item.relevance_score > 0.7 && (
                  <Tag color="gold" className="text-xs">高相关</Tag>
                )}
              </div>
            </div>
          }
          description={
            <div className="space-y-2">
              <Paragraph
                ellipsis={{ rows: 2, expandable: true }}
                className="mb-0 text-sm text-gray-600"
              >
                {item.summary}
              </Paragraph>

              {/* 关键词 */}
              {item.keywords && item.keywords.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {item.keywords.slice(0, 5).map((keyword, index) => (
                    <Tag key={index} className="text-xs">
                      {keyword}
                    </Tag>
                  ))}
                  {item.keywords.length > 5 && (
                    <Tag className="text-xs">+{item.keywords.length - 5}</Tag>
                  )}
                </div>
              )}

              {/* 相关股票 */}
              {item.mentioned_stocks && item.mentioned_stocks.length > 0 && (
                <div className="flex items-center space-x-2">
                  <Text className="text-xs text-gray-500">相关股票:</Text>
                  <div className="flex flex-wrap gap-1">
                    {item.mentioned_stocks.slice(0, 3).map((stock, index) => (
                      <Tag key={index} color="orange" className="text-xs">
                        {stock}
                      </Tag>
                    ))}
                    {item.mentioned_stocks.length > 3 && (
                      <Tag className="text-xs">+{item.mentioned_stocks.length - 3}</Tag>
                    )}
                  </div>
                </div>
              )}
            </div>
          }
        />
      </List.Item>
    );
  };

  // 筛选菜单
  const filterMenuItems: MenuProps['items'] = [
    {
      key: 'category',
      label: '分类',
      children: categories.map((cat: any) => ({
        key: cat.value,
        label: cat.label,
        onClick: () => setSelectedCategory(cat.value)
      }))
    },
    {
      key: 'source',
      label: '来源',
      children: sources.map((source: any) => ({
        key: source.name,
        label: source.name,
        onClick: () => setSelectedSource(source.name)
      }))
    },
    {
      key: 'sentiment',
      label: '情感',
      children: [
        { key: 'positive', label: '利好', onClick: () => setSelectedSentiment('positive') },
        { key: 'negative', label: '利空', onClick: () => setSelectedSentiment('negative') },
        { key: 'neutral', label: '中性', onClick: () => setSelectedSentiment('neutral') }
      ]
    }
  ];

  return (
    <Card
      title={
        showHeader ? (
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <MessageOutlined className="text-blue-500" />
              <span>新闻资讯</span>
              {stockCode && (
                <Tag color="orange">{stockCode} 相关</Tag>
              )}
            </div>
            <Space>
              <Button
                type="text"
                icon={<ReloadOutlined />}
                onClick={handleRefresh}
                loading={isLoading}
              >
                刷新
              </Button>
            </Space>
          </div>
        ) : null
      }
      className="h-full"
      bodyStyle={{ padding: 0, height: showHeader ? 'calc(100% - 60px)' : '100%', overflow: 'hidden' }}
    >
      <div className="flex flex-col h-full">
        {/* 搜索和筛选栏 */}
        {showFilters && (
          <div className="p-4 border-b bg-gray-50">
            <Row gutter={[16, 8]} align="middle">
              <Col xs={24} sm={12} md={8}>
                <Search
                  placeholder="搜索新闻..."
                  value={searchKeyword}
                  onChange={(e) => setSearchKeyword(e.target.value)}
                  onSearch={handleSearch}
                  style={{ width: '100%' }}
                  allowClear
                />
              </Col>
              <Col xs={24} sm={12} md={8}>
                <Space wrap>
                  <Dropdown menu={{ items: filterMenuItems }} placement="bottomLeft">
                    <Button icon={<FilterOutlined />}>
                      筛选
                    </Button>
                  </Dropdown>
                  <RangePicker
                    value={dateRange}
                    onChange={setDateRange}
                    format="YYYY-MM-DD"
                    placeholder={['开始日期', '结束日期']}
                  />
                </Space>
              </Col>
              <Col xs={24} sm={24} md={8}>
                <Space wrap>
                  <Select
                    placeholder="排序"
                    value={`${sortBy}_${sortOrder}`}
                    onChange={(value) => {
                      const [by, order] = value.split('_');
                      handleSortChange(by, order);
                    }}
                    style={{ width: 120 }}
                  >
                    <Option value="publish_time_desc">最新发布</Option>
                    <Option value="publish_time_asc">最早发布</Option>
                    <Option value="relevance_score_desc">相关度</Option>
                  </Select>
                  {(selectedCategory || selectedSource || selectedSentiment || dateRange) && (
                    <Button
                      size="small"
                      onClick={() => handleFilterChange({
                        category: '',
                        source: '',
                        sentiment: '',
                        dateRange: null
                      })}
                    >
                      清空筛选
                    </Button>
                  )}
                </Space>
              </Col>
            </Row>

            {/* 筛选状态显示 */}
            <div className="flex items-center space-x-2 mt-2">
              {selectedCategory && (
                <Tag color="blue" closable onClose={() => setSelectedCategory('')}>
                  分类: {selectedCategory}
                </Tag>
              )}
              {selectedSource && (
                <Tag color="green" closable onClose={() => setSelectedSource('')}>
                  来源: {selectedSource}
                </Tag>
              )}
              {selectedSentiment && (
                <Tag color="orange" closable onClose={() => setSelectedSentiment('')}>
                  情感: {selectedSentiment}
                </Tag>
              )}
              {dateRange && (
                <Tag color="purple" closable onClose={() => setDateRange(null)}>
                  日期: {dateRange[0].format('MM-DD')} - {dateRange[1].format('MM-DD')}
                </Tag>
              )}
            </div>
          </div>
        )}

        {/* 新闻列表 */}
        <div className="flex-1 overflow-y-auto">
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <Spin size="large" />
            </div>
          ) : error ? (
            <div className="flex items-center justify-center h-64">
              <Empty description="加载失败，请重试" />
            </div>
          ) : newsData?.data && newsData.data.length > 0 ? (
            <div className="p-4">
              <List
                dataSource={newsData.data}
                renderItem={renderNewsItem}
                split={false}
              />

              {/* 分页 */}
              <div className="flex justify-center mt-4">
                <Pagination
                  current={currentPage}
                  total={newsData.total}
                  pageSize={limit}
                  showSizeChanger={false}
                  showQuickJumper
                  showTotal={(total, range) =>
                    `第 ${range[0]}-${range[1]} 条，共 ${total} 条`
                  }
                  onChange={handlePageChange}
                />
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-64">
              <Empty
                image={Empty.PRESENTED_IMAGE_SIMPLE}
                description="暂无相关新闻"
              />
            </div>
          )}
        </div>
      </div>
    </Card>
  );
};

export default NewsList;