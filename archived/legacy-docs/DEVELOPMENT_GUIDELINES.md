# 开发规范指南

## Git 工作流

### 分支策略

我们采用 **Git Flow** 工作流，主要分支包括：

- **main**: 主分支，只包含稳定的发布版本
- **develop**: 开发分支，集成最新的功能代码
- **feature/***: 功能分支，用于开发新功能
- **hotfix/***: 热修复分支，用于紧急修复生产环境问题
- **release/***: 发布分支，用于准备发布版本

### 分支命名规范

```bash
# 功能分支
feature/股票数据看板
feature/AI分析师集成
feature/新闻聚合系统

# 修复分支
fix/股票显示异常
fix/AI接口调用错误

# 热修复分支
hotfix/紧急修复数据泄露
hotfix/修复生产环境崩溃

# 发布分支
release/v1.0.0
release/v1.1.0-beta
```

### 提交信息规范

采用 **Conventional Commits** 规范：

```
<类型>[可选的作用域]: <描述>

[可选的正文]

[可选的脚注]
```

#### 提交类型

- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整（不影响功能）
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动
- `perf`: 性能优化
- `ci`: CI/CD相关
- `build`: 构建系统或外部依赖

#### 示例

```bash
feat(数据看板): 添加股票实时价格显示功能

- 实现WebSocket连接获取实时数据
- 添加价格变动动画效果
- 支持多个股票同时监控

Closes #123
```

```bash
fix(AI分析): 修复GLM API调用超时问题

增加请求超时设置和重试机制，提高API调用的稳定性。
```

### 代码审查流程

1. 创建Pull Request
2. 至少需要一人代码审查
3. 通过所有自动化测试
4. 解决审查意见
5. 合并到目标分支

## 代码规范

### TypeScript/JavaScript

#### 命名规范

```typescript
// 变量和函数：camelCase
const userName = 'john';
const getUserInfo = () => {};

// 常量：UPPER_SNAKE_CASE
const API_BASE_URL = 'https://api.example.com';
const MAX_RETRY_COUNT = 3;

// 类和接口：PascalCase
class UserService {}
interface ApiResponse {}

// 类型别名：PascalCase
type StockData = {
  symbol: string;
  price: number;
};

// 枚举：PascalCase
enum UserRole {
  Admin = 'admin',
  User = 'user',
}
```

#### 文件命名

```typescript
// 组件文件：PascalCase
UserProfile.tsx
StockChart.tsx

// 工具文件：camelCase
apiClient.ts
dateUtils.ts

// 类型文件：camelCase
types.ts
interfaces.ts

// 常量文件：camelCase
constants.ts
config.ts
```

#### 组件规范

```typescript
// 函数组件示例
interface StockChartProps {
  data: StockData[];
  height?: number;
  onSymbolClick?: (symbol: string) => void;
}

const StockChart: React.FC<StockChartProps> = ({
  data,
  height = 400,
  onSymbolClick,
}) => {
  // 组件实现
  return (
    <div className="stock-chart" style={{ height }}>
      {/* 图表内容 */}
    </div>
  );
};

export default StockChart;
```

### Python

#### 命名规范

```python
# 变量和函数：snake_case
user_name = 'john'
def get_user_info():
    pass

# 常量：UPPER_SNAKE_CASE
API_BASE_URL = 'https://api.example.com'
MAX_RETRY_COUNT = 3

# 类：PascalCase
class UserService:
    pass

# 私有变量：前缀下划线
class MyClass:
    def __init__(self):
        self._private_var = 'private'
        self.__very_private = 'very private'
```

#### 文档字符串

```python
def get_stock_price(symbol: str, date: Optional[str] = None) -> Dict[str, Any]:
    """
    获取股票价格信息

    Args:
        symbol: 股票代码，如 '000001.SZ'
        date: 查询日期，格式为 'YYYY-MM-DD'，默认为当前日期

    Returns:
        包含价格信息的字典，包含以下字段：
        - open: 开盘价
        - close: 收盘价
        - high: 最高价
        - low: 最低价
        - volume: 成交量

    Raises:
        ValueError: 当股票代码格式不正确时
        APITimeout: 当API调用超时时

    Example:
        >>> get_stock_price('000001.SZ')
        {'open': 10.5, 'close': 11.0, 'high': 11.2, 'low': 10.3, 'volume': 1000000}
    """
    pass
```

### SQL

#### 命名规范

```sql
-- 表名：snake_case，复数形式
CREATE TABLE stock_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引名：idx_表名_列名
CREATE INDEX idx_stock_prices_symbol ON stock_prices(symbol);
CREATE INDEX idx_stock_prices_created_at ON stock_prices(created_at);

-- 外键名：fk_表名_列名
ALTER TABLE stock_prices
ADD CONSTRAINT fk_stock_prices_symbol
FOREIGN KEY (symbol) REFERENCES stocks(symbol);
```

## 测试规范

### 前端测试

```typescript
// 单元测试示例
import { render, screen, fireEvent } from '@testing-library/react';
import { StockChart } from './StockChart';

describe('StockChart', () => {
  const mockData = [
    { symbol: 'AAPL', price: 150, change: 2.5 },
    { symbol: 'GOOGL', price: 2500, change: -1.2 },
  ];

  it('renders stock data correctly', () => {
    render(<StockChart data={mockData} />);

    expect(screen.getByText('AAPL')).toBeInTheDocument();
    expect(screen.getByText('$150')).toBeInTheDocument();
  });

  it('calls onSymbolClick when symbol is clicked', () => {
    const handleClick = jest.fn();
    render(<StockChart data={mockData} onSymbolClick={handleClick} />);

    fireEvent.click(screen.getByText('AAPL'));
    expect(handleClick).toHaveBeenCalledWith('AAPL');
  });
});
```

### 后端测试

```python
# 单元测试示例
import pytest
from unittest.mock import Mock, patch
from services.stock_service import StockService

class TestStockService:
    def setup_method(self):
        self.service = StockService()

    @pytest.mark.asyncio
    async def test_get_stock_price_success(self):
        # Arrange
        symbol = "000001.SZ"
        expected_price = 10.5

        # Act
        result = await self.service.get_current_price(symbol)

        # Assert
        assert result["symbol"] == symbol
        assert result["price"] == expected_price

    @pytest.mark.asyncio
    async def test_get_stock_price_invalid_symbol(self):
        # Arrange
        symbol = "INVALID"

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid stock symbol"):
            await self.service.get_current_price(symbol)

# 集成测试示例
@pytest.mark.integration
class TestStockAPI:
    async def test_get_stock_list_endpoint(self, client):
        response = await client.get("/api/stocks/list")
        assert response.status_code == 200
        assert "data" in response.json()
```

## 性能优化规范

### 前端性能

1. **组件懒加载**
```typescript
const StockChart = lazy(() => import('./components/StockChart'));
```

2. **代码分割**
```typescript
// 路由级别的代码分割
const Dashboard = lazy(() => import('./pages/Dashboard'));
const StockAnalysis = lazy(() => import('./pages/StockAnalysis'));
```

3. **使用 React.memo 优化组件**
```typescript
const StockListItem = React.memo(({ stock }: { stock: Stock }) => {
  return <div>{stock.name}</div>;
});
```

### 后端性能

1. **数据库查询优化**
```python
# 使用索引
query = select(Stock).where(Stock.symbol == symbol).limit(100)

# 批量操作
bulk_insert(stocks, stock_data_list)

# 连接池配置
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_timeout=30
)
```

2. **缓存策略**
```python
# Redis缓存
@cache_result(ttl=300)  # 5分钟缓存
async def get_stock_price(symbol: str):
    pass

# 内存缓存
from functools import lru_cache

@lru_cache(maxsize=1000)
def calculate_technical_indicators(data: List[float]):
    pass
```

## 安全规范

### 前端安全

1. **XSS防护**
```typescript
// 使用DOMPurify清理HTML
import DOMPurify from 'dompurify';

const cleanHtml = DOMPurify.sanitize(userInput);
```

2. **API密钥保护**
```typescript
// 不要在前端代码中硬编码API密钥
// 使用环境变量
const API_KEY = import.meta.env.VITE_API_KEY;
```

### 后端安全

1. **SQL注入防护**
```python
# 使用参数化查询
query = text("SELECT * FROM stocks WHERE symbol = :symbol")
result = await db.execute(query, {"symbol": symbol})
```

2. **输入验证**
```python
from pydantic import BaseModel, validator

class StockQuery(BaseModel):
    symbol: str

    @validator('symbol')
    def validate_symbol(cls, v):
        if not re.match(r'^\d{6}\.(SH|SZ)$', v):
            raise ValueError('Invalid stock symbol format')
        return v
```

## 文档规范

### README.md

每个项目都应该有详细的README.md，包含：
- 项目介绍
- 安装说明
- 使用方法
- API文档链接
- 贡献指南

### API文档

使用OpenAPI/Swagger自动生成API文档：

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="智股通API",
    description="基于AI的桌面投资研究平台API",
    version="1.0.0"
)

@app.get(
    "/stocks/{symbol}",
    response_model=StockResponse,
    summary="获取股票信息",
    description="根据股票代码获取详细的股票信息",
    tags=["stocks"]
)
async def get_stock(symbol: str):
    """获取股票信息

    - **symbol**: 股票代码
    """
    pass
```

### 代码注释

1. **复杂逻辑注释**
```python
def calculate_rsi(prices: List[float], period: int = 14) -> List[float]:
    """
    计算相对强弱指标(RSI)

    RSI是一种技术分析指标，用于识别价格变动的速度和变化。
    计算公式：RSI = 100 - (100 / (1 + RS))
    其中RS = 平均上涨幅度 / 平均下跌幅度
    """
    # 实现细节...
```

2. **TODO/FIXME注释**
```typescript
// TODO: 添加错误处理和重试机制
// FIXME: 这里存在性能问题，需要优化查询逻辑
// HACK: 临时解决方案，待重构
```

## 发布流程

### 版本号规范

采用语义化版本号：`主版本.次版本.修订版本`

- **主版本**：不兼容的API修改
- **次版本**：向下兼容的功能性新增
- **修订版本**：向下兼容的问题修正

### 发布检查清单

- [ ] 所有测试通过
- [ ] 代码审查完成
- [ ] 文档更新
- [ ] 版本号更新
- [ ] 变更日志更新
- [ ] 安全扫描通过
- [ ] 性能测试通过
- [ ] 发布说明准备

---

**文档版本**: v1.0
**创建时间**: 2025-10-28
**更新时间**: 2025-10-28
**负责人**: Smart Stock Insider Team