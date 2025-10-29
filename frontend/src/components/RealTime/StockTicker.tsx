/**
 * 实时股票行情组件
 * 显示股票价格变动和市场指数
 */

import React, { useState, useEffect, useRef } from 'react';
import { Card, Row, Col, Statistic, Tag, Space, Badge, Typography, Tooltip } from 'antd';
import {
  TrendingUpOutlined,
  TrendingDownOutlined,
  MinusOutlined,
  ReloadOutlined,
  SettingOutlined
} from '@ant-design/icons';
import { websocketManager, WEBSOCKET_CONNECTIONS, ConnectionStatus } from '@/services/websocket';
import { formatCurrency, formatPercent, formatNumber } from '@/utils/format';

const { Text } = Typography;

interface StockPrice {
  symbol: string;
  name: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
  turnover: number;
  high: number;
  low: number;
  open: number;
  close: number;
  timestamp: string;
  market: string;
}

interface MarketIndex {
  name: string;
  current: number;
  change: number;
  change_percent: number;
  volume: number;
  timestamp: string;
}

interface StockTickerProps {
  height?: number;
  showSettings?: boolean;
  customStocks?: string[];
}

const StockTicker: React.FC<StockTickerProps> = ({
  height = 120,
  showSettings = true,
  customStocks = []
}) => {
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>(ConnectionStatus.DISCONNECTED);
  const [hotStocks, setHotStocks] = useState<StockPrice[]>([]);
  const [marketIndices, setMarketIndices] = useState<MarketIndex[]>([]);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [subscribedStocks, setSubscribedStocks] = useState<Set<string>>(new Set(customStocks));

  const unsubscribersRef = useRef<(() => void)[]>([]);

  useEffect(() => {
    connectWebSocket();
    return () => {
      disconnectWebSocket();
    };
  }, []);

  useEffect(() => {
    setSubscribedStocks(new Set(customStocks));
  }, [customStocks]);

  const connectWebSocket = async () => {
    try {
      await websocketManager.connect(WEBSOCKET_CONNECTIONS.STOCK_DATA, {
        url: '/api/realtime/stock',
        token: localStorage.getItem('token') || undefined
      });

      setConnectionStatus(ConnectionStatus.CONNECTED);

      // 订阅消息
      const unsubscribeRealtime = websocketManager.subscribeByType(
        WEBSOCKET_CONNECTIONS.STOCK_DATA,
        'data',
        handleRealtimeData
      );

      const unsubscribeStock = websocketManager.subscribeByType(
        WEBSOCKET_CONNECTIONS.STOCK_DATA,
        'stock',
        handleStockData
      );

      unsubscribersRef.current = [unsubscribeRealtime, unsubscribeStock];

      // 订阅热门股票
      hotStocks.forEach(stock => {
        websocketManager.send(WEBSOCKET_CONNECTIONS.STOCK_DATA, {
          type: 'subscribe',
          data: { subscription: stock.symbol }
        });
      });

    } catch (error) {
      console.error('连接股票数据WebSocket失败:', error);
      setConnectionStatus(ConnectionStatus.ERROR);
    }
  };

  const disconnectWebSocket = () => {
    unsubscribersRef.current.forEach(unsubscribe => unsubscribe());
    websocketManager.disconnect(WEBSOCKET_CONNECTIONS.STOCK_DATA);
    setConnectionStatus(ConnectionStatus.DISCONNECTED);
  };

  const handleRealtimeData = (data: any) => {
    try {
      setLastUpdate(new Date());

      if (data.hot_stocks) {
        setHotStocks(data.hot_stocks);
      }

      if (data.indices) {
        setMarketIndices(data.indices);
      }
    } catch (error) {
      console.error('处理实时数据失败:', error);
    }
  };

  const handleStockData = (data: any) => {
    try {
      const stockData: StockPrice = data.stock;
      setHotStocks(prev => {
        const index = prev.findIndex(stock => stock.symbol === stockData.symbol);
        if (index >= 0) {
          const newStocks = [...prev];
          newStocks[index] = stockData;
          return newStocks;
        }
        return [...prev, stockData];
      });
    } catch (error) {
      console.error('处理股票数据失败:', error);
    }
  };

  const renderTrendIcon = (change: number) => {
    if (change > 0) {
      return <TrendingUpOutlined className="text-red-500" />;
    } else if (change < 0) {
      return <TrendingDownOutlined className="text-green-500" />;
    }
    return <MinusOutlined className="text-gray-500" />;
  };

  const renderTrendColor = (value: number) => {
    if (value > 0) return 'text-red-500';
    if (value < 0) return 'text-green-500';
    return 'text-gray-500';
  };

  const renderMarketIndex = (index: MarketIndex) => (
    <Col key={index.name} xs={24} sm={12} md={8}>
      <Card size="small" className="h-full">
        <div className="text-center">
          <Text strong className="text-sm">{index.name}</Text>
          <div className="mt-1">
            <Statistic
              value={index.current}
              precision={2}
              valueStyle={{ fontSize: '16px', fontWeight: 'bold' }}
              prefix={renderTrendIcon(index.change)}
            />
          </div>
          <div className={`text-xs ${renderTrendColor(index.change)}`}>
            {index.change >= 0 ? '+' : ''}{index.change.toFixed(2)}
            ({index.change_percent >= 0 ? '+' : ''}{index.change_percent.toFixed(2)}%)
          </div>
        </div>
      </Card>
    </Col>
  );

  const renderHotStock = (stock: StockPrice, index: number) => (
    <Col key={stock.symbol} xs={12} sm={8} md={6}>
      <Card
        size="small"
        className="h-full cursor-pointer hover:shadow-md transition-shadow"
        onClick={() => window.open(`/stock/${stock.symbol}`, '_blank')}
      >
        <div className="text-center">
          <div className="flex items-center justify-center space-x-1">
            <Badge count={index + 1} color="blue" />
            <Text strong className="text-xs">{stock.symbol}</Text>
          </div>
          <div className="mt-1">
            <Statistic
              value={stock.price}
              precision={2}
              valueStyle={{ fontSize: '14px' }}
            />
          </div>
          <div className={`text-xs ${renderTrendColor(stock.change)}`}>
            {renderTrendIcon(stock.change)}
            {formatPercent(stock.change_percent / 100)}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            成交量: {formatNumber(stock.volume)}
          </div>
        </div>
      </Card>
    </Col>
  );

  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case ConnectionStatus.CONNECTED:
        return 'green';
      case ConnectionStatus.CONNECTING:
      case ConnectionStatus.RECONNECTING:
        return 'orange';
      case ConnectionStatus.ERROR:
        return 'red';
      default:
        return 'default';
    }
  };

  const getConnectionStatusText = () => {
    switch (connectionStatus) {
      case ConnectionStatus.CONNECTED:
        return '已连接';
      case ConnectionStatus.CONNECTING:
        return '连接中...';
      case ConnectionStatus.RECONNECTING:
        return '重连中...';
      case ConnectionStatus.ERROR:
        return '连接错误';
      default:
        return '未连接';
    }
  };

  return (
    <Card
      className="stock-ticker"
      bodyStyle={{ padding: '12px' }}
      title={
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="font-semibold">实时行情</span>
            <Tag color={getConnectionStatusColor()} size="small">
              {getConnectionStatusText()}
            </Tag>
            {lastUpdate && (
              <Text type="secondary" className="text-xs">
                更新: {lastUpdate.toLocaleTimeString()}
              </Text>
            )}
          </div>
          {showSettings && (
            <Space>
              <Tooltip title="刷新连接">
                <Button
                  type="text"
                  size="small"
                  icon={<ReloadOutlined />}
                  onClick={connectionStatus === ConnectionStatus.CONNECTED ? disconnectWebSocket : connectWebSocket}
                />
              </Tooltip>
              <Tooltip title="设置">
                <Button
                  type="text"
                  size="small"
                  icon={<SettingOutlined />}
                  onClick={() => console.log('打开设置')}
                />
              </Tooltip>
            </Space>
          )}
        </div>
      }
    >
      <div style={{ height: height - 60, overflow: 'hidden' }}>
        {/* 市场指数 */}
        {marketIndices.length > 0 && (
          <div className="mb-4">
            <Text strong className="text-sm mb-2 block">市场指数</Text>
            <Row gutter={[8, 8]}>
              {marketIndices.map(renderMarketIndex)}
            </Row>
          </div>
        )}

        {/* 热门股票 */}
        {hotStocks.length > 0 && (
          <div>
            <Text strong className="text-sm mb-2 block">热门股票</Text>
            <Row gutter={[8, 8]}>
              {hotStocks.slice(0, 8).map((stock, index) => renderHotStock(stock, index))}
            </Row>
          </div>
        )}

        {/* 无数据状态 */}
        {hotStocks.length === 0 && marketIndices.length === 0 && (
          <div className="flex items-center justify-center h-full text-gray-500">
            <div className="text-center">
              <div className="text-lg mb-2">📊</div>
              <div>等待实时数据...</div>
              {connectionStatus === ConnectionStatus.DISCONNECTED && (
                <Button
                  type="link"
                  size="small"
                  onClick={connectWebSocket}
                  className="mt-2"
                >
                  重新连接
                </Button>
              )}
            </div>
          </div>
        )}
      </div>
    </Card>
  );
};

export default StockTicker;