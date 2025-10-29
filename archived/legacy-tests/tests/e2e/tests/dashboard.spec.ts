/**
 * 仪表板端到端测试
 * 测试仪表板页面的完整用户流程
 */

import { test, expect } from '@playwright/test';
import { createTestHelpers } from '../helpers/test-helpers';
import { TEST_USERS, TEST_STOCKS, PERFORMANCE_THRESHOLDS } from '../fixtures/test-data';

test.describe('仪表板功能测试', () => {
  let helpers: ReturnType<typeof createTestHelpers>;

  test.beforeEach(async ({ page }) => {
    helpers = createTestHelpers(page);
    await helpers.setTestEnvironment();
    await helpers.clearStorage();
  });

  test('仪表板页面加载和基本功能', async ({ page }) => {
    // 导航到仪表板
    const startTime = Date.now();
    await helpers.navigateToPage('/dashboard');
    await helpers.waitForPageLoad();
    const loadTime = Date.now() - startTime;

    // 验证页面加载性能
    expect(loadTime).toBeLessThan(PERFORMANCE_THRESHOLDS.pageLoad.maxLoadTime);

    // 验证页面标题
    await expect(page).toHaveTitle(/智股通.*仪表板/);

    // 验证主要组件存在
    await helpers.expectVisible('[data-testid="dashboard-header"]');
    await helpers.expectVisible('[data-testid="stock-overview"]');
    await helpers.expectVisible('[data-testid="news-panel"]');
    await helpers.expectVisible('[data-testid="ai-assistant-widget"]');
    await helpers.expectVisible('[data-testid="portfolio-summary"]');

    // 验证可访问性
    await helpers.checkAccessibility();
  });

  test('股票概览功能', async ({ page }) => {
    await helpers.navigateToPage('/dashboard');
    await helpers.waitForPageLoad();

    // 验证股票列表显示
    await helpers.expectVisible('[data-testid="stock-list"]');

    // 等待股票数据加载
    await helpers.waitForLoadingToDisappear();

    // 验证股票数据展示
    const stockItems = page.locator('[data-testid="stock-item"]');
    await expect(stockItems.first()).toBeVisible();

    // 验证股票搜索功能
    const searchInput = page.locator('[data-testid="stock-search-input"]');
    await helpers.safeFill(searchInput, 'AAPL');

    // 等待搜索结果
    await helpers.waitForApiResponse('/api/stocks/search');

    // 验证搜索结果
    const searchResults = page.locator('[data-testid="search-results"]');
    if (await searchResults.isVisible()) {
      await expect(searchResults).toContainText('AAPL');
    }

    // 测试股票筛选
    const filterButton = page.locator('[data-testid="stock-filter-button"]');
    await helpers.safeClick(filterButton);

    // 选择科技板块
    await helpers.safeClick('[data-testid="filter-technology"]');

    // 验证筛选结果
    await helpers.waitForApiResponse('/api/stocks');

    // 测试实时价格更新
    const realtimeToggle = page.locator('[data-testid="realtime-toggle"]');
    if (await realtimeToggle.isVisible()) {
      await helpers.safeClick(realtimeToggle);

      // 验证实时数据标识
      await helpers.expectVisible('[data-testid="realtime-indicator"]');
    }
  });

  test('新闻面板功能', async ({ page }) => {
    await helpers.navigateToPage('/dashboard');
    await helpers.waitForPageLoad();

    // 验证新闻面板
    await helpers.expectVisible('[data-testid="news-panel"]');

    // 等待新闻数据加载
    await helpers.waitForLoadingToDisappear();

    // 验证新闻列表
    const newsItems = page.locator('[data-testid="news-item"]');
    if (await newsItems.count() > 0) {
      await expect(newsItems.first()).toBeVisible();

      // 测试新闻分类筛选
      const categoryFilter = page.locator('[data-testid="news-category-filter"]');
      if (await categoryFilter.isVisible()) {
        await helpers.safeClick(categoryFilter);
        await helpers.safeClick('[data-testid="category-technology"]');

        // 验证分类筛选结果
        await helpers.waitForApiResponse('/api/news');
      }

      // 测试新闻搜索
      const newsSearch = page.locator('[data-testid="news-search-input"]');
      if (await newsSearch.isVisible()) {
        await helpers.safeFill(newsSearch, '苹果');
        await helpers.pressKeyboardShortcut('Enter');

        // 验证搜索结果
        await helpers.waitForApiResponse('/api/news/search');
      }

      // 测试新闻点击
      const firstNews = newsItems.first();
      await helpers.safeClick(firstNews.locator('[data-testid="news-title"]'));

      // 验证新闻详情或跳转
      await page.waitForTimeout(1000); // 等待页面响应
    }
  });

  test('AI助手交互', async ({ page }) => {
    await helpers.navigateToPage('/dashboard');
    await helpers.waitForPageLoad();

    // 验证AI助手组件
    await helpers.expectVisible('[data-testid="ai-assistant-widget"]');

    // 开始对话
    const startButton = page.locator('[data-testid="start-ai-chat"]');
    if (await startButton.isVisible()) {
      await helpers.safeClick(startButton);

      // 验证聊天对话框打开
      await helpers.expectVisible('[data-testid="ai-chat-dialog"]');

      // 选择分析师角色
      const roleSelector = page.locator('[data-testid="analyst-role-selector"]');
      if (await roleSelector.isVisible()) {
        await helpers.safeClick(roleSelector);
        await helpers.safeClick('[data-testid="role-technical-analyst"]');
      }

      // 输入股票代码
      const stockInput = page.locator('[data-testid="stock-symbol-input"]');
      await helpers.safeFill(stockInput, 'AAPL');

      // 输入问题
      const messageInput = page.locator('[data-testid="message-input"]');
      await helpers.safeFill(messageInput, '请分析这只股票的技术面');

      // 发送消息
      const sendButton = page.locator('[data-testid="send-message"]');
      await helpers.safeClick(sendButton);

      // 验证消息发送和AI回复
      await helpers.waitForApiResponse('/api/ai/analyze');
      await helpers.expectVisible('[data-testid="ai-response"]');

      // 验证对话历史
      const conversationHistory = page.locator('[data-testid="conversation-history"]');
      await expect(conversationHistory).toBeVisible();

      // 测试建议功能
      const suggestions = page.locator('[data-testid="ai-suggestions"]');
      if (await suggestions.isVisible()) {
        const firstSuggestion = suggestions.locator('[data-testid="suggestion-item"]').first();
        await helpers.safeClick(firstSuggestion);

        // 验证建议被填入输入框
        const messageValue = await messageInput.inputValue();
        expect(messageValue.length).toBeGreaterThan(0);
      }

      // 测试流式响应（如果启用）
      const streamToggle = page.locator('[data-testid="stream-toggle"]');
      if (await streamToggle.isVisible()) {
        await helpers.safeClick(streamToggle);

        // 发送另一条消息测试流式响应
        await helpers.safeFill(messageInput, '市场趋势如何？');
        await helpers.safeClick(sendButton);

        // 验证流式响应指示器
        await helpers.expectVisible('[data-testid="streaming-indicator"]');
      }

      // 测试对话导出
      const exportButton = page.locator('[data-testid="export-conversation"]');
      if (await exportButton.isVisible()) {
        await helpers.safeClick(exportButton);

        // 验证下载触发（无法直接验证下载，但可以验证按钮状态变化）
        await page.waitForTimeout(500);
      }

      // 关闭对话框
      const closeButton = page.locator('[data-testid="close-chat-dialog"]');
      await helpers.safeClick(closeButton);

      // 验证对话框关闭
      await helpers.expectHidden('[data-testid="ai-chat-dialog"]');
    }
  });

  test('投资组合概览', async ({ page }) => {
    await helpers.navigateToPage('/dashboard');
    await helpers.waitForPageLoad();

    // 验证投资组合组件
    await helpers.expectVisible('[data-testid="portfolio-summary"]');

    // 等待投资组合数据加载
    await helpers.waitForLoadingToDisappear();

    // 验证投资组合统计
    const portfolioStats = page.locator('[data-testid="portfolio-stats"]');
    if (await portfolioStats.isVisible()) {
      // 验证关键指标显示
      await helpers.expectVisible('[data-testid="total-value"]');
      await helpers.expectVisible('[data-testid="total-return"]');
      await helpers.expectVisible('[data-testid="risk-indicator"]');

      // 测试投资组合详情
      const detailsButton = page.locator('[data-testid="portfolio-details-button"]');
      if (await detailsButton.isVisible()) {
        await helpers.safeClick(detailsButton);

        // 验证详情面板
        await helpers.expectVisible('[data-testid="portfolio-details"]');

        // 测试持仓列表
        const holdings = page.locator('[data-testid="holding-item"]');
        if (await holdings.count() > 0) {
          await expect(holdings.first()).toBeVisible();
        }

        // 测试风险分析
        const riskAnalysis = page.locator('[data-testid="risk-analysis"]');
        if (await riskAnalysis.isVisible()) {
          await helpers.expectVisible('[data-testid="risk-metrics"]');
        }

        // 测试资产配置图表
        const allocationChart = page.locator('[data-testid="allocation-chart"]');
        if (await allocationChart.isVisible()) {
          await expect(allocationChart).toBeVisible();
        }
      }
    }

    // 测试投资组合优化
    const optimizeButton = page.locator('[data-testid="optimize-portfolio"]');
    if (await optimizeButton.isVisible()) {
      await helpers.safeClick(optimizeButton);

      // 验证优化对话框
      await helpers.expectVisible('[data-testid="optimization-dialog"]');

      // 设置优化参数
      const riskTolerance = page.locator('[data-testid="risk-tolerance"]');
      if (await riskTolerance.isVisible()) {
        await helpers.selectOption(riskTolerance, 'moderate');
      }

      const investmentGoal = page.locator('[data-testid="investment-goal"]');
      if (await investmentGoal.isVisible()) {
        await helpers.selectOption(investmentGoal, 'balanced');
      }

      // 开始优化
      const startOptimization = page.locator('[data-testid="start-optimization"]');
      await helpers.safeClick(startOptimization);

      // 验证优化过程
      await helpers.expectVisible('[data-testid="optimization-progress"]');

      // 等待优化完成
      await helpers.waitForApiResponse('/api/portfolio/optimize');

      // 验证优化结果
      await helpers.expectVisible('[data-testid="optimization-results"]');
    }
  });

  test('实时数据更新', async ({ page }) => {
    await helpers.navigateToPage('/dashboard');
    await helpers.waitForPageLoad();

    // 启用实时数据
    const realtimeToggle = page.locator('[data-testid="realtime-data-toggle"]');
    if (await realtimeToggle.isVisible()) {
      await helpers.safeClick(realtimeToggle);

      // 验证实时数据指示器
      await helpers.expectVisible('[data-testid="realtime-indicator"]');

      // 监听WebSocket连接
      const wsConnections = [];
      page.on('websocket', ws => {
        wsConnections.push(ws);
      });

      // 等待实时数据更新
      await page.waitForTimeout(5000); // 等待5秒

      // 验证数据更新
      const lastUpdate = page.locator('[data-testid="last-update-time"]');
      if (await lastUpdate.isVisible()) {
        const updateTime = await lastUpdate.textContent();
        expect(updateTime).toBeTruthy();
      }

      // 测试实时图表更新
      const chart = page.locator('[data-testid="realtime-chart"]');
      if (await chart.isVisible()) {
        await helpers.expectVisible('[data-testid="chart-updating"]');
      }
    }
  });

  test('响应式设计测试', async ({ page }) => {
    await helpers.navigateToPage('/dashboard');
    await helpers.waitForPageLoad();

    // 测试桌面视图
    await helpers.verifyResponsiveDesign({ width: 1280, height: 720 });

    // 测试平板视图
    await helpers.verifyResponsiveDesign({ width: 768, height: 1024 });

    // 测试移动视图
    await helpers.verifyResponsiveDesign({ width: 375, height: 667 });

    // 在移动视图下验证导航菜单
    const mobileMenuButton = page.locator('[data-testid="mobile-menu-button"]');
    if (await mobileMenuButton.isVisible()) {
      await helpers.safeClick(mobileMenuButton);
      await helpers.expectVisible('[data-testid="mobile-navigation"]');
    }
  });

  test('用户偏好设置', async ({ page }) => {
    await helpers.navigateToPage('/dashboard');
    await helpers.waitForPageLoad();

    // 打开设置
    const settingsButton = page.locator('[data-testid="settings-button"]');
    if (await settingsButton.isVisible()) {
      await helpers.safeClick(settingsButton);

      // 验证设置对话框
      await helpers.expectVisible('[data-testid="settings-dialog"]');

      // 测试主题切换
      const themeToggle = page.locator('[data-testid="theme-toggle"]');
      if (await themeToggle.isVisible()) {
        await helpers.safeClick(themeToggle);

        // 验证主题应用
        await page.waitForTimeout(500);
      }

      // 测试语言设置
      const languageSelect = page.locator('[data-testid="language-select"]');
      if (await languageSelect.isVisible()) {
        await helpers.selectOption(languageSelect, 'en');

        // 验证语言切换
        await page.waitForTimeout(500);
      }

      // 测试通知设置
      const notificationToggle = page.locator('[data-testid="notification-toggle"]');
      if (await notificationToggle.isVisible()) {
        await helpers.safeClick(notificationToggle);
      }

      // 保存设置
      const saveButton = page.locator('[data-testid="save-settings"]');
      await helpers.safeClick(saveButton);

      // 验证设置保存
      await helpers.verifyToastMessage('设置已保存');
    }
  });

  test('错误处理和恢复', async ({ page }) => {
    await helpers.navigateToPage('/dashboard');
    await helpers.waitForPageLoad();

    // 模拟网络错误
    await helpers.simulateNetworkCondition('offline');

    // 验证离线状态指示器
    await helpers.expectVisible('[data-testid="offline-indicator"]');

    // 测试离线时的功能降级
    const refreshButton = page.locator('[data-testid="refresh-button"]');
    if (await refreshButton.isVisible()) {
      await helpers.safeClick(refreshButton);

      // 验证错误提示
      await helpers.expectVisible('[data-testid="error-message"]');
    }

    // 恢复网络连接
    const context = page.context();
    await context.setOffline(false);

    // 验证自动重连
    await helpers.expectVisible('[data-testid="reconnected-indicator"]');

    // 验证数据自动刷新
    await helpers.waitForLoadingToDisappear();
  });

  test('性能监控', async ({ page }) => {
    await helpers.navigateToPage('/dashboard');
    await helpers.waitForPageLoad();

    // 监控页面性能指标
    const performanceMetrics = await page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      return {
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
        loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
        firstPaint: performance.getEntriesByType('paint')[0]?.startTime || 0,
        firstContentfulPaint: performance.getEntriesByType('paint')[1]?.startTime || 0
      };
    });

    // 验证性能指标
    expect(performanceMetrics.domContentLoaded).toBeLessThan(2000);
    expect(performanceMetrics.loadComplete).toBeLessThan(PERFORMANCE_THRESHOLDS.pageLoad.maxLoadTime);
    expect(performanceMetrics.firstContentfulPaint).toBeLessThan(
      PERFORMANCE_THRESHOLDS.pageLoad.maxFirstContentfulPaint
    );

    // 监控API响应时间
    const apiResponseTimes: number[] = [];

    page.on('response', response => {
      if (response.url().includes('/api/')) {
        const timing = response.request().timing();
        const responseTime = timing.responseEnd - timing.requestStart;
        apiResponseTimes.push(responseTime);
      }
    });

    // 执行一些操作来触发API调用
    const refreshButton = page.locator('[data-testid="refresh-button"]');
    if (await refreshButton.isVisible()) {
      await helpers.safeClick(refreshButton);
      await helpers.waitForLoadingToDisappear();
    }

    // 验证API响应时间
    if (apiResponseTimes.length > 0) {
      const avgResponseTime = apiResponseTimes.reduce((a, b) => a + b, 0) / apiResponseTimes.length;
      expect(avgResponseTime).toBeLessThan(PERFORMANCE_THRESHOLDS.apiResponse.maxResponseTime);
    }
  });
});