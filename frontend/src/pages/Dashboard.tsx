import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Statistic, Typography, Space, Button, Badge } from 'antd';
import {
  ReloadOutlined,
  SettingOutlined,
  FullscreenOutlined,
  FullscreenExitOutlined
} from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';

import StockList from '@/components/Stock/StockList';
import KLineChart from '@/components/Charts/KLineChart';
import TechnicalIndicatorsChart from '@/components/Charts/TechnicalIndicatorsChart';
import { AIAnalysisPanel } from '@/components/AI';
import { NewsPanel } from '@/components/News';
import { StockTicker, NewsNotification } from '@/components/RealTime';
import { api } from '@/services/api';
import { formatCurrency, formatPercent } from '@/utils/format';

const { Title, Text } = Typography;

interface MarketOverview {
  total_stocks: number;
  up_stocks: number;
  down_stocks: number;
  flat_stocks: number;
  market_cap: number;
  turnover: number;
  updated_at: string;
}

interface HotStock {
  symbol: string;
  name: string;
  change_percent: number;
  volume: number;
  turnover: number;
}

const Dashboard: React.FC = () => {
  const [selectedStock, setSelectedStock] = useState<string | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);

  // 获取市场概览
  const {
    data: marketOverview,
    isLoading: marketLoading,
    refetch: refetchMarket
  } = useQuery<MarketOverview>({
    queryKey: ['market-overview'],
    queryFn: async () => {
      // 这里可以创建一个市场概览API
      // 暂时返回模拟数据
      const response = await api.get('/api/stocks/list?page=1&size=1');
      return {
        total_stocks: 5000,
        up_stocks: 2500,
        down_stocks: 2300,
        flat_stocks: 200,
        market_cap: 5000000000000,
        turnover: 80000000000,
        updated_at: new Date().toISOString()
      };
    },
    refetchInterval: 30000, // 30秒刷新
  });

  // 获取热门股票
  const {
    data: hotStocks,
    isLoading: hotStocksLoading,
    refetch: refetchHotStocks
  } = useQuery<HotStock[]>({
    queryKey: ['hot-stocks'],
    queryFn: async () => {
      // 这里可以创建一个热门股票API
      // 暂时返回模拟数据
      const response = await api.get('/api/stocks/list?page=1&size=10');
      return response.data.data?.slice(0, 10).map((stock: any) => ({
        ...stock,
        change_percent: stock.change_percent || 0
      })) || [];
    },
    refetchInterval: 60000, // 1分钟刷新
  });

  // 全屏切换
  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  // 监听全屏变化
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
    };
  }, []);

  // 处理股票选择
  const handleStockSelect = (stock: any) => {
    setSelectedStock(stock.symbol);
  };

  // 计算涨跌比例
  const upPercent = marketOverview?.total_stocks
    ? ((marketOverview.up_stocks / marketOverview.total_stocks) * 100).toFixed(1)
    : '0';

  const downPercent = marketOverview?.total_stocks
    ? ((marketOverview.down_stocks / marketOverview.total_stocks) * 100).toFixed(1)
    : '0';

  return (
    <div className="p-6">
      {/* 页面标题和操作栏 */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <Title level={2} className="mb-2">智能股票看板</Title>
          <Text type="secondary">
            实时监控股票市场动态，提供专业的投资决策支持
          </Text>
        </div>
        <Space>
          <NewsNotification />
          <Button
            icon={<SettingOutlined />}
            onClick={() => console.log('打开设置')}
          >
            设置
          </Button>
          <Button
            icon={isFullscreen ? <FullscreenExitOutlined /> : <FullscreenOutlined />}
            onClick={toggleFullscreen}
          >
            {isFullscreen ? '退出全屏' : '全屏'}
          </Button>
          <Button
            icon={<ReloadOutlined />}
            onClick={() => {
              refetchMarket();
              refetchHotStocks();
            }}
            loading={marketLoading || hotStocksLoading}
          >
            刷新数据
          </Button>
        </Space>
      </div>

      {/* 实时行情组件 */}
      <div className="mb-6">
        <StockTicker height={120} />
      </div>

      {/* 市场概览统计 */}
      <Row gutter={[16, 16]} className="mb-6">
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="股票总数"
              value={marketOverview?.total_stocks || 0}
              valueStyle={{ color: '#1890ff' }}
              prefix={<Badge count="A" style={{ backgroundColor: '#1890ff' }} />}
            />
            <div className="mt-2 text-xs text-gray-500">
              更新时间: {marketOverview?.updated_at ?
                new Date(marketOverview.updated_at).toLocaleTimeString() :
                'Loading...'
              }
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="上涨股票"
              value={marketOverview?.up_stocks || 0}
              valueStyle={{ color: '#f5222d' }}
              suffix={`/ ${marketOverview?.total_stocks || 0}`}
              prefix={<div className="w-2 h-2 bg-red-500 rounded-full mr-2" />}
            />
            <div className="mt-2 text-xs text-gray-500">
              占比: {upPercent}%
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="下跌股票"
              value={marketOverview?.down_stocks || 0}
              valueStyle={{ color: '#52c41a' }}
              suffix={`/ ${marketOverview?.total_stocks || 0}`}
              prefix={<div className="w-2 h-2 bg-green-500 rounded-full mr-2" />}
            />
            <div className="mt-2 text-xs text-gray-500">
              占比: {downPercent}%
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="总成交额"
              value={marketOverview?.turnover || 0}
              valueStyle={{ color: '#722ed1' }}
              formatter={(value) => formatCurrency(Number(value))}
              prefix="¥"
            />
            <div className="mt-2 text-xs text-gray-500">
              市场活跃度指标
            </div>
          </Card>
        </Col>
      </Row>

      {/* 主要内容区域 */}
      <Row gutter={[16, 16]}>
        {/* 左侧 - 股票列表和AI分析 */}
        <Col xs={24} lg={16}>
          <Row gutter={[16, 16]}>
            {/* 股票列表 */}
            <Col xs={24} lg={14}>
              <StockList
                onStockSelect={handleStockSelect}
                showRealtime={true}
                pageSize={10}
              />
            </Col>

            {/* AI分析面板 */}
            <Col xs={24} lg={10}>
              {selectedStock ? (
                <AIAnalysisPanel
                  symbol={selectedStock}
                  onAnalysisComplete={(result) => console.log('AI分析完成:', result)}
                />
              ) : (
                <Card className="h-full">
                  <div className="flex flex-col items-center justify-center h-64 text-gray-500">
                    <RobotOutlined className="text-4xl mb-4" />
                    <Title level={5} type="secondary">AI投资分析师</Title>
                    <Text type="secondary">选择股票开始智能分析</Text>
                  </div>
                </Card>
              )}
            </Col>
          </Row>
        </Col>

        {/* 右侧 - 图表和新闻 */}
        <Col xs={24} lg={8}>
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            {/* K线图 */}
            {selectedStock && (
              <KLineChart
                symbol={selectedStock}
                height={280}
                showVolume={true}
                showTechnicalIndicators={true}
              />
            )}

            {/* 技术指标图 */}
            {selectedStock && (
              <TechnicalIndicatorsChart
                symbol={selectedStock}
                period="daily"
                height={220}
              />
            )}

            {/* 新闻面板 */}
            <NewsPanel
              stockCode={selectedStock}
              height={350}
              limit={5}
              showHeader={true}
            />

            {/* 热门股票 */}
            <Card
              title="热门股票"
              extra={
                <Button
                  size="small"
                  icon={<ReloadOutlined />}
                  onClick={() => refetchHotStocks()}
                  loading={hotStocksLoading}
                >
                  刷新
                </Button>
              }
            >
              <div className="space-y-2">
                {hotStocks?.map((stock, index) => (
                  <div
                    key={stock.symbol}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded hover:bg-gray-100 cursor-pointer transition-colors"
                    onClick={() => setSelectedStock(stock.symbol)}
                  >
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center text-xs font-bold">
                        {index + 1}
                      </div>
                      <div>
                        <div className="font-semibold text-sm">
                          {stock.symbol}
                        </div>
                        <div className="text-xs text-gray-500">
                          {stock.name}
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className={`font-semibold text-sm ${
                        stock.change_percent >= 0 ? 'text-red-500' : 'text-green-500'
                      }`}>
                        {stock.change_percent >= 0 ? '+' : ''}
                        {formatPercent(stock.change_percent / 100)}
                      </div>
                      <div className="text-xs text-gray-500">
                        成交量: {(stock.volume / 10000).toFixed(1)}万手
                      </div>
                    </div>
                  </div>
                ))}

                {!hotStocks || hotStocks.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    暂无热门股票数据
                  </div>
                ) : null}
              </div>
            </Card>
          </Space>
        </Col>
      </Row>

      {/* 底部信息栏 */}
      <div className="mt-6 p-4 bg-gray-50 rounded">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <div>
            <span className="mr-4">
              数据来源: AKShare (akshare.com)
            </span>
            <span className="mr-4">
              更新频率: 实时数据5秒，基础数据1分钟
            </span>
            <span>
              免责声明: 投资有风险，入市需谨慎
            </span>
          </div>
          <div>
            {isFullscreen && (
              <span className="mr-4">
                按 ESC 退出全屏
              </span>
            )}
            <span>
              智股通 v1.0.0 - 专业的AI投资研究平台
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;