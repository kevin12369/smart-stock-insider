import React, { useState, useEffect, useMemo } from 'react';
import {
  Table,
  Card,
  Input,
  Select,
  Button,
  Space,
  Tag,
  Tooltip,
  Typography,
  Pagination,
  Row,
  Col,
  Badge,
  Switch,
  Divider
} from 'antd';
import {
  SearchOutlined,
  ReloadOutlined,
  StarOutlined,
  StarFilled,
  RiseOutlined,
  FallOutlined,
  MinusOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { debounce } from 'lodash-es';

import { apiClient } from '@/services/api';
import { useWatchlistStore } from '@/stores/watchlistStore';
import { formatNumber, formatPercent, formatCurrency } from '@/utils/format';

const { Title, Text } = Typography;
const { Option } = Select;

interface StockItem {
  id: number;
  symbol: string;
  name: string;
  market: string;
  sector: string;
  industry: string;
  current_price?: number;
  change_amount?: number;
  change_percent?: number;
  volume?: number;
  turnover?: number;
  high_price?: number;
  low_price?: number;
  open_price?: number;
  prev_close?: number;
  updated_at?: string;
}

interface StockListResponse {
  data: StockItem[];
  pagination: {
    page: number;
    size: number;
    total: number;
    pages: number;
  };
}

interface StockListProps {
  onStockSelect?: (stock: StockItem) => void;
  showRealtime?: boolean;
  pageSize?: number;
}

const StockList: React.FC<StockListProps> = ({
  onStockSelect,
  showRealtime = true,
  pageSize = 20
}) => {
  const [searchKeyword, setSearchKeyword] = useState('');
  const [selectedMarket, setSelectedMarket] = useState<string>('');
  const [selectedSector, setSelectedSector] = useState<string>('');
  const [currentPage, setCurrentPage] = useState(1);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(5000); // 5秒

  const queryClient = useQueryClient();
  const { watchlist, addToWatchlist, removeFromWatchlist } = useWatchlistStore();

  // 获取股票列表
  const {
    data: stockListData,
    isLoading,
    error,
    refetch
  } = useQuery<StockListResponse>({
    queryKey: ['stocks', currentPage, pageSize, selectedMarket, selectedSector],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: currentPage.toString(),
        size: pageSize.toString()
      });

      if (selectedMarket) params.append('market', selectedMarket);
      if (selectedSector) params.append('sector', selectedSector);

      const response = await apiClient.get(`/api/stocks/list?${params}`);
      return response.data;
    },
    refetchInterval: autoRefresh ? refreshInterval : false,
    staleTime: 30000, // 30秒内数据被认为是新鲜的
  });

  // 获取实时价格
  const { data: realtimeData } = useQuery({
    queryKey: ['realtime', 'all'],
    queryFn: async () => {
      if (stockListData?.data && showRealtime) {
        const symbols = stockListData.data.map(stock => stock.symbol);
        if (symbols.length > 0) {
          const response = await apiClient.post('/api/stocks/realtime', {
            symbols: symbols.slice(0, 50) // 限制一次最多50只股票
          });
          return response.data;
        }
      }
      return [];
    },
    refetchInterval: autoRefresh ? refreshInterval : false,
    enabled: showRealtime && !!stockListData?.data,
  });

  // 获取行业板块列表
  const { data: sectorsData } = useQuery({
    queryKey: ['sectors'],
    queryFn: async () => {
      const response = await apiClient.get('/api/stocks/sectors');
      return response.data;
    },
    staleTime: 3600000, // 1小时
  });

  // 搜索股票
  const {
    data: searchData,
    isLoading: isSearchLoading
  } = useQuery({
    queryKey: ['stock-search', searchKeyword],
    queryFn: async () => {
      if (searchKeyword.trim()) {
        const response = await apiClient.get(`/api/stocks/search?keyword=${encodeURIComponent(searchKeyword)}&limit=20`);
        return response.data;
      }
      return [];
    },
    enabled: searchKeyword.trim().length > 0,
  });

  // 合并实时数据到股票列表
  const enrichedStockData = useMemo(() => {
    if (!stockListData?.data) return [];

    return stockListData.data.map(stock => {
      const realtimeInfo = realtimeData?.find((item: any) => item.symbol === stock.symbol);
      return {
        ...stock,
        ...(realtimeInfo || {})
      };
    });
  }, [stockListData?.data, realtimeData]);

  // 防抖搜索
  const debouncedSearch = debounce((value: string) => {
    setSearchKeyword(value);
  }, 300);

  // 切换自选股状态
  const toggleWatchlist = async (stock: StockItem, e: React.MouseEvent) => {
    e.stopPropagation();

    const isInWatchlist = watchlist.some(item => item.symbol === stock.symbol);

    if (isInWatchlist) {
      await removeFromWatchlist(stock.symbol);
    } else {
      await addToWatchlist(stock);
    }
  };

  // 渲染涨跌标签
  const renderChangeTag = (changePercent: number) => {
    if (changePercent > 0) {
      return (
        <Tag color="red" icon={<RiseOutlined />}>
          +{formatPercent(changePercent)}
        </Tag>
      );
    } else if (changePercent < 0) {
      return (
        <Tag color="green" icon={<FallOutlined />}>
          {formatPercent(changePercent)}
        </Tag>
      );
    } else {
      return (
        <Tag color="default" icon={<MinusOutlined />}>
          {formatPercent(changePercent)}
        </Tag>
      );
    }
  };

  // 表格列定义
  const columns: ColumnsType<StockItem> = [
    {
      title: '代码',
      dataIndex: 'symbol',
      key: 'symbol',
      width: 100,
      fixed: 'left',
      render: (text: string, record: StockItem) => (
        <div className="flex items-center space-x-2">
          <Button
            type="text"
            size="small"
            icon={watchlist.some(item => item.symbol === text) ?
              <StarFilled style={{ color: '#faad14' }} /> :
              <StarOutlined />
            }
            onClick={(e) => toggleWatchlist(record, e)}
          />
          <Text strong className="font-mono">{text}</Text>
        </div>
      ),
    },
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      width: 120,
      ellipsis: {
        showTitle: false,
      },
      render: (text: string) => (
        <Tooltip placement="topLeft" title={text}>
          {text}
        </Tooltip>
      ),
    },
    {
      title: '当前价',
      dataIndex: 'current_price',
      key: 'current_price',
      width: 100,
      align: 'right',
      render: (price: number, record: StockItem) => (
        <div>
          <Text strong>{formatCurrency(price)}</Text>
          {renderChangeTag(record.change_percent || 0)}
        </div>
      ),
    },
    {
      title: '涨跌额',
      dataIndex: 'change_amount',
      key: 'change_amount',
      width: 80,
      align: 'right',
      render: (value: number) => (
        <Text className={value >= 0 ? 'text-red-500' : 'text-green-500'}>
          {value >= 0 ? '+' : ''}{formatCurrency(value)}
        </Text>
      ),
    },
    {
      title: '涨跌幅',
      dataIndex: 'change_percent',
      key: 'change_percent',
      width: 80,
      align: 'right',
      render: (value: number) => (
        <Text className={value >= 0 ? 'text-red-500' : 'text-green-500'}>
          {value >= 0 ? '+' : ''}{formatPercent(value)}
        </Text>
      ),
    },
    {
      title: '成交量',
      dataIndex: 'volume',
      key: 'volume',
      width: 100,
      align: 'right',
      render: (value: number) => (
        <Text className="text-xs">{formatNumber(value)}</Text>
      ),
    },
    {
      title: '成交额',
      dataIndex: 'turnover',
      key: 'turnover',
      width: 100,
      align: 'right',
      render: (value: number) => (
        <Text className="text-xs">{formatNumber(value)}</Text>
      ),
    },
    {
      title: '最高/最低',
      key: 'high_low',
      width: 120,
      render: (_, record: StockItem) => (
        <div className="text-xs">
          <div className="text-red-500">{formatCurrency(record.high_price)}</div>
          <div className="text-green-500">{formatCurrency(record.low_price)}</div>
        </div>
      ),
    },
    {
      title: '市场',
      dataIndex: 'market',
      key: 'market',
      width: 60,
      render: (market: string) => {
        const colors: Record<string, string> = {
          'SH': 'red',
          'SZ': 'blue',
          'BJ': 'orange'
        };
        return <Tag color={colors[market] || 'default'}>{market}</Tag>;
      },
    },
    {
      title: '行业',
      dataIndex: 'sector',
      key: 'sector',
      width: 100,
      ellipsis: true,
    },
  ];

  return (
    <Card
      title={
        <div className="flex items-center justify-between">
          <Title level={4} className="mb-0">股票列表</Title>
          <Space>
            <Tooltip title="自动刷新">
              <Switch
                checked={autoRefresh}
                onChange={setAutoRefresh}
                checkedChildren="开"
                unCheckedChildren="关"
              />
            </Tooltip>
            <Button
              icon={<ReloadOutlined />}
              onClick={() => refetch()}
              loading={isLoading}
            >
              刷新
            </Button>
          </Space>
        </div>
      }
      extra={
        <Space wrap>
          <Input.Search
            placeholder="搜索股票代码或名称"
            style={{ width: 200 }}
            onSearch={setSearchKeyword}
            onChange={(e) => debouncedSearch(e.target.value)}
            loading={isSearchLoading}
            allowClear
          />

          <Select
            placeholder="选择市场"
            style={{ width: 100 }}
            value={selectedMarket}
            onChange={setSelectedMarket}
            allowClear
          >
            <Option value="SH">上海</Option>
            <Option value="SZ">深圳</Option>
            <Option value="BJ">北京</Option>
          </Select>

          <Select
            placeholder="选择行业"
            style={{ width: 150 }}
            value={selectedSector}
            onChange={setSelectedSector}
            allowClear
            showSearch
            filterOption={(input, option) =>
              (option?.children as string)?.toLowerCase().includes(input.toLowerCase())
            }
          >
            {sectorsData?.map((sector: any) => (
              <Option key={sector.code} value={sector.name}>
                {sector.name}
              </Option>
            ))}
          </Select>
        </Space>
      }
    >
      {/* 搜索结果 */}
      {searchKeyword && searchData && searchData.length > 0 && (
        <div className="mb-4">
          <Divider>搜索结果</Divider>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
            {searchData.map((stock: StockItem) => (
              <Card
                key={stock.symbol}
                size="small"
                hoverable
                className="cursor-pointer"
                onClick={() => onStockSelect?.(stock)}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <Text strong>{stock.symbol}</Text>
                    <Text className="ml-2 text-gray-500">{stock.name}</Text>
                  </div>
                  {stock.change_percent !== undefined && renderChangeTag(stock.change_percent)}
                </div>
              </Card>
            ))}
          </div>
          <Divider />
        </div>
      )}

      {/* 股票列表表格 */}
      <Table
        columns={columns}
        dataSource={enrichedStockData}
        loading={isLoading}
        rowKey="id"
        pagination={false}
        scroll={{ x: 1200, y: 600 }}
        size="small"
        onRow={(record) => ({
          onClick: () => onStockSelect?.(record),
          className: 'cursor-pointer hover:bg-gray-50',
        })}
        rowClassName={(record) => {
          const change = record.change_percent || 0;
          if (change > 0) return 'bg-red-50';
          if (change < 0) return 'bg-green-50';
          return '';
        }}
      />

      {/* 分页 */}
      {stockListData?.pagination && (
        <div className="mt-4 flex justify-center">
          <Pagination
            current={currentPage}
            total={stockListData.pagination.total}
            pageSize={pageSize}
            showSizeChanger
            showQuickJumper
            showTotal={(total, range) =>
              `第 ${range[0]}-${range[1]} 条，共 ${total} 条`
            }
            onChange={(page) => setCurrentPage(page)}
            onShowSizeChange={(_, size) => {
              // 这里可以更新页面大小
              setCurrentPage(1);
            }}
          />
        </div>
      )}

      {/* 状态统计 */}
      <div className="mt-4 flex justify-between text-sm text-gray-500">
        <Space>
          <span>更新时间: {new Date().toLocaleTimeString()}</span>
          {realtimeData && (
            <Badge status="processing" text="实时数据" />
          )}
        </Space>
        <Space>
          {stockListData?.data && (
            <span>显示 {stockListData.data.length} 只股票</span>
          )}
        </Space>
      </div>
    </Card>
  );
};

export default StockList;