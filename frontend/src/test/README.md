# 前端测试指南

本文档描述了智股通前端应用的测试框架、测试策略和最佳实践。

## 目录

- [测试框架](#测试框架)
- [测试结构](#测试结构)
- [测试类型](#测试类型)
- [运行测试](#运行测试)
- [编写测试](#编写测试)
- [Mock策略](#mock策略)
- [覆盖率](#覆盖率)
- [最佳实践](#最佳实践)

## 测试框架

我们使用以下测试技术栈：

- **Vitest**: 测试运行器和框架
- **React Testing Library**: React组件测试
- **MSW**: API模拟
- **jsdom**: 测试环境
- **Vitest Coverage**: 代码覆盖率报告

## 测试结构

```
src/test/
├── setup.ts              # 测试环境设置
├── utils.tsx              # 测试工具函数
├── data/                  # 测试数据
│   └── index.ts           # 模拟数据生成器
├── mocks/                 # Mock对象
│   └── server.ts          # API Mock服务器
├── components/            # 组件测试
│   ├── Stock/             # 股票相关组件测试
│   ├── AI/                # AI分析组件测试
│   ├── News/              # 新闻组件测试
│   └── Charts/            # 图表组件测试
├── integration/           # 集成测试
├── e2e/                   # 端到端测试
├── performance/           # 性能测试
└── fixtures/              # 测试夹具
```

## 测试类型

### 1. 单元测试

测试单个函数、组件或模块的功能。

```typescript
import { describe, it, expect } from 'vitest'
import { render, screen } from '@/test/utils'
import MyComponent from '@/components/MyComponent'

describe('MyComponent', () => {
  it('应该正确渲染', () => {
    render(<MyComponent />)
    expect(screen.getByText('Hello World')).toBeInTheDocument()
  })
})
```

### 2. 组件测试

测试React组件的渲染、交互和状态管理。

```typescript
import { userEvent } from '@testing-library/user-event'
import { render } from '@/test/utils'

describe('Component Tests', () => {
  it('应该处理用户交互', async () => {
    const user = userEvent.setup()
    render(<MyComponent />)

    await user.click(screen.getByRole('button'))
    expect(screen.getByText('Clicked')).toBeInTheDocument()
  })
})
```

### 3. 集成测试

测试多个组件或模块之间的交互。

```typescript
describe('Integration Tests', () => {
  it('应该正确处理API调用和数据流', async () => {
    // 测试组件间的数据传递和API交互
  })
})
```

## 运行测试

### 基本命令

```bash
# 运行所有测试
npm test

# 监视模式运行测试
npm run test:watch

# 运行测试并生成覆盖率报告
npm run test:coverage

# 运行特定组件测试
npm run test:component

# 运行单元测试
npm run test:unit

# CI环境运行测试
npm run test:ci
```

### 使用脚本

```bash
# Unix/Linux/macOS
./scripts/run-tests.sh --mode unit --coverage

# Windows
scripts\run-tests.bat -m unit -c
```

### 脚本选项

- `-c, --coverage`: 生成覆盖率报告
- `-w, --watch`: 监视模式
- `-m, --mode MODE`: 测试模式 (unit, integration, e2e, all)
- `-r, --reporter R`: 报告格式 (verbose, dot, json, junit)
- `--component NAME`: 运行特定组件测试
- `-h, --help`: 显示帮助信息

## 编写测试

### 测试文件命名

- 组件测试: `ComponentName.test.tsx`
- 工具函数测试: `utility.test.ts`
- 集成测试: `feature.integration.test.ts`

### 测试结构

```typescript
describe('测试主题', () => {
  beforeEach(() => {
    // 每个测试前的设置
  })

  afterEach(() => {
    // 每个测试后的清理
  })

  it('应该执行某个行为', () => {
    // 测试实现
  })

  it('应该处理边界情况', () => {
    // 边界情况测试
  })
})
```

### 测试工具

```typescript
import { render, screen, waitFor } from '@/test/utils'
import { validateStockData } from '@/test/data'

// 渲染组件
const { getByTestId } = render(<MyComponent />)

// 等待异步操作
await waitFor(() => {
  expect(getByTestId('result')).toBeInTheDocument()
})

// 验证数据
validateStockData(mockStockData)
```

## Mock策略

### API Mock

使用MSW模拟API请求：

```typescript
import { server } from '@/test/mocks/server'

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
```

### 组件Mock

```typescript
// Mock外部依赖
vi.mock('@/services/api', () => ({
  api: {
    get: vi.fn().mockResolvedValue({ data: [] })
  }
}))

// Mock子组件
vi.mock('@/components/ChildComponent', () => ({
  default: () => <div>Mock Child</div>
}))
```

### Hook Mock

```typescript
// Mock React Query
vi.mock('@tanstack/react-query', () => ({
  useQuery: vi.fn().mockReturnValue({
    data: mockData,
    isLoading: false,
    error: null
  })
}))
```

## 覆盖率

### 覆盖率目标

- 整体代码覆盖率: ≥ 70%
- 分支覆盖率: ≥ 70%
- 函数覆盖率: ≥ 70%
- 行覆盖率: ≥ 70%

### 生成报告

```bash
# 生成HTML覆盖率报告
npm run test:coverage

# 查看覆盖率报告
open coverage/index.html
```

### 覆盖率配置

```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        'dist/'
      ],
      thresholds: {
        global: {
          branches: 70,
          functions: 70,
          lines: 70,
          statements: 70
        }
      }
    }
  }
})
```

## 最佳实践

### 1. 测试原则

- **单一职责**: 每个测试只验证一个功能点
- **独立性**: 测试之间不应相互依赖
- **可重复性**: 测试结果应该一致且可重复
- **可读性**: 测试代码应该清晰易懂

### 2. 测试命名

```typescript
// 好的命名
it('应该在用户点击按钮时显示加载状态')
it('应该在网络错误时显示错误消息')

// 避免的命名
it('测试按钮点击')
it('测试组件')
```

### 3. 断言策略

- 专注于用户可见的行为
- 避免测试实现细节
- 使用有意义的断言消息

```typescript
// 好的断言
expect(screen.getByRole('button', { name: '提交' })).toBeDisabled()

// 避免的断言
expect(component.state('isLoading')).toBe(true)
```

### 4. 异步测试

```typescript
// 使用waitFor等待异步操作
await waitFor(() => {
  expect(screen.getByText('数据加载完成')).toBeInTheDocument()
})

// 使用userEvent模拟用户操作
await user.click(screen.getByRole('button'))
```

### 5. 测试数据

- 使用工厂函数生成测试数据
- 保持测试数据的一致性和可重用性
- 避免在测试中使用硬编码数据

```typescript
const createMockStock = (overrides = {}) => ({
  id: 1,
  symbol: 'AAPL',
  name: 'Apple Inc.',
  price: 150.0,
  ...overrides
})
```

### 6. 错误处理测试

```typescript
it('应该正确处理API错误', async () => {
  mockApi.get.mockRejectedValue(new Error('Network error'))

  render(<MyComponent />)

  await waitFor(() => {
    expect(screen.getByText('加载失败')).toBeInTheDocument()
  })
})
```

### 7. 性能测试

```typescript
it('应该在大量数据下保持性能', () => {
  const largeData = Array.from({ length: 10000 }, (_, i) => createMockItem(i))

  const startTime = performance.now()
  render(<MyComponent data={largeData} />)
  const endTime = performance.now()

  expect(endTime - startTime).toBeLessThan(1000) // 1秒内完成渲染
})
```

## 调试测试

### 1. 使用screen.debug()

```typescript
render(<MyComponent />)
screen.debug() // 打印当前DOM结构
```

### 2. 使用logRoles

```typescript
import { logRoles } from '@testing-library/dom'

const { container } = render(<MyComponent />)
logRoles(container) // 打印可访问的角色
```

### 3. 使用only和skip

```typescript
// 只运行特定测试
it.only('只运行这个测试', () => {
  // 测试代码
})

// 跳过测试
it.skip('跳过这个测试', () => {
  // 测试代码
})
```

## 持续集成

在CI/CD流水线中运行测试：

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run test:ci
```

## 故障排除

### 常见问题

1. **测试超时**: 增加超时时间或检查异步操作
2. **Mock失败**: 确保Mock正确设置和清理
3. **DOM更新**: 使用waitFor等待DOM更新
4. **覆盖率不足**: 检查未覆盖的代码路径

### 调试技巧

- 使用`console.log`或`screen.debug()`输出状态
- 检查Mock函数的调用历史
- 验证测试环境配置

## 参考资料

- [Vitest文档](https://vitest.dev/)
- [React Testing Library文档](https://testing-library.com/docs/react-testing-library/intro/)
- [MSW文档](https://mswjs.io/)
- [测试最佳实践](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)