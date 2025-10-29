import React, { useState, useEffect } from 'react';
import {
  Row,
  Col,
  Card,
  Input,
  Button,
  Space,
  Typography,
  Alert,
  Divider,
  Tabs,
  Select,
  AutoComplete
} from 'antd';
import {
  SearchOutlined,
  RobotOutlined,
  LineChartOutlined,
  BulbOutlined,
  FireOutlined,
  SafetyCertificateOutlined,
  HistoryOutlined
} from '@ant-design/icons';
import { ExpertRoundTable } from '@/components/AI/ExpertRoundTable';
import { api } from '@/services/api';

const { Title, Text, Paragraph } = Typography;

const { TabPane } = Tabs;

interface StockInfo {
  symbol: string;
  name: string;
  current_price: number;
  change: number;
  change_percent: number;
  volume: number;
}

const AIAnalysis: React.FC = () => {
  const [symbol, setSymbol] = useState('');
  const [searchHistory, setSearchHistory] = useState<string[]>([]);
  const [currentStock, setCurrentStock] = useState<StockInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('roundtable');

  // 常见股票代码建议
  const commonStocks = [
    { symbol: '000001', name: '平安银行' },
    { symbol: '000002', name: '万科A' },
    { symbol: '000858', name: '五粮液' },
    { symbol: '600036', name: '招商银行' },
    { symbol: '600519', name: '贵州茅台' },
    { symbol: '000858', name: '五粮液' },
    { symbol: '600000', name: '浦发银行' },
    { symbol: '600036', name: '招商银行' },
    { symbol: '000001', name: '平安银行' }
  ];

  // 从本地存储加载搜索历史
  useEffect(() => {
    const saved = localStorage.getItem('stock-search-history');
    if (saved) {
      try {
        setSearchHistory(JSON.parse(saved));
      } catch (error) {
        console.error('加载搜索历史失败:', error);
      }
    }
  }, []);

  // 保存搜索历史到本地存储
  const saveSearchHistory = (newSymbol: string) => {
    const updated = [newSymbol, ...searchHistory.filter(s => s !== newSymbol)].slice(0, 10);
    setSearchHistory(updated);
    localStorage.setItem('stock-search-history', JSON.stringify(updated));
  };

  // 搜索股票
  const searchStock = async (searchSymbol: string) => {
    if (!searchSymbol.trim()) return;

    setLoading(true);
    try {
      // 先检查是否为6位数字（股票代码）
      const codePattern = /^\d{6}$/;
      let finalSymbol = searchSymbol;

      if (!codePattern.test(searchSymbol)) {
        // 如果不是6位数字，尝试转换
        // 这里可以添加更多的转换逻辑
        finalSymbol = searchSymbol.padStart(6, '0');
      }

      const response = await api.get(`/api/stock/${finalSymbol}/info`);

      if (response.data.success) {
        setCurrentStock(response.data.data);
        setSymbol(finalSymbol);
        saveSearchHistory(finalSymbol);
      } else {
        throw new Error('未找到股票信息');
      }
    } catch (error) {
      console.error('搜索股票失败:', error);
      setCurrentStock(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    searchStock(symbol);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handleSymbolSelect = (value: string) => {
    setSymbol(value);
    searchStock(value);
  };

  const clearHistory = () => {
    setSearchHistory([]);
    localStorage.removeItem('stock-search-history');
  };

  return (
    <div className="p-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <Title level={2}>
            <RobotOutlined className="mr-2" />
            AI智能分析
          </Title>
          <Text type="secondary">
            基于GLM-4.5-Flash的专业投资分析平台
          </Text>
        </div>
        <Space>
          <Button
            icon={<HistoryOutlined />}
            onClick={clearHistory}
            disabled={searchHistory.length === 0}
          >
            清空历史
          </Button>
        </Space>
      </div>

      {/* 搜索区域 */}
      <Card className="mb-6">
        <div className="flex gap-4 items-center">
          <div className="flex-1">
            <AutoComplete
              style={{ width: '100%' }}
              placeholder="输入6位股票代码或选择常见股票"
              options={commonStocks.map(stock => ({
                value: stock.symbol,
                label: `${stock.symbol} - ${stock.name}`
              }))}
              onSelect={handleSymbolSelect}
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              filterOption={(inputValue, option) =>
                option.label.toLowerCase().includes(inputValue.toLowerCase())
              }
            >
              <Input.Search
                placeholder="输入股票代码"
                enterButton="搜索"
                size="large"
                loading={loading}
                onSearch={handleSearch}
                onPressEnter={handleKeyPress}
              />
            </AutoComplete>
          </div>
        </div>

        {/* 搜索历史 */}
        {searchHistory.length > 0 && (
          <div className="mt-4">
            <Text type="secondary" className="text-xs mb-2">
              搜索历史:
            </Text>
            <div className="flex flex-wrap gap-2">
              {searchHistory.map((stock) => (
                <Button
                  key={stock}
                  size="small"
                  onClick={() => handleSymbolSelect(stock)}
                >
                  {stock}
                </Button>
              ))}
            </div>
          </div>
        )}
      </Card>

      {/* 当前股票信息 */}
      {currentStock && (
        <Card className="mb-6">
          <Row gutter={16} align="middle">
            <Col>
              <div>
                <Title level={4}>{currentStock.name}</Title>
                <Text type="secondary">代码: {currentStock.symbol}</Text>
              </div>
            </Col>
            <Col>
              <div className="text-right">
                <div className="text-2xl font-bold">
                  ¥{currentStock.current_price.toFixed(2)}
                </div>
                <div
                  className={`text-sm ${
                    currentStock.change_percent >= 0 ? 'text-red-500' : 'text-green-500'
                  }`}
                >
                  {currentStock.change_percent >= 0 ? '+' : ''}
                  {currentStock.change_percent.toFixed(2)}%
                </div>
              </div>
            </Col>
            <Col>
              <div className="text-right">
                <div className="text-sm text-gray-500">成交量</div>
                <div className="font-semibold">
                  {(currentStock.volume / 10000).toFixed(1)}万手
                </div>
              </div>
            </Col>
          </Row>
        </Card>
      )}

      {/* 主要功能标签页 */}
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane
          tab={
            <span>
              <TeamOutlined className="mr-2" />
              专家圆桌会议
            </span>
          }
          key="roundtable"
        >
          {currentStock ? (
            <ExpertRoundTable symbol={currentStock.symbol} />
          ) : (
            <Card className="text-center py-16">
              <SearchOutlined className="text-6xl mb-4 text-gray-400" />
              <Title level={4} type="secondary">
                请先搜索股票
              </Title>
              <Paragraph type="secondary">
                输入股票代码开始专家圆桌会议分析
              </Paragraph>
            </Card>
          )}
        </TabPane>

        <TabPane
          tab={
            <span>
              <LineChartOutlined className="mr-2" />
              技术分析
            </span>
          }
          key="technical"
        >
          <Card className="text-center py-16">
            <LineChartOutlined className="text-6xl mb-4 text-gray-400" />
            <Title level={4} type="secondary">
              技术分析功能开发中
            </Title>
            <Paragraph type="secondary">
              即将推出专业技术指标分析功能
            </Paragraph>
          </Card>
        </TabPane>

        <TabPane
          tab={
            <span>
              <BulbOutlined className="mr-2" />
              基本面分析
            </span>
          }
          key="fundamental"
        >
          <Card className="text-center py-16">
            <BulbOutlined className="text-6xl mb-4 text-gray-400" />
            <Title level={4} type="secondary">
              基本面分析功能开发中
            </Title>
            <Paragraph type="secondary">
              即将推出专业基本面分析功能
            </Paragraph>
          </Card>
        </TabPane>

        <TabPane
          tab={
            <span>
              <FireOutlined className="mr-2" />
              新闻分析
            </span>
          }
          key="news"
        >
          <Card className="text-center py-16">
            <FireOutlined className="text-6xl mb-4 text-gray-400" />
            <Title level={4} type="secondary">
              新闻分析功能开发中
            </Title>
            <Paragraph type="secondary">
              即将推出新闻情感分析功能
            </Paragraph>
          </Card>
        </TabPane>

        <TabPane
          tab={
            <span>
              <SafetyCertificateOutlined className="mr-2" />
              风险评估
            </span>
          }
          key="risk"
        >
          <Card className="text-center py-16">
            <SafetyCertificateOutlined className="text-6xl mb-4 text-gray-400" />
            <Title level={4} type="secondary">
              风险评估功能开发中
            </Title>
            <Paragraph type="secondary">
              即将推出专业风险评估功能
            </Paragraph>
          </Card>
        </TabPane>
      </Tabs>

      {/* 功能介绍 */}
      {!currentStock && (
        <Alert
          message="AI分析功能介绍"
          description="智股通AI分析平台采用GLM-4.5-Flash大语言模型，为您提供专业的股票投资分析服务。专家圆桌会议系统汇聚四位专业分析师，从不同维度为您的投资决策提供参考。"
          type="info"
          showIcon
          className="mb-6"
        />
      )}

      {/* 功能特点 */}
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} md={6}>
          <Card size="small">
            <div className="text-center">
              <RobotOutlined className="text-2xl mb-2 text-blue-500" />
              <Title level={5}>AI驱动</Title>
              <Text type="secondary" className="text-xs">
                基于GLM-4.5-Flash大语言模型
              </Text>
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Card size="small">
            <div className="text-center">
              <TeamOutlined className="text-2xl mb-2 text-green-500" />
              <Title level={5}>专家团队</Title>
              <Text type="secondary" className="text-xs">
                四位专业分析师多维度分析
              </Text>
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Card size="small">
            <div className="text-center">
              <BulbOutlined className="text-2xl mb-2 text-orange-500" />
              <Title level={5}>实时分析</Title>
              <Text type="secondary" className="text-xs">
                实时数据驱动专业分析
              </Text>
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Card size="small">
            <div className="text-center">
              <SafetyCertificateOutlined className="text-2xl mb-2 text-red-500" />
              <Title level={5}>风险控制</Title>
              <Text type="secondary" className="text-xs">
                专业风险评估和仓位管理
              </Text>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default AIAnalysis;