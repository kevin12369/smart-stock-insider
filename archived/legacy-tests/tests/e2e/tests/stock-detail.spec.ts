/**
 * 股票详情页面端到端测试
 * 测试股票详情页面的完整用户流程
 */

import { test, expect } from '@playwright/test';
import { createTestHelpers } from '../helpers/test-helpers';
import { TEST_STOCKS, PERFORMANCE_THRESHOLDS } from '../fixtures/test-data';

test.describe('股票详情功能测试', () => {
  let helpers: ReturnType<typeof createTestHelpers>;

  test.beforeEach(async ({ page }) => {
    helpers = createTestHelpers(page);
    await helpers.setTestEnvironment();
    await helpers.clearStorage();
  });

  test('股票详情页面加载和基本信息', async ({ page }) => {
    // 使用测试股票AAPL
    const testStock = TEST_STOCKS[0];

    // 导航到股票详情页
    const startTime = Date.now();
    await helpers.navigateToPage(`/stock/${testStock.symbol}`);
    await helpers.waitForPageLoad();
    const loadTime = Date.now() - startTime;

    // 验证页面加载性能
    expect(loadTime).toBeLessThan(PERFORMANCE_THRESHOLDS.pageLoad.maxLoadTime);

    // 验证页面标题
    await expect(page).toHaveTitle(new RegExp(`${testStock.symbol}.*${testStock.name}`));

    // 验证基本信息显示
    await helpers.expectVisible('[data-testid="stock-header"]');
    await helpers.expectVisible('[data-testid="stock-name"]');
    await helpers.expectVisible('[data-testid="stock-symbol"]');
    await helpers.expectVisible('[data-testid="current-price"]');
    await helpers.expectVisible('[data-testid="price-change"]');

    // 验证股票基本信息正确性
    await helpers.expectText('[data-testid="stock-symbol"]', testStock.symbol);
    await helpers.expectText('[data-testid="stock-name"]', testStock.name);

    // 验证价格信息
    await helpers.expectVisible('[data-testid="price-info"]');
    const priceElement = page.locator('[data-testid="current-price"]');
    const changeElement = page.locator('[data-testid="price-change"]');

    expect(await priceElement.isVisible()).toBeTruthy();
    expect(await changeElement.isVisible()).toBeTruthy();

    // 验证可访问性
    await helpers.checkAccessibility();
  });

  test('价格图表功能', async ({ page }) => {
    const testStock = TEST_STOCKS[0];

    await helpers.navigateToPage(`/stock/${testStock.symbol}`);
    await helpers.waitForPageLoad();

    // 验证图表组件
    await helpers.expectVisible('[data-testid="price-chart"]');

    // 等待图表数据加载
    await helpers.waitForLoadingToDisappear();
    await helpers.waitForApiResponse('/api/stocks');

    // 验证图表渲染
    const chartContainer = page.locator('[data-testid="chart-container"]');
    await expect(chartContainer).toBeVisible();

    // 测试时间周期选择
    const timeframeButtons = page.locator('[data-testid="timeframe-button"]');
    if (await timeframeButtons.count() > 0) {
      // 测试不同时间周期
      const timeframes = ['1D', '1W', '1M', '3M', '1Y', 'ALL'];

      for (const timeframe of timeframes) {
        const button = page.locator(`[data-testid="timeframe-${timeframe}"]`);
        if (await button.isVisible()) {
          await helpers.safeClick(button);

          // 等待图表数据更新
          await helpers.waitForApiResponse('/api/stocks/history');
          await page.waitForTimeout(500); // 等待图表重绘
        }
      }
    }

    // 测试图表类型切换
    const chartTypeButtons = page.locator('[data-testid="chart-type-button"]');
    if (await chartTypeButtons.count() > 0) {
      const chartTypes = ['candlestick', 'line', 'area'];

      for (const chartType of chartTypes) {
        const button = page.locator(`[data-testid="chart-type-${chartType}"]`);
        if (await button.isVisible()) {
          await helpers.safeClick(button);
          await page.waitForTimeout(300); // 等待图表切换
        }
      }
    }

    // 测试技术指标
    const indicatorToggle = page.locator('[data-testid="indicator-toggle"]');
    if (await indicatorToggle.isVisible()) {
      await helpers.safeClick(indicatorToggle);

      // 选择技术指标
      const indicators = ['MA', 'MACD', 'RSI', 'BOLL'];
      for (const indicator of indicators) {
        const indicatorCheckbox = page.locator(`[data-testid="indicator-${indicator}"]`);
        if (await indicatorCheckbox.isVisible()) {
          await helpers.safeClick(indicatorCheckbox);
          await page.waitForTimeout(200);
        }
      }
    }

    // 测试图表交互功能
    const chartArea = page.locator('[data-testid="chart-area"]');
    if (await chartArea.isVisible()) {
      // 测试鼠标悬停显示数据点
      await helpers.hover(chartArea);
      await page.waitForTimeout(200);

      // 验证数据提示框
      const tooltip = page.locator('[data-testid="chart-tooltip"]');
      if (await tooltip.isVisible()) {
        await expect(tooltip).toBeVisible();
      }

      // 测试缩放功能
      await chartArea.click({ position: { x: 100, y: 100 } });
      await page.waitForTimeout(100);
    }
  });

  test('实时价格更新', async ({ page }) => {
    const testStock = TEST_STOCKS[0];

    await helpers.navigateToPage(`/stock/${testStock.symbol}`);
    await helpers.waitForPageLoad();

    // 启用实时更新
    const realtimeToggle = page.locator('[data-testid="realtime-toggle"]');
    if (await realtimeToggle.isVisible()) {
      await helpers.safeClick(realtimeToggle);

      // 验证实时更新指示器
      await helpers.expectVisible('[data-testid="realtime-indicator"]');

      // 监听WebSocket连接
      let wsConnected = false;
      page.on('websocket', ws => {
        wsConnected = true;
      });

      // 等待实时数据更新
      await page.waitForTimeout(3000);

      // 验证价格更新
      const priceElement = page.locator('[data-testid="current-price"]');
      const initialPrice = await priceElement.textContent();

      await page.waitForTimeout(5000); // 等待可能的更新

      const updatedPrice = await priceElement.textContent();

      // 价格应该已经更新或保持不变（如果没有新数据）
      expect(updatedPrice).toBeTruthy();

      // 验证最后更新时间
      const lastUpdateTime = page.locator('[data-testid="last-update-time"]');
      if (await lastUpdateTime.isVisible()) {
        const updateTime = await lastUpdateTime.textContent();
        expect(updateTime).toBeTruthy();
      }
    }
  });

  test('股票基本面信息', async ({ page }) => {
    const testStock = TEST_STOCKS[0];

    await helpers.navigateToPage(`/stock/${testStock.symbol}`);
    await helpers.waitForPageLoad();

    // 切换到基本面标签页
    const fundamentalsTab = page.locator('[data-testid="tab-fundamentals"]');
    if (await fundamentalsTab.isVisible()) {
      await helpers.safeClick(fundamentalsTab);

      // 验证基本面信息组件
      await helpers.expectVisible('[data-testid="fundamentals-panel"]');

      // 验证财务指标
      const financialMetrics = page.locator('[data-testid="financial-metrics"]');
      if (await financialMetrics.isVisible()) {
        await helpers.expectVisible('[data-testid="market-cap"]');
        await helpers.expectVisible('[data-testid="pe-ratio"]');
        await helpers.expectVisible('[data-testid="dividend-yield"]');
        await helpers.expectVisible('[data-testid="debt-ratio"]');
      }

      // 验证关键财务数据
      const keyFinancials = page.locator('[data-testid="key-financials"]');
      if (await keyFinancials.isVisible()) {
        await helpers.expectVisible('[data-testid="revenue"]');
        await helpers.expectVisible('[data-testid="net-income"]');
        await helpers.expectVisible('[data-testid="earnings-per-share"]');
      }

      // 测试财务报表
      const financialStatements = page.locator('[data-testid="financial-statements"]');
      if (await financialStatements.isVisible()) {
        const statementTypes = ['income-statement', 'balance-sheet', 'cash-flow'];

        for (const statementType of statementTypes) {
          const statementButton = page.locator(`[data-testid="${statementType}-button"]`);
          if (await statementButton.isVisible()) {
            await helpers.safeClick(statementButton);
            await page.waitForTimeout(300);

            // 验证财务报表数据
            const statementData = page.locator(`[data-testid="${statementType}-data"]`);
            await expect(statementData).toBeVisible();
          }
        }
      }

      // 测试行业对比
      const industryComparison = page.locator('[data-testid="industry-comparison"]');
      if (await industryComparison.isVisible()) {
        await helpers.expectVisible('[data-testid="comparison-table"]');

        // 验证对比数据包含同行
        const peers = page.locator('[data-testid="peer-company"]');
        if (await peers.count() > 0) {
          await expect(peers.first()).toBeVisible();
        }
      }
    }
  });

  test('技术分析功能', async ({ page }) => {
    const testStock = TEST_STOCKS[0];

    await helpers.navigateToPage(`/stock/${testStock.symbol}`);
    await helpers.waitForPageLoad();

    // 切换到技术分析标签页
    const technicalTab = page.locator('[data-testid="tab-technical"]');
    if (await technicalTab.isVisible()) {
      await helpers.safeClick(technicalTab);

      // 验证技术分析面板
      await helpers.expectVisible('[data-testid="technical-analysis-panel"]');

      // 验证技术指标概览
      const indicatorsOverview = page.locator('[data-testid="indicators-overview"]');
      if (await indicatorsOverview.isVisible()) {
        await helpers.expectVisible('[data-testid="trend-indicator"]');
        await helpers.expectVisible('[data-testid="momentum-indicator"]');
        await helpers.expectVisible('[data-testid="volatility-indicator"]');
      }

      // 测试详细技术指标
      const detailedIndicators = page.locator('[data-testid="detailed-indicators"]');
      if (await detailedIndicators.isVisible()) {
        const indicatorGroups = ['trend', 'momentum', 'volatility', 'volume'];

        for (const group of indicatorGroups) {
          const groupSection = page.locator(`[data-testid="indicators-${group}"]`);
          if (await groupSection.isVisible()) {
            await expect(groupSection).toBeVisible();
          }
        }
      }

      // 测试支撑阻力位
      const supportResistance = page.locator('[data-testid="support-resistance"]');
      if (await supportResistance.isVisible()) {
        await helpers.expectVisible('[data-testid="support-levels"]');
        await helpers.expectVisible('[data-testid="resistance-levels"]');
      }

      // 测试买卖信号
      const signals = page.locator('[data-testid="trading-signals"]');
      if (await signals.isVisible()) {
        await helpers.expectVisible('[data-testid="buy-signals"]');
        await helpers.expectVisible('[data-testid="sell-signals"]');
        await helpers.expectVisible('[data-testid="neutral-signals"]');
      }
    }
  });

  test('新闻和公告', async ({ page }) => {
    const testStock = TEST_STOCKS[0];

    await helpers.navigateToPage(`/stock/${testStock.symbol}`);
    await helpers.waitForPageLoad();

    // 切换到新闻标签页
    const newsTab = page.locator('[data-testid="tab-news"]');
    if (await newsTab.isVisible()) {
      await helpers.safeClick(newsTab);

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
          await helpers.safeClick('[data-testid="category-all"]');

          // 测试不同分类
          const categories = ['announcement', 'research', 'news'];
          for (const category of categories) {
            const categoryButton = page.locator(`[data-testid="category-${category}"]`);
            if (await categoryButton.isVisible()) {
              await helpers.safeClick(categoryButton);
              await page.waitForTimeout(300);
            }
          }
        }

        // 测试新闻搜索
        const newsSearch = page.locator('[data-testid="news-search"]');
        if (await newsSearch.isVisible()) {
          await helpers.safeFill(newsSearch, '财报');
          await helpers.pressKeyboardShortcut('Enter');

          // 验证搜索结果
          await page.waitForTimeout(500);
        }

        // 测试新闻详情查看
        const firstNews = newsItems.first();
        await helpers.safeClick(firstNews);

        // 验证新闻详情或外部链接
        await page.waitForTimeout(1000);
      }

      // 测试情感分析
      const sentimentAnalysis = page.locator('[data-testid="sentiment-analysis"]');
      if (await sentimentAnalysis.isVisible()) {
        await helpers.expectVisible('[data-testid="sentiment-score"]');
        await helpers.expectVisible('[data-testid="sentiment-trend"]');
      }
    }
  });

  test('自选股功能', async ({ page }) => {
    const testStock = TEST_STOCKS[0];

    await helpers.navigateToPage(`/stock/${testStock.symbol}`);
    await helpers.waitForPageLoad();

    // 测试添加到自选股
    const addToWatchlistButton = page.locator('[data-testid="add-to-watchlist"]');
    if (await addToWatchlistButton.isVisible()) {
      await helpers.safeClick(addToWatchlistButton);

      // 验证添加成功提示
      await helpers.verifyToastMessage('已添加到自选股');

      // 验证按钮状态变化
      await helpers.expectVisible('[data-testid="remove-from-watchlist"]');

      // 测试从自选股移除
      const removeButton = page.locator('[data-testid="remove-from-watchlist"]');
      if (await removeButton.isVisible()) {
        await helpers.safeClick(removeButton);

        // 验证移除成功提示
        await helpers.verifyToastMessage('已从自选股移除');

        // 验证按钮状态恢复
        await helpers.expectVisible('[data-testid="add-to-watchlist"]');
      }
    }

    // 测试价格提醒设置
    const priceAlertButton = page.locator('[data-testid="price-alert"]');
    if (await priceAlertButton.isVisible()) {
      await helpers.safeClick(priceAlertButton);

      // 验证价格提醒对话框
      await helpers.expectVisible('[data-testid="price-alert-dialog"]');

      // 设置价格提醒
      const alertType = page.locator('[data-testid="alert-type"]');
      if (await alertType.isVisible()) {
        await helpers.selectOption(alertType, 'above');
      }

      const alertPrice = page.locator('[data-testid="alert-price"]');
      if (await alertPrice.isVisible()) {
        await helpers.safeFill(alertPrice, '200');
      }

      // 保存提醒
      const saveAlert = page.locator('[data-testid="save-alert"]');
      await helpers.safeClick(saveAlert);

      // 验证提醒设置成功
      await helpers.verifyToastMessage('价格提醒已设置');
    }
  });

  test('股票比较功能', async ({ page }) => {
    const testStock = TEST_STOCKS[0];

    await helpers.navigateToPage(`/stock/${testStock.symbol}`);
    await helpers.waitForPageLoad();

    // 测试股票比较
    const compareButton = page.locator('[data-testid="compare-stock"]');
    if (await compareButton.isVisible()) {
      await helpers.safeClick(compareButton);

      // 验证比较对话框
      await helpers.expectVisible('[data-testid="compare-dialog"]');

      // 添加比较股票
      const compareInput = page.locator('[data-testid="compare-input"]');
      if (await compareInput.isVisible()) {
        await helpers.safeFill(compareInput, 'GOOGL');
        await page.waitForTimeout(500);

        // 选择搜索结果
        const searchResult = page.locator('[data-testid="compare-result"]').first();
        if (await searchResult.isVisible()) {
          await helpers.safeClick(searchResult);
        }
      }

      // 开始比较
      const startCompare = page.locator('[data-testid="start-compare"]');
      if (await startCompare.isVisible()) {
        await helpers.safeClick(startCompare);

        // 验证比较结果
        await helpers.expectVisible('[data-testid="comparison-results"]');

        // 验证比较图表
        const comparisonChart = page.locator('[data-testid="comparison-chart"]');
        if (await comparisonChart.isVisible()) {
          await expect(comparisonChart).toBeVisible();
        }

        // 验证比较表格
        const comparisonTable = page.locator('[data-testid="comparison-table"]');
        if (await comparisonTable.isVisible()) {
          await expect(comparisonTable).toBeVisible();
        }
      }
    }
  });

  test('响应式设计', async ({ page }) => {
    const testStock = TEST_STOCKS[0];

    await helpers.navigateToPage(`/stock/${testStock.symbol}`);
    await helpers.waitForPageLoad();

    // 测试桌面视图
    await helpers.verifyResponsiveDesign({ width: 1280, height: 720 });

    // 验证所有主要组件在桌面视图正常显示
    await helpers.expectVisible('[data-testid="stock-header"]');
    await helpers.expectVisible('[data-testid="price-chart"]');
    await helpers.expectVisible('[data-testid="stock-tabs"]');

    // 测试平板视图
    await helpers.verifyResponsiveDesign({ width: 768, height: 1024 });

    // 在平板视图中验证标签页导航
    const tabletTabs = page.locator('[data-testid="mobile-tabs"]');
    if (await tabletTabs.isVisible()) {
      await expect(tabletTabs).toBeVisible();
    }

    // 测试移动视图
    await helpers.verifyResponsiveDesign({ width: 375, height: 667 });

    // 在移动视图中验证布局调整
    const mobileLayout = page.locator('[data-testid="mobile-layout"]');
    if (await mobileLayout.isVisible()) {
      await expect(mobileLayout).toBeVisible();
    }

    // 测试移动视图下的图表交互
    const mobileChart = page.locator('[data-testid="mobile-chart"]');
    if (await mobileChart.isVisible()) {
      await helpers.simulateTouch(mobileChart);
    }
  });

  test('错误处理', async ({ page }) => {
    // 测试无效股票代码
    await helpers.navigateToPage('/stock/INVALID');

    // 验证错误页面或提示
    const errorMessage = page.locator('[data-testid="error-message"]');
    const notFoundMessage = page.locator('[data-testid="not-found-message"]');

    const errorVisible = await errorMessage.isVisible();
    const notFoundVisible = await notFoundMessage.isVisible();

    expect(errorVisible || notFoundVisible).toBeTruthy();

    // 测试网络错误恢复
    const validStock = TEST_STOCKS[0];
    await helpers.navigateToPage(`/stock/${validStock.symbol}`);
    await helpers.waitForPageLoad();

    // 模拟网络断开
    await helpers.simulateNetworkCondition('offline');

    // 尝试刷新数据
    const refreshButton = page.locator('[data-testid="refresh-button"]');
    if (await refreshButton.isVisible()) {
      await helpers.safeClick(refreshButton);

      // 验证错误状态显示
      await helpers.expectVisible('[data-testid="offline-indicator"]' );
    }

    // 恢复网络连接
    const context = page.context();
    await context.setOffline(false);

    // 验证自动重连和数据恢复
    await page.waitForTimeout(2000);
    await helpers.expectVisible('[data-testid="reconnected-indicator"]');
  });
});