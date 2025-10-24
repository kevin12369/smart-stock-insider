# 智股通 API 文档

## 概述

智股通API提供完整的金融数据和投资分析服务，支持股票查询、技术信号、新闻推送、投资组合管理等功能。

### 基本信息

- **Base URL**: `http://localhost:8080/api`
- **版本**: v1.0
- **数据格式**: JSON
- **认证方式**: API Key (可选)

### 通用响应格式

```json
{
  "success": true,
  "message": "操作成功",
  "data": {...},
  "error": null,
  "time": "2024-01-15T10:30:00Z"
}
```

## 系统接口

### 健康检查

检查API服务状态和依赖组件健康度。

**请求**:
```http
GET /api/health
```

**响应**:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "database": {
      "connected": true,
      "query_time_ms": 12
    },
    "cache": {
      "hit_rate": 0.85,
      "size": 256
    },
    "services": {
      "akshare": true,
      "news_service": true,
      "ai_service": false
    }
  }
}
```

### 系统信息

获取系统基本信息和统计数据。

**请求**:
```http
GET /api/system/info
```

**响应**:
```json
{
  "success": true,
  "data": {
    "app_name": "智股通",
    "app_version": "1.0.0",
    "build_time": "2024-01-15T10:00:00Z",
    "uptime": "5天3小时",
    "database": {
      "path": "./data/smart_stock.db",
      "size": "256.7 MB",
      "stats": {
        "stock_basic": 5234,
        "stock_daily": 1256780,
        "technical_signals": 45678,
        "news_items": 123456
      }
    }
  }
}
```

## 股票数据接口

### 搜索股票

搜索和筛选股票数据。

**请求**:
```http
GET /api/stocks?keyword=平安&limit=20&offset=0&market=sh
```

**参数**:
- `keyword` (string): 搜索关键词
- `limit` (int): 返回数量限制，默认20，最大100
- `offset` (int): 偏移量，默认0
- `market` (string): 市场筛选 (sh/sz/bj)
- `industry` (string): 行业筛选
- `sector` (string): 板块筛选

**响应**:
```json
{
  "success": true,
  "data": {
    "stocks": [
      {
        "code": "000001",
        "name": "平安银行",
        "market": "sz",
        "industry": "银行",
        "sector": "金融",
        "listing_date": "1991-04-03",
        "current_price": 15.68,
        "change": 0.18,
        "change_percent": 1.16,
        "volume": 1234567,
        "market_cap": 304156789012
      }
    ],
    "total": 156,
    "limit": 20,
    "offset": 0
  }
}
```

### 股票详情

获取单个股票的详细信息。

**请求**:
```http
GET /api/stocks/{code}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "code": "000001",
    "name": "平安银行",
    "market": "sz",
    "industry": "银行",
    "sector": "金融",
    "listing_date": "1991-04-03",
    "total_shares": 19405918198,
    "float_shares": 19405918198,
    "pe": 5.87,
    "pb": 0.62,
    "roe": 10.56,
    "current_price": 15.68,
    "change": 0.18,
    "change_percent": 1.16,
    "high_52w": 20.89,
    "low_52w": 12.35
  }
}
```

### 日线数据

获取股票的日线历史数据。

**请求**:
```http
GET /api/stocks/{code}/daily?start_date=2024-01-01&end_date=2024-01-15&limit=200
```

**参数**:
- `start_date` (string): 开始日期 (YYYY-MM-DD)
- `end_date` (string): 结束日期 (YYYY-MM-DD)
- `limit` (int): 返回数据条数，默认200

**响应**:
```json
{
  "success": true,
  "data": {
    "code": "000001",
    "data": [
      {
        "date": "2024-01-15",
        "open": 15.50,
        "high": 15.88,
        "low": 15.42,
        "close": 15.68,
        "volume": 12345678,
        "amount": 1934567890.12,
        "change": 0.18,
        "change_percent": 1.16
      }
    ],
    "count": 15
  }
}
```

## 技术信号接口

### 获取技术信号

获取股票的技术分析信号。

**请求**:
```http
GET /api/stocks/{code}/signals?indicators=MACD,RSI,BOLL&limit=30
```

**参数**:
- `indicators` (string): 指标列表，逗号分隔
- `limit` (int): 返回信号数量，默认30

**响应**:
```json
{
  "success": true,
  "data": {
    "signals": [
      {
        "id": "signal_001",
        "code": "000001",
        "date": "2024-01-15",
        "indicator": "MACD",
        "signal_type": "BUY",
        "strength": "STRONG_BUY",
        "signal_value": 0.125,
        "confidence": 0.85,
        "description": "MACD金叉信号",
        "params": {
          "fast_ema": 12,
          "slow_ema": 26,
          "signal_ema": 9
        },
        "created_at": "2024-01-15T10:30:00Z"
      }
    ],
    "signal_count": 15,
    "buy_signals": 8,
    "sell_signals": 2
  }
}
```

### 计算组合信号

基于多个指标计算组合信号。

**请求**:
```http
POST /api/signals/combo
Content-Type: application/json

{
  "code": "000001",
  "indicators": ["MACD", "RSI", "KDJ", "BOLL"],
  "weights": {
    "MACD": 1.2,
    "RSI": 1.0,
    "KDJ": 0.8,
    "BOLL": 1.1
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "combo_score": 2.45,
    "recommendation": "BUY",
    "confidence": 0.78,
    "signals": [
      {
        "indicator": "MACD",
        "signal": "BUY",
        "value": 0.12,
        "weight": 1.2
      }
    ],
    "analysis": "多个技术指标同时显示买入信号，建议关注"
  }
}
```

### 信号配置

管理技术信号配置。

**请求**:
```http
GET /api/signals/configs
```

**响应**:
```json
{
  "success": true,
  "data": [
    {
      "id": "config_001",
      "indicator": "MACD",
      "enabled": true,
      "weight": 1.2,
      "params": {
        "fast_period": 12,
        "slow_period": 26,
        "signal_period": 9
      },
      "description": "MACD指标配置",
      "created_at": "2024-01-01T10:00:00Z"
    }
  ]
}
```

## 新闻数据接口

### 获取新闻

获取财经新闻列表。

**请求**:
```http
GET /api/news?category=财经&source=东方财富&limit=20&offset=0
```

**参数**:
- `category` (string): 新闻分类
- `source` (string): 新闻源
- `keyword` (string): 搜索关键词
- `limit` (int): 返回数量，默认20
- `offset` (int): 偏移量，默认0

**响应**:
```json
{
  "success": true,
  "data": {
    "news": [
      {
        "id": "news_001",
        "title": "央行降准0.25个百分点",
        "summary": "央行宣布下调金融机构存款准备金率0.25个百分点",
        "content": "详细新闻内容...",
        "source": "央行官网",
        "author": "财经记者",
        "url": "https://example.com/news/001",
        "category": "政策",
        "tags": ["货币政策", "降准", "流动性"],
        "publish_time": "2024-01-15T10:00:00Z",
        "sentiment": {
          "label": "positive",
          "score": 0.75,
          "confidence": 0.85
        },
        "stock_codes": ["000001", "600036"],
        "relevance": 0.95,
        "created_at": "2024-01-15T10:05:00Z"
      }
    ],
    "total": 1234,
    "categories": ["政策", "市场", "公司", "行业"],
    "sources": ["央行官网", "东方财富", "同花顺"]
  }
}
```

### 新闻详情

获取单条新闻的详细信息。

**请求**:
```http
GET /api/news/{id}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "id": "news_001",
    "title": "央行降准0.25个百分点",
    "content": "完整的新闻内容...",
    "html_content": "<p>HTML格式的新闻内容</p>",
    "related_news": [
      {
        "id": "news_002",
        "title": "降准对市场的影响分析",
        "similarity": 0.85
      }
    ]
  }
}
```

## 投资组合接口

### 获取投资组合

获取用户的投资组合列表。

**请求**:
```http
GET /api/portfolios
```

**响应**:
```json
{
  "success": true,
  "data": [
    {
      "id": "portfolio_001",
      "name": "我的价值股组合",
      "description": "专注于价值股的投资组合",
      "total_value": 1000000,
      "cash_amount": 50000,
      "total_return": 0.15,
      "annualized_return": 0.12,
      "risk_level": "moderate",
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-15T15:30:00Z"
    }
  ]
}
```

### 创建投资组合

创建新的投资组合。

**请求**:
```http
POST /api/portfolios
Content-Type: application/json

{
  "name": "新投资组合",
  "description": "测试投资组合",
  "total_value": 1000000,
  "risk_level": "moderate"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "id": "portfolio_002",
    "name": "新投资组合",
    "created_at": "2024-01-15T16:00:00Z"
  }
}
```

### 获取持仓

获取投资组合的持仓详情。

**请求**:
```http
GET /api/portfolios/{id}/positions
```

**响应**:
```json
{
  "success": true,
  "data": {
    "positions": [
      {
        "id": "position_001",
        "portfolio_id": "portfolio_001",
        "stock_code": "000001",
        "stock_name": "平安银行",
        "quantity": 1000,
        "avg_cost": 15.20,
        "current_price": 15.68,
        "market_value": 15680,
        "unrealized_pnl": 480,
        "unrealized_pct": 0.0316,
        "weight": 0.01568,
        "sector": "金融",
        "industry": "银行",
        "risk_contribution": 0.012,
        "created_at": "2024-01-10T09:30:00Z"
      }
    ],
    "total_positions": 5,
    "total_value": 1000000,
    "total_pnl": 15000
  }
}
```

### 添加持仓

向投资组合添加持仓。

**请求**:
```http
POST /api/portfolios/{id}/positions
Content-Type: application/json

{
  "stock_code": "000001",
  "stock_name": "平安银行",
  "quantity": 1000,
  "price": 15.50,
  "transaction_type": "buy",
  "fee": 7.75,
  "executed_at": "2024-01-15T10:30:00Z"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "position_id": "position_002",
    "message": "持仓添加成功"
  }
}
```

### 获取交易记录

获取投资组合的交易历史。

**请求**:
```http
GET /api/portfolios/{id}/transactions?limit=50&offset=0
```

**响应**:
```json
{
  "success": true,
  "data": {
    "transactions": [
      {
        "id": "transaction_001",
        "portfolio_id": "portfolio_001",
        "stock_code": "000001",
        "transaction_type": "buy",
        "quantity": 1000,
        "price": 15.50,
        "amount": 15500,
        "fee": 7.75,
        "tax": 0,
        "executed_at": "2024-01-15T10:30:00Z",
        "created_at": "2024-01-15T10:30:00Z"
      }
    ],
    "total_transactions": 156,
    "buy_count": 78,
    "sell_count": 78
  }
}
```

## 推送通知接口

### 获取推送设置

获取用户的推送通知设置。

**请求**:
```http
GET /api/notifications/settings
```

**响应**:
```json
{
  "success": true,
  "data": {
    "price_alerts": {
      "enabled": true,
      "threshold_percent": 5.0,
      "targets": ["000001", "600036"]
    },
    "news_notifications": {
      "enabled": true,
      "categories": ["政策", "公司公告"],
      "sources": ["央行官网", "交易所公告"],
      "max_per_day": 20
    },
    "signal_notifications": {
      "enabled": true,
      "indicators": ["MACD", "RSI"],
      "min_strength": "BUY"
    },
    "quiet_hours": {
      "enabled": true,
      "start_time": "22:00",
      "end_time": "08:00"
    }
  }
}
```

### 更新推送设置

更新推送通知设置。

**请求**:
```http
PUT /api/notifications/settings
Content-Type: application/json

{
  "price_alerts": {
    "enabled": true,
    "threshold_percent": 5.0
  }
}
```

**响应**:
```json
{
  "success": true,
  "message": "推送设置更新成功"
}
```

### 发送测试通知

发送测试通知。

**请求**:
```http
POST /api/notifications/test
Content-Type: application/json

{
  "type": "price_alert",
  "title": "价格预警测试",
  "content": "这是测试通知",
  "target_devices": ["device_001"]
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "notification_id": "notification_001",
    "sent_count": 1,
    "failed_count": 0
  }
}
```

## 数据分析接口

### 获取市场指数

获取主要市场指数数据。

**请求**:
```http
GET /api/market/indices
```

**响应**:
```json
{
  "success": true,
  "data": {
    "indices": [
      {
        "code": "sh000001",
        "name": "上证指数",
        "current": 3089.45,
        "change": 37.28,
        "change_percent": 1.22,
        "high": 3100.00,
        "low": 3075.50,
        "volume": 1234567890,
        "amount": 15678901234.56,
        "update_time": "2024-01-15T15:00:00Z"
      }
    ]
  }
}
```

### 获取板块数据

获取行业板块的涨跌情况。

**请求**:
```http
GET /api/market/sectors?sort=change_percent&order=desc&limit=20
```

**响应**:
```json
{
  "success": true,
  "data": {
    "sectors": [
      {
        "code": "BK0476",
        "name": "银行",
        "change_percent": 2.15,
        "leading_stock": "600036",
        "stock_count": 42,
        "avg_pe": 6.5,
        "update_time": "2024-01-15T15:00:00Z"
      }
    ]
  }
}
```

## 错误处理

### 错误码

| 错误码 | 描述 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 未授权访问 |
| 403 | 访问被禁止 |
| 404 | 资源不存在 |
| 429 | 请求频率过高 |
| 500 | 服务器内部错误 |
| 502 | 网关错误 |
| 503 | 服务不可用 |

### 错误响应格式

```json
{
  "success": false,
  "message": "请求参数错误",
  "error": "INVALID_PARAMS",
  "error_code": 400,
  "details": {
    "field": "limit",
    "message": "limit参数必须是正整数"
  },
  "time": "2024-01-15T10:30:00Z"
}
```

## 限制和配额

### API限制

- **请求频率**: 每分钟最多100次请求
- **并发连接**: 每个IP最多10个并发连接
- **数据量限制**: 单次请求最多返回1000条记录
- **查询时间范围**: 历史数据查询范围不超过2年

### 缓存策略

- **实时数据**: 不缓存，每次查询最新数据
- **历史数据**: 缓存5分钟
- **技术指标**: 缓存1分钟
- **新闻数据**: 缓存10分钟

## 认证和安全

### API Key认证

部分接口需要API Key认证：

**请求头**:
```
Authorization: Bearer YOUR_API_KEY
```

**获取API Key**:
```http
POST /api/auth/api-key
Content-Type: application/json

{
  "app_name": "我的应用",
  "description": "应用描述"
}
```

### 请求签名

对敏感接口使用请求签名：

1. 将所有参数按字母顺序排序
2. 拼接成查询字符串
3. 使用API Secret进行HMAC-SHA256签名
4. 将签名添加到请求头中

```http
X-Signature: calculated_signature
X-Timestamp: 1642243200
```

## 示例代码

### JavaScript示例

```javascript
// 获取股票信息
async function getStockInfo(code) {
  try {
    const response = await fetch(`/api/stocks/${code}`);
    const data = await response.json();

    if (data.success) {
      return data.data;
    } else {
      throw new Error(data.message);
    }
  } catch (error) {
    console.error('获取股票信息失败:', error);
    throw error;
  }
}

// 使用示例
getStockInfo('000001')
  .then(stock => {
    console.log('股票信息:', stock);
  })
  .catch(error => {
    console.error('错误:', error);
  });
```

### Python示例

```python
import requests
import json

class StockAPI:
    def __init__(self, base_url='http://localhost:8080/api'):
        self.base_url = base_url
        self.session = requests.Session()

    def get_stock_info(self, code):
        """获取股票信息"""
        url = f'{self.base_url}/stocks/{code}'
        response = self.session.get(url)

        if response.status_code == 200:
            data = response.json()
            if data['success']:
                return data['data']

        raise Exception(f'API错误: {data.get("message", "未知错误")}')

    def get_technical_signals(self, code, indicators=None):
        """获取技术信号"""
        url = f'{self.base_url}/stocks/{code}/signals'
        params = {}
        if indicators:
            params['indicators'] = ','.join(indicators)

        response = self.session.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            if data['success']:
                return data['data']

        raise Exception(f'API错误: {data.get("message", "未知错误")}')

# 使用示例
api = StockAPI()

# 获取股票信息
try:
    stock = api.get_stock_info('000001')
    print(f"股票名称: {stock['name']}")
    print(f"当前价格: {stock['current_price']}")
except Exception as e:
    print(f"错误: {e}")
```

### Go示例

```go
package main

import (
    "encoding/json"
    "fmt"
    "net/http"
    "time"
)

type StockAPI struct {
    BaseURL string
    Client  *http.Client
}

type StockInfo struct {
    Code         string  `json:"code"`
    Name         string  `json:"name"`
    CurrentPrice float64 `json:"current_price"`
    Change       float64 `json:"change"`
    ChangePct    float64 `json:"change_percent"`
}

func NewStockAPI(baseURL string) *StockAPI {
    return &StockAPI{
        BaseURL: baseURL,
        Client:  &http.Client{Timeout: 30 * time.Second},
    }
}

func (api *StockAPI) GetStockInfo(code string) (*StockInfo, error) {
    url := fmt.Sprintf("%s/stocks/%s", api.BaseURL, code)

    resp, err := api.Client.Get(url)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    var result struct {
        Success bool        `json:"success"`
        Data    *StockInfo  `json:"data"`
        Message string       `json:"message"`
    }

    if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
        return nil, err
    }

    if !result.Success {
        return nil, fmt.Errorf("API错误: %s", result.Message)
    }

    return result.Data, nil
}

func main() {
    api := NewStockAPI("http://localhost:8080/api")

    stock, err := api.GetStockInfo("000001")
    if err != nil {
        fmt.Printf("错误: %v\n", err)
        return
    }

    fmt.Printf("股票名称: %s\n", stock.Name)
    fmt.Printf("当前价格: %.2f\n", stock.CurrentPrice)
}
```

## 版本更新

### 版本控制

API使用语义化版本控制：`主版本.次版本.修订版本`

- **主版本**: 不兼容的API变更
- **次版本**: 向后兼容的功能新增
- **修订版本**: 向后兼容的问题修正

### 版本信息

获取当前API版本：

```http
GET /api/version
```

**响应**:
```json
{
  "success": true,
  "data": {
    "version": "1.0.0",
    "build_date": "2024-01-15",
    "git_commit": "abc123def",
    "api_docs": "https://api.smart-stock-insider.com/docs/v1.0.0"
  }
}
```

### 向后兼容性

- 新增字段不会破坏现有功能
- 废弃字段会提前通知并提供迁移指导
- 重大变更会有新版本号和详细的迁移文档

## 开发工具

### Postman集合

提供完整的Postman集合，包含所有API接口的示例：

```json
{
  "info": {
    "name": "智股通API",
    "version": "1.0.0"
  },
  "item": [
    {
      "name": "系统接口",
      "item": [
        {
          "name": "健康检查",
          "request": {
            "url": "{{base_url}}/api/health",
            "method": "GET"
          }
        }
      ]
    }
  ]
}
```

### OpenAPI规范

提供完整的OpenAPI 3.0规范文件，支持：
- 自动生成客户端SDK
- API文档自动生成
- 接口测试工具集成

```yaml
openapi: 3.0.0
info:
  title: 智股通API
  version: 1.0.0
  description: 智能量化投研平台API
servers:
  - url: http://localhost:8080/api
    description: 开发环境
paths:
  /health:
    get:
      summary: 健康检查
      responses:
        '200':
          description: 成功响应
```

## 联系信息

- **API文档**: https://api.smart-stock-insider.com
- **开发者支持**: dev@smart-stock-insider.com
- **问题反馈**: https://github.com/smart-stock-insider/api-issues
- **更新通知**: https://api.smart-stock-insider.com/updates

---

**免责声明**: 本API提供的所有信息仅供参考，不构成投资建议。数据可能存在延迟，使用时请注意风险。