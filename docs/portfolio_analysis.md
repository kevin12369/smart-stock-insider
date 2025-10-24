# 投资组合分析功能文档

## 概述

智股通投资组合分析功能为用户提供全面的组合管理、业绩评估、风险分析和资产配置优化服务。支持多维度分析、实时监控和智能建议。

## 核心功能

### 1. 投资组合管理

#### 创建投资组合
- **功能**: 创建新的投资组合
- **参数**: 组合名称、描述、初始资金、风险等级
- **支持**: 多币种、自定义基准

#### 持仓管理
- **实时持仓**: 维护当前股票持仓
- **成本追踪**: 记录买入成本、当前价格
- **盈亏计算**: 自动计算未实现盈亏
- **持仓统计**: 持有天数、权重、风险贡献度

#### 交易记录
- **完整交易历史**: 买入、卖出、分红、拆股
- **成本精确计算**: 包含手续费、税费
- **交易分析**: 交易频率、平均成本、胜率统计

### 2. 业绩分析

#### 收益率计算
- **多时间维度**: 日、周、月、年初至今
- **年化收益**: 基于时间长度计算
- **相对收益**: 相对基准指数的表现
- **Alpha/Beta**: 系统性风险和超额收益分析

#### 风险调整收益
- **夏普比率**: 风险调整后收益
- **索提诺比率**: 下行风险调整收益
- **卡玛比率**: 最大回撤调整收益
- **信息比率**: 相对基准的信息比率

#### 回测表现
- **历史回测**: 基于历史数据的业绩回测
- **不同市场周期**: 牛市、熊市、震荡市表现
- **风险指标**: 最大回撤、波动率、VaR计算

### 3. 风险分析

#### 风险度量
- **整体风险等级**: 低、中、高、极高
- **系统性风险**: Beta值、市场相关性
- **非系统性风险**: 个股特有风险
- **集中度风险**: HHI指数、分散化评分

#### 风险分解
- **行业风险**: 各行业风险暴露
- **风格风险**: 成长、价值、规模等风格因子
- **地区风险**: 不同地区市场风险
- **货币风险**: 汇率风险暴露

#### 情景分析
- **压力测试**: 极端市场情况下的表现
- **敏感性分析**: 市场因子变动影响
- **在险价值**: 不同置信区间的VaR
- **黑天鹅事件**: 极端尾部风险

### 4. 资产配置分析

#### 配置分析
- **行业配置**: 各行业资金分配比例
- **市值配置**: 大、中、小盘股配置
- **地域配置**: 不同市场地区配置
- **资产类别**: 股票、债券、现金等配置

#### 集中度分析
- **持仓集中度**: 前十大持仓占比
- **行业集中度**: 行业分散化程度
- **分散化评分**: 0-1分散化程度评分
- **风险集中度**: 各持仓风险贡献度

#### 再平衡建议
- **目标配置**: 基于现代投资组合理论
- **再平衡信号**: 偏离阈值触发
- **具体操作**: 买入、卖出、调整建议
- **执行优先级**: 高、中、低优先级排序

### 5. 智能建议系统

#### 业绩建议
- **持仓优化**: 基于业绩表现的调整建议
- **止损建议**: 基于风险水平的止损建议
- **获利了结**: 基于收益的卖出建议

#### 风险建议
- **分散化建议**: 降低集中度风险
- **对冲建议**: 基于风险暴露的对冲操作
- **仓位调整**: 基于市场环境的仓位建议

#### 再平衡建议
- **定期再平衡**: 基于时间周期的自动建议
- **阈值再平衡**: 基于偏离度的触发建议
- **目标调整**: 基于市场环境的目标配置调整

## API接口

### 投资组合管理

#### 获取投资组合
```go
result := app.GetPortfolio(portfolioID)
```

**参数**:
- `portfolioID`: 投资组合ID

**返回**:
```json
{
  "success": true,
  "data": {
    "id": "portfolio_001",
    "name": "我的组合",
    "total_value": 1000000,
    "cash_amount": 50000,
    "holdings": [...],
    "statistics": {...},
    "performance": {...},
    "allocation": {...}
  }
}
```

#### 创建投资组合
```go
result := app.CreatePortfolio({
  "id": "portfolio_002",
  "user_id": "user_001",
  "name": "新组合",
  "description": "长期价值投资组合",
  "total_value": 500000,
  "cash_amount": 200000,
  "currency": "CNY",
  "risk_level": "moderate"
})
```

#### 添加持仓
```go
result := app.AddPosition({
  "portfolio_id": "portfolio_001",
  "stock_code": "000001",
  "stock_name": "平安银行",
  "quantity": 1000,
  "avg_cost": 15.50,
  "current_price": 16.80,
  "market_value": 16800,
  "sector": "金融",
  "industry": "银行"
})
```

#### 更新持仓
```go
result := app.UpdatePosition({
  "id": "position_001",
  "portfolio_id": "portfolio_001",
  "current_price": 16.90,
  "market_value": 16900
})
```

#### 移除持仓
```go
result := app.RemovePosition("position_001")
```

### 投资组合分析

#### 综合分析
```go
result := app.AnalyzePortfolio({
  "portfolio_id": "portfolio_001",
  "user_id": "user_001",
  "analysis_type": "comprehensive",
  "benchmark_code": "000300",
  "include_inactive": true,
  "parameters": {
    "risk_free_rate": 0.03,
    "confidence_level": 0.95
  }
})
```

**分析类型**:
- `performance`: 业绩分析
- `risk`: 风险分析
- `allocation`: 配置分析
- `rebalancing`: 再平衡分析
- `comprehensive`: 综合分析

**返回**:
```json
{
  "success": true,
  "data": {
    "portfolio_id": "portfolio_001",
    "analysis_type": "comprehensive",
    "performance": {
      "total_return": 0.15,
      "annualized_return": 0.12,
      "sharpe_ratio": 1.2,
      "max_drawdown": 0.08
    },
    "risk_analysis": {
      "overall_risk_level": "medium",
      "volatility": 0.18,
      "beta": 1.1,
      "var_95": 0.05
    },
    "allocation": {
      "by_sector": {
        "科技": 0.35,
        "金融": 0.25,
        "消费": 0.20,
        "医药": 0.20
      },
      "concentration": {
        "diversification_score": 0.75,
        "top_positions": [...]
      },
      "rebalancing": {
        "rebalancing_needed": true,
        "recommended_actions": [...]
      }
    },
    "recommendations": [...]
  }
}
```

### 持仓管理

#### 获取持仓列表
```go
result := app.GetPortfolioHoldings("portfolio_001")
```

## 数据模型

### 核心模型

#### Portfolio (投资组合)
```json
{
  "id": "portfolio_001",
  "user_id": "user_001",
  "name": "智股通组合",
  "description": "精选价值股组合",
  "total_value": 1000000,
  "cash_amount": 50000,
  "currency": "CNY",
  "risk_level": "moderate",
  "holdings": [...],
  "statistics": {
    "total_positions": 8,
    "profitable_positions": 5,
    "win_rate": 0.625,
    "avg_holding_days": 45
  },
  "performance": {
    "total_return": 0.15,
    "sharpe_ratio": 1.2,
    "max_drawdown": 0.08
  },
  "allocation": {
    "by_sector": {...},
    "concentration": {...},
    "rebalancing": {...}
  }
}
```

#### Position (持仓)
```json
{
  "id": "position_001",
  "portfolio_id": "portfolio_001",
  "stock_code": "000001",
  "stock_name": "平安银行",
  "quantity": 1000,
  "avg_cost": 15.50,
  "current_price": 16.80,
  "market_value": 16800,
  "unrealized_pnl": 1300,
  "unrealized_pct": 0.084,
  "weight": 0.0168,
  "risk_contribution": 0.012,
  "holding_days": 30,
  "sector": "金融",
  "industry": "银行",
  "market_cap": "large",
  "pe": 6.8,
  "pb": 0.85,
  "dividend_yield": 0.045
}
```

#### Transaction (交易)
```json
{
  "id": "transaction_001",
  "portfolio_id": "portfolio_001",
  "position_id": "position_001",
  "stock_code": "000001",
  "transaction_type": "buy",
  "quantity": 1000,
  "price": 15.50,
  "amount": 15500,
  "fee": 7.75,
  "tax": 0,
  "executed_at": "2024-01-15T09:30:00Z"
}
```

## 技术实现

### 数据库设计

#### 主要表结构
- **portfolios**: 投资组合基础信息
- **positions**: 持仓详情
- **transactions**: 交易记录
- **portfolio_analysis_cache**: 分析结果缓存
- **portfolio_alerts**: 投资组合预警
- **portfolio_config**: 配置信息
- **portfolio_snapshots**: 投资组合快照

#### 索引优化
- 复合索引: (portfolio_id, stock_code)
- 时间索引: executed_at, created_at
- 分析缓存索引: (portfolio_id, analysis_type)

### 计算逻辑

#### 收益率计算
```go
// 简单收益率
return = (current_value - initial_value) / initial_value

// 年化收益率
annualized_return = math.Pow(1 + return, 365/days) - 1

// 夏普比率
sharpe = (annualized_return - risk_free_rate) / volatility
```

#### 风险指标计算
```go
// Beta计算
beta = covariance(portfolio_returns, market_returns) / variance(market_returns)

// 最大回撤
max_drawdown = max((peak - trough) / peak)

// VaR计算 (历史模拟法)
var_95 = percentile(returns, 0.05)
```

### 缓存策略
- **分析结果缓存**: 15分钟有效期
- **快照数据**: 每日更新
- **配置缓存**: 配置变更时清除
- **智能失效**: 数据更新时自动清除

## 使用场景

### 1. 个人投资管理
- 创建多个不同策略的投资组合
- 实时监控投资组合表现
- 定期分析风险和收益

### 2. 投资顾问服务
- 为客户提供专业投资组合分析
- 生成个性化投资建议
- 风险管理和资产配置

### 3. 机构投资分析
- 大规模组合风险管理
- 业绩归因分析
- 合规性检查

### 4. 智能投顾
- 基于AI的投资建议
- 自动再平衡提醒
- 风险预警系统

## 性能优化

### 1. 计算优化
- 增量计算: 只重新计算变化部分
- 并行处理: 多指标并行计算
- 缓存策略: 智能缓存计算结果

### 2. 数据库优化
- 分区表: 按时间分区存储历史数据
- 索引策略: 覆盖常用查询场景
- 批量操作: 减少数据库交互次数

### 3. 内存优化
- 数据结构优化: 使用高效数据结构
- 垃圾回收: 及时释放不用的数据
- 连接池: 数据库连接复用

## 安全考虑

### 1. 数据安全
- 敏感数据加密存储
- 用户数据隔离
- 访问权限控制

### 2. 计算安全
- 输入验证: 严格参数验证
- 防注入攻击: SQL注入防护
- 内存安全: 防止内存溢出

### 3. 业务安全
- 异常检测: 异常交易行为监控
- 风险控制: 投资风险限制
- 审计日志: 操作记录和追踪

## 扩展规划

### 短期扩展
- 更多分析指标: Calmar比率、特雷诺比率
- 国际市场支持: 港股、美股
- 高级图表: 收益曲线、回撤分析图

### 中期扩展
- 机器学习优化: 基于历史数据的模型优化
- 因子投资: Fama-French多因子模型
- 组合优化: 有效前沿计算

### 长期扩展
- ESG投资: 环境、社会、治理因素整合
- 量子计算: 量子投资组合优化算法
- 跨资产配置: 大类资产配置模型

---

*最后更新: 2024年1月*