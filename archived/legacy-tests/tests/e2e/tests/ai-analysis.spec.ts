/**
 * AI投资分析功能端到端测试
 * 测试AI投资分析的完整用户流程
 */

import { test, expect } from '@playwright/test';
import { createTestHelpers } from '../helpers/test-helpers';
import { TEST_USERS, TEST_STOCKS, PERFORMANCE_THRESHOLDS } from '../fixtures/test-data';

test.describe('AI投资分析功能测试', () => {
  let helpers: ReturnType<typeof createTestHelpers>;

  test.beforeEach(async ({ page }) => {
    helpers = createTestHelpers(page);
    await helpers.setTestEnvironment();
    await helpers.clearStorage();
  });

  test('AI分析对话框基本功能', async ({ page }) => {
    // 导航到有AI分析功能的页面
    await helpers.navigateToPage('/dashboard');
    await helpers.waitForPageLoad();

    // 打开AI分析对话框
    const aiAnalysisButton = page.locator('[data-testid="ai-analysis-button"]');
    if (await aiAnalysisButton.isVisible()) {
      await helpers.safeClick(aiAnalysisButton);

      // 验证对话框打开
      await helpers.expectVisible('[data-testid="ai-analysis-dialog"]');

      // 验证对话框标题
      await helpers.expectText('[data-testid="dialog-title"]', 'AI投资分析师');

      // 验证基本组件
      await helpers.expectVisible('[data-testid="stock-symbol-input"]');
      await helpers.expectVisible('[data-testid="analyst-role-selector"]');
      await helpers.expectVisible('[data-testid="message-input"]');
      await helpers.expectVisible('[data-testid="send-button"]');

      // 验证分析师角色选项
      const roleOptions = page.locator('[data-testid="role-option"]');
      expect(await roleOptions.count()).toBeGreaterThan(0);

      // 验证预设建议区域
      const suggestionsPanel = page.locator('[data-testid="suggestions-panel"]');
      if (await suggestionsPanel.isVisible()) {
        await helpers.expectVisible('[data-testid="suggestion-item"]');
      }

      // 验证设置选项
      const settingsArea = page.locator('[data-testid="analysis-settings"]');
      if (await settingsArea.isVisible()) {
        await helpers.expectVisible('[data-testid="stream-toggle"]');
        await helpers.expectVisible('[data-testid="suggestions-toggle"]');
      }
    }
  });

  test('完整的AI分析流程', async ({ page }) => {
    await helpers.navigateToPage('/dashboard');
    await helpers.waitForPageLoad();

    // 打开AI分析对话框
    const aiAnalysisButton = page.locator('[data-testid="ai-analysis-button"]');
    if (await aiAnalysisButton.isVisible()) {
      await helpers.safeClick(aiAnalysisButton);

      // 输入股票代码
      const stockInput = page.locator('[data-testid="stock-symbol-input"]');
      await helpers.safeFill(stockInput, 'AAPL');

      // 选择分析师角色
      const roleSelector = page.locator('[data-testid="analyst-role-selector"]');
      await helpers.safeClick(roleSelector);
      await helpers.safeClick('[data-testid="role-technical-analyst"]');

      // 输入分析问题
      const messageInput = page.locator('[data-testid="message-input"]');
      await helpers.safeFill(messageInput, '请分析AAPL股票的技术面和基本面，并给出投资建议');

      // 发送分析请求
      const sendButton = page.locator('[data-testid="send-button"]');
      const startTime = Date.now();
      await helpers.safeClick(sendButton);

      // 验证用户消息显示
      await helpers.expectVisible('[data-testid="user-message"]');
      await helpers.expectText('[data-testid="user-message"]', '请分析AAPL股票的技术面和基本面，并给出投资建议');

      // 等待AI响应
      await helpers.waitForApiResponse('/api/ai/analyze');
      const responseTime = Date.now() - startTime;

      // 验证响应时间在合理范围内
      expect(responseTime).toBeLessThan(PERFORMANCE_THRESHOLDS.apiResponse.maxAIAnalysisResponse);

      // 验证AI回复显示
      await helpers.expectVisible('[data-testid="ai-response"]');
      const aiResponse = page.locator('[data-testid="ai-response"]');
      const responseText = await aiResponse.textContent();

      // 验证回复内容质量
      expect(responseText?.length).toBeGreaterThan(50); // 至少有一定内容
      expect(responseText).toContain('AAPL'); // 包含股票信息

      // 验证分析师信息显示
      await helpers.expectVisible('[data-testid="analyst-info"]');
      await helpers.expectText('[data-testid="analyst-role"]', '技术分析师');

      // 验证置信度显示
      const confidenceScore = page.locator('[data-testid="confidence-score"]');
      if (await confidenceScore.isVisible()) {
        const confidenceText = await confidenceScore.textContent();
        expect(confidenceText).toMatch(/\d+%/); // 应该包含百分比
      }

      // 验证推理过程
      const reasoningSection = page.locator('[data-testid="reasoning-section"]');
      if (await reasoningSection.isVisible()) {
        await helpers.expectVisible('[data-testid="reasoning-content"]');
      }

      // 验证建议部分
      const suggestionsSection = page.locator('[data-testid="suggestions-section"]');
      if (await suggestionsSection.isVisible()) {
        await helpers.expectVisible('[data-testid="suggestion-list"]');
      }
    }
  });

  test('多轮对话流程', async ({ page }) => {
    await helpers.navigateToPage('/dashboard');
    await helpers.waitForPageLoad();

    // 打开AI分析对话框
    const aiAnalysisButton = page.locator('[data-testid="ai-analysis-button"]');
    if (await aiAnalysisButton.isVisible()) {
      await helpers.safeClick(aiAnalysisButton);

      // 设置股票代码
      const stockInput = page.locator('[data-testid="stock-symbol-input"]');
      await helpers.safeFill(stockInput, 'AAPL');

      // 第一轮对话：基础分析
      const messageInput = page.locator('[data-testid="message-input"]');
      await helpers.safeFill(messageInput, '请简单分析AAPL的当前状况');
      await helpers.safeClick('[data-testid="send-button"]');

      // 等待AI回复
      await helpers.waitForApiResponse('/api/ai/analyze');
      await helpers.expectVisible('[data-testid="ai-response"]');

      // 第二轮对话：追问细节
      await helpers.safeFill(messageInput, '这个风险水平适合保守投资者吗？');
      await helpers.safeClick('[data-testid="send-button"]');

      // 验证上下文理解
      await helpers.waitForApiResponse('/api/ai/analyze');
      const secondResponse = page.locator('[data-testid="ai-response"]').last();
      const responseText = await secondResponse.textContent();

      // 验证回复参考了之前的对话内容
      expect(responseText).toMatch(/风险|保守|投资者/);

      // 第三轮对话：具体建议
      await helpers.safeFill(messageInput, '有什么具体的投资建议吗？');
      await helpers.safeClick('[data-testid="send-button"]');

      // 验证对话历史显示
      const conversationHistory = page.locator('[data-testid="conversation-history"]');
      const messageCount = await conversationHistory.locator('[data-testid^="message-"]').count();
      expect(messageCount).toBeGreaterThanOrEqual(6); // 至少3轮对话，每轮包含用户和AI消息

      // 验证对话连贯性
      await helpers.waitForApiResponse('/api/ai/analyze');
    }
  });

  test('不同分析师角色测试', async ({ page }) => {
    await helpers.navigateToPage('/dashboard');
    await helpers.waitForPageLoad();

    // 打开AI分析对话框
    const aiAnalysisButton = page.locator('[data-testid="ai-analysis-button"]');
    if (await aiAnalysisButton.isVisible()) {
      await helpers.safeClick(aiAnalysisButton);

      // 设置股票代码
      const stockInput = page.locator('[data-testid="stock-symbol-input"]');
      await helpers.safeFill(stockInput, 'AAPL');

      // 测试不同分析师角色
      const analystRoles = [
        { role: 'technical-analyst', name: '技术分析师', expectedKeywords: ['技术', '图表', '指标'] },
        { role: 'fundamental-analyst', name: '基本面分析师', expectedKeywords: ['财务', '基本面', '业绩'] },
        { role: 'news-analyst', name: '新闻分析师', expectedKeywords: ['新闻', '市场', '情绪'] },
        { role: 'risk-analyst', name: '风控分析师', expectedKeywords: ['风险', '控制', '策略'] }
      ];

      for (const analystRole of analystRoles) {
        // 选择分析师角色
        const roleSelector = page.locator('[data-testid="analyst-role-selector"]');
        await helpers.safeClick(roleSelector);
        await helpers.safeClick(`[data-testid="role-${analystRole.role}"]`);

        // 发送分析请求
        const messageInput = page.locator('[data-testid="message-input"]');
        await helpers.safeFill(messageInput, `请从${analystRole.name}角度分析AAPL`);
        await helpers.safeClick('[data-testid="send-button"]');

        // 等待AI回复
        await helpers.waitForApiResponse('/api/ai/analyze');
        await helpers.expectVisible('[data-testid="ai-response"]');

        // 验证角色特定内容
        const aiResponse = page.locator('[data-testid="ai-response"]').last();
        const responseText = await aiResponse.textContent();

        // 验证回复包含角色相关的关键词
        const hasRelevantKeyword = analystRole.expectedKeywords.some(keyword =>
          responseText?.toLowerCase().includes(keyword.toLowerCase())
        );
        expect(hasRelevantKeyword).toBeTruthy();

        // 验证角色标识显示正确
        await helpers.expectText('[data-testid="analyst-role"]', analystRole.name);

        // 短暂延迟避免请求过频
        await page.waitForTimeout(1000);
      }
    }
  });

  test('流式响应测试', async ({ page }) => {
    await helpers.navigateToPage('/dashboard');
    await helpers.waitForPageLoad();

    // 打开AI分析对话框
    const aiAnalysisButton = page.locator('[data-testid="ai-analysis-button"]');
    if (await aiAnalysisButton.isVisible()) {
      await helpers.safeClick(aiAnalysisButton);

      // 启用流式响应
      const streamToggle = page.locator('[data-testid="stream-toggle"]');
      if (await streamToggle.isVisible()) {
        await helpers.safeClick(streamToggle);

        // 验证流式响应已启用
        await helpers.expectVisible('[data-testid="stream-indicator"]');

        // 设置股票代码和问题
        const stockInput = page.locator('[data-testid="stock-symbol-input"]');
        await helpers.safeFill(stockInput, 'AAPL');

        const messageInput = page.locator('[data-testid="message-input"]');
        await helpers.safeFill(messageInput, '请详细分析AAPL的投资价值，包括技术面、基本面和市场前景');
        await helpers.safeClick('[data-testid="send-button"]');

        // 验证流式响应指示器
        await helpers.expectVisible('[data-testid="streaming-indicator"]');

        // 监听流式响应内容
        let previousContent = '';
        let contentChanges = 0;

        // 定期检查内容变化
        const checkInterval = setInterval(async () => {
          const currentResponse = page.locator('[data-testid="ai-response"]').last();
          const currentContent = await currentResponse.textContent() || '';

          if (currentContent !== previousContent) {
            contentChanges++;
            previousContent = currentContent;
          }

          // 检查是否完成
          const isComplete = await page.locator('[data-testid="streaming-complete"]').isVisible();
          if (isComplete || contentChanges > 5) {
            clearInterval(checkInterval);
          }
        }, 500);

        // 等待流式响应完成
        await page.waitForTimeout(10000);

        // 验证最终内容
        const finalResponse = page.locator('[data-testid="ai-response"]').last();
        const finalContent = await finalResponse.textContent();
        expect(finalContent?.length).toBeGreaterThan(100);

        // 验证流式指示器消失
        await helpers.expectHidden('[data-testid="streaming-indicator"]');

        clearInterval(checkInterval);
      }
    }
  });

  test('建议功能测试', async ({ page }) => {
    await helpers.navigateToPage('/dashboard');
    await helpers.waitForPageLoad();

    // 打开AI分析对话框
    const aiAnalysisButton = page.locator('[data-testid="ai-analysis-button"]');
    if (await aiAnalysisButton.isVisible()) {
      await helpers.safeClick(aiAnalysisButton);

      // 输入股票代码
      const stockInput = page.locator('[data-testid="stock-symbol-input"]');
      await helpers.safeFill(stockInput, 'AAPL');

      // 等待建议加载
      await page.waitForTimeout(2000);

      // 验证建议面板
      const suggestionsPanel = page.locator('[data-testid="suggestions-panel"]');
      if (await suggestionsPanel.isVisible()) {
        const suggestionItems = page.locator('[data-testid="suggestion-item"]');
        const suggestionCount = await suggestionItems.count();

        if (suggestionCount > 0) {
          // 点击第一个建议
          const firstSuggestion = suggestionItems.first();
          await helpers.safeClick(firstSuggestion);

          // 验证建议被填入输入框
          const messageInput = page.locator('[data-testid="message-input"]');
          const inputContent = await messageInput.inputValue();
          expect(inputContent.length).toBeGreaterThan(0);

          // 发送基于建议的消息
          await helpers.safeClick('[data-testid="send-button"]');

          // 验证AI回复
          await helpers.waitForApiResponse('/api/ai/analyze');
          await helpers.expectVisible('[data-testid="ai-response"]');
        }

        // 测试建议开关
        const suggestionsToggle = page.locator('[data-testid="suggestions-toggle"]');
        if (await suggestionsToggle.isVisible()) {
          await helpers.safeClick(suggestionsToggle);

          // 验证建议面板隐藏
          await helpers.expectHidden('[data-testid="suggestions-panel"]');

          // 重新显示建议
          await helpers.safeClick(suggestionsToggle);
          await helpers.expectVisible('[data-testid="suggestions-panel"]');
        }
      }
    }
  });

  test('对话管理功能', async ({ page }) => {
    await helpers.navigateToPage('/dashboard');
    await helpers.waitForPageLoad();

    // 打开AI分析对话框
    const aiAnalysisButton = page.locator('[data-testid="ai-analysis-button"]');
    if (await aiAnalysisButton.isVisible()) {
      await helpers.safeClick(aiAnalysisButton);

      // 进行几轮对话生成历史记录
      const stockInput = page.locator('[data-testid="stock-symbol-input"]');
      await helpers.safeFill(stockInput, 'AAPL');

      const messages = [
        '请分析AAPL的技术指标',
        '风险如何？',
        '有什么投资建议？'
      ];

      for (const message of messages) {
        const messageInput = page.locator('[data-testid="message-input"]');
        await helpers.safeFill(messageInput, message);
        await helpers.safeClick('[data-testid="send-button"]');
        await helpers.waitForApiResponse('/api/ai/analyze');
        await page.waitForTimeout(1000);
      }

      // 测试清空对话
      const clearButton = page.locator('[data-testid="clear-conversation"]');
      if (await clearButton.isVisible()) {
        await helpers.safeClick(clearButton);

        // 验证对话历史被清空
        const conversationHistory = page.locator('[data-testid="conversation-history"]');
        const messageCount = await conversationHistory.locator('[data-testid^="message-"]').count();
        expect(messageCount).toBe(0);
      }

      // 重新开始对话
      await helpers.safeFill(messageInput, '重新开始，请分析AAPL');
      await helpers.safeClick('[data-testid="send-button"]');
      await helpers.waitForApiResponse('/api/ai/analyze');

      // 测试对话导出
      const exportButton = page.locator('[data-testid="export-conversation"]');
      if (await exportButton.isVisible()) {
        // 监听下载事件
        const downloadPromise = page.waitForEvent('download');
        await helpers.safeClick(exportButton);

        // 验证下载触发
        const download = await downloadPromise;
        expect(download.suggestedFilename()).toContain('AI分析对话');
      }
    }
  });

  test('错误处理和边界情况', async ({ page }) => {
    await helpers.navigateToPage('/dashboard');
    await helpers.waitForPageLoad();

    // 打开AI分析对话框
    const aiAnalysisButton = page.locator('[data-testid="ai-analysis-button"]');
    if (await aiAnalysisButton.isVisible()) {
      await helpers.safeClick(aiAnalysisButton);

      // 测试空股票代码
      const messageInput = page.locator('[data-testid="message-input"]');
      await helpers.safeFill(messageInput, '请分析这只股票');
      await helpers.safeClick('[data-testid="send-button"]');

      // 验证错误提示
      await helpers.expectVisible('[data-testid="error-message"]');
      await helpers.expectText('[data-testid="error-message"]', '请输入股票代码');

      // 测试无效股票代码
      const stockInput = page.locator('[data-testid="stock-symbol-input"]');
      await helpers.safeFill(stockInput, 'INVALID');
      await helpers.safeFill(messageInput, '请分析这只股票');
      await helpers.safeClick('[data-testid="send-button"]');

      // 验证错误处理
      await helpers.waitForApiResponse('/api/ai/analyze');
      const errorMessage = page.locator('[data-testid="error-message"]');
      if (await errorMessage.isVisible()) {
        await expect(errorMessage).toContainText('找不到' || '无效');
      }

      // 测试空消息
      await helpers.safeFill(stockInput, 'AAPL');
      await helpers.safeFill(messageInput, '');
      await helpers.safeClick('[data-testid="send-button"]');

      // 验证消息验证
      await helpers.expectVisible('[data-testid="error-message"]');
      await helpers.expectText('[data-testid="error-message"]', '请输入分析问题');

      // 测试网络错误模拟
      await helpers.simulateNetworkCondition('offline');

      await helpers.safeFill(messageInput, '请分析AAPL');
      await helpers.safeClick('[data-testid="send-button"]');

      // 验证离线状态处理
      await helpers.expectVisible('[data-testid="offline-indicator"]');

      // 恢复网络连接
      const context = page.context();
      await context.setOffline(false);

      // 验证自动重连提示
      await helpers.expectVisible('[data-testid="reconnected-indicator"]');
    }
  });

  test('性能和响应时间测试', async ({ page }) => {
    await helpers.navigateToPage('/dashboard');
    await helpers.waitForPageLoad();

    // 打开AI分析对话框
    const aiAnalysisButton = page.locator('[data-testid="ai-analysis-button"]');
    if (await aiAnalysisButton.isVisible()) {
      // 测量对话框打开时间
      const dialogOpenStart = Date.now();
      await helpers.safeClick(aiAnalysisButton);
      await helpers.expectVisible('[data-testid="ai-analysis-dialog"]');
      const dialogOpenTime = Date.now() - dialogOpenStart;

      expect(dialogOpenTime).toBeLessThan(1000); // 对话框应该在1秒内打开

      // 设置分析参数
      const stockInput = page.locator('[data-testid="stock-symbol-input"]');
      await helpers.safeFill(stockInput, 'AAPL');

      const messageInput = page.locator('[data-testid="message-input"]');
      await helpers.safeFill(messageInput, '请快速分析AAPL的投资价值');

      // 测量AI响应时间
      const analysisStart = Date.now();
      await helpers.safeClick('[data-testid="send-button"]');

      // 监听API调用
      let responseReceived = false;
      page.on('response', response => {
        if (response.url().includes('/api/ai/analyze')) {
          responseReceived = true;
        }
      });

      // 等待响应
      await helpers.waitForApiResponse('/api/ai/analyze');
      const analysisTime = Date.now() - analysisStart;

      // 验证响应时间在合理范围内
      expect(analysisTime).toBeLessThan(PERFORMANCE_THRESHOLDS.apiResponse.maxAIAnalysisResponse);

      // 验证响应内容质量
      await helpers.expectVisible('[data-testid="ai-response"]');
      const aiResponse = page.locator('[data-testid="ai-response"]');
      const responseText = await aiResponse.textContent();
      expect(responseText?.length).toBeGreaterThan(50);

      // 测试并发请求处理
      const concurrentRequests = 3;
      const requestPromises = [];

      for (let i = 0; i < concurrentRequests; i++) {
        await helpers.safeFill(messageInput, `并发测试请求 ${i + 1}`);
        requestPromises.push(helpers.safeClick('[data-testid="send-button"]'));
        await page.waitForTimeout(500);
      }

      // 等待所有请求完成
      await Promise.all(requestPromises);

      // 验证所有请求都有响应
      const responseCount = await page.locator('[data-testid="ai-response"]').count();
      expect(responseCount).toBeGreaterThanOrEqual(concurrentRequests + 1); // 包括第一个请求
    }
  });
});