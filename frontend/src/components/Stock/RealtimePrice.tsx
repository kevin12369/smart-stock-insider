import React, { useState, useEffect, useRef } from 'react';
import { Card, Typography, Tag, Button, Space, Tooltip } from 'antd';
import {
  RiseOutlined,
  FallOutlined,
  MinusOutlined,
  ReloadOutlined,
  SyncOutlined
} from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';

import { api } from '@/services/api';
import { formatCurrency, formatPercent, formatRelativeTime } from '@/utils/format';

const { Text } = Typography;

interface StockPrice {
  symbol: string;
  name: string;
  current_price: number;
  change_amount: number;
  change_percent: number;
  volume: number;
  turnover: number;
  high_price: number;
  low_price: number;
  open_price: number;
  prev_close: number;
  updated_at: string;
}

interface RealtimePriceProps {
  symbol: string;
  showDetails?: boolean;
  autoRefresh?: boolean;
  refreshInterval?: number;
  className?: string;
}

const RealtimePrice: React.FC<RealtimePriceProps> = ({
  symbol,
  showDetails = false,
  autoRefresh = true,
  refreshInterval = 5000,
  className
}) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<NodeJS.Timeout | null>(null);

  // 获取实时价格数据
  const {
    data: priceData,
    isLoading,
    error,
    refetch
  } = useQuery<StockPrice>({
    queryKey: ['realtime-price', symbol],
    queryFn: async () => {
      const response = await api.post('/api/stocks/realtime', {
        symbols: [symbol]
      });
      return response.data[0]; // 返回第一个股票的数据
    },
    refetchInterval: autoRefresh ? refreshInterval : false,
    enabled: !!symbol,
    onSuccess: (data) => {
      setLastUpdate(new Date());
      setIsConnected(true);
    },
    onError: () => {
      setIsConnected(false);
    }
  });

  // WebSocket连接用于实时更新
  useEffect(() => {
    if (!symbol || !autoRefresh) return;

    const connectWebSocket = () => {
      try {
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${wsProtocol}//${window.location.host}/ws/price/${symbol}`;

        wsRef.current = new WebSocket(wsUrl);

        wsRef.current.onopen = () => {
          console.log(`WebSocket连接成功: ${symbol}`);
          setIsConnected(true);
        };

        wsRef.current.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.symbol === symbol) {
              setLastUpdate(new Date());
              // 更新查询缓存
              queryClient.setQueryData(['realtime-price', symbol], data);
            }
          } catch (error) {
            console.error('解析WebSocket消息失败:', error);
          }
        };

        wsRef.current.onclose = () => {
          console.log(`WebSocket连接关闭: ${symbol}`);
          setIsConnected(false);
          // 5秒后尝试重连
          reconnectTimerRef.current = setTimeout(connectWebSocket, 5000);
        };

        wsRef.current.onerror = (error) => {
          console.error('WebSocket错误:', error);
          setIsConnected(false);
        };
      } catch (error) {
        console.error('创建WebSocket连接失败:', error);
        setIsConnected(false);
      }
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
      }
    };
  }, [symbol, autoRefresh]);

  // 手动刷新
  const handleRefresh = () => {
    refetch();
  };

  // 渲染涨跌标签
  const renderChangeTag = (changePercent: number) => {
    if (changePercent > 0) {
      return (
        <Tag color="red" icon={<RiseOutlined />}>
          +{formatPercent(changePercent / 100)}
        </Tag>
      );
    } else if (changePercent < 0) {
      return (
        <Tag color="green" icon={<FallOutlined />}>
          {formatPercent(changePercent / 100)}
        </Tag>
      );
    } else {
      return (
        <Tag color="default" icon={<MinusOutlined />}>
          0.00%
        </Tag>
      );
    }
  };

  // 渲染连接状态
  const renderConnectionStatus = () => {
    if (isConnected) {
      return (
        <Tooltip title="实时连接正常">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
        </Tooltip>
      );
    } else {
      return (
        <Tooltip title="连接已断开，使用HTTP轮询">
          <div className="w-2 h-2 bg-yellow-500 rounded-full" />
        </Tooltip>
      );
    }
  };

  if (error) {
    return (
    <Card className={className}>
      <div className="text-center py-4">
        <Text type="danger">获取价格数据失败</Text>
        <Button
          type="link"
          icon={<ReloadOutlined />}
          onClick={handleRefresh}
          className="ml-2"
        >
          重试
        </Button>
      </div>
    </Card>
    );
  }

  if (isLoading && !priceData) {
    return (
    <Card className={className}>
      <div className="text-center py-4">
        <SyncOutlined spin className="text-2xl" />
        <div className="mt-2 text-gray-500">加载中...</div>
      </div>
    </Card>
    );
  }

  if (!priceData) {
    return (
      <Card className={className}>
        <div className="text-center py-4 text-gray-500">
          暂无价格数据
        </div>
      </Card>
    );
  }

  const {
    current_price,
    change_amount,
    change_percent,
    volume,
    turnover,
    high_price,
    low_price,
    open_price,
    prev_close
  } = priceData;

  const changeColor = change_percent > 0 ? 'text-red-500' :
                      change_percent < 0 ? 'text-green-500' : 'text-gray-500';

  return (
    <Card className={className}>
      <div className="space-y-3">
        {/* 股票基本信息 */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Text strong className="text-lg font-mono">{symbol}</Text>
            {renderConnectionStatus()}
          </div>
          <Button
            type="text"
            size="small"
            icon={<ReloadOutlined />}
            onClick={handleRefresh}
            loading={isLoading}
          />
        </div>

        {/* 当前价格和涨跌 */}
        <div className="text-center">
          <div className={`text-3xl font-bold ${changeColor}`}>
            {formatCurrency(current_price)}
          </div>
          {renderChangeTag(change_percent)}
        </div>

        {/* 详细信息 */}
        {showDetails && (
          <div className="space-y-2 pt-3 border-t border-gray-200">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <Text type="secondary">开盘价</Text>
                <div className="font-semibold">{formatCurrency(open_price)}</div>
              </div>
              <div>
                <Text type="secondary">昨收价</Text>
                <div className="font-semibold">{formatCurrency(prev_close)}</div>
              </div>
              <div>
                <Text type="secondary">最高价</Text>
                <div className="font-semibold text-red-500">{formatCurrency(high_price)}</div>
              </div>
              <div>
                <Text type="secondary">最低价</Text>
                <div className="font-semibold text-green-500">{formatCurrency(low_price)}</div>
              </div>
              <div>
                <Text type="secondary">成交量</Text>
                <div className="font-semibold">
                  {(volume / 10000).toFixed(2)}万手
                </div>
              </div>
              <div>
                <Text type="secondary">成交额</Text>
                <div className="font-semibold">
                  {formatCurrency(turnover)}
                </div>
              </div>
            </div>

            {/* 涨跌额和涨跌幅 */}
            <div className="grid grid-cols-2 gap-4 text-sm pt-2">
              <div>
                <Text type="secondary">涨跌额</Text>
                <div className={`font-semibold ${changeColor}`}>
                  {change_amount >= 0 ? '+' : ''}
                  {formatCurrency(change_amount)}
                </div>
              </div>
              <div>
                <Text type="secondary">涨跌幅</Text>
                <div className={`font-semibold ${changeColor}`}>
                  {formatPercent(change_percent / 100)}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 更新时间 */}
        <div className="text-xs text-gray-500 text-center pt-2 border-t border-gray-200">
          最后更新: {formatRelativeTime(lastUpdate)}
        </div>
      </div>
    </Card>
  );
};

export default RealtimePrice;