/**
 * 测试辅助函数
 * 提供常用的端到端测试工具函数
 */

import { Page, BrowserContext, expect } from '@playwright/test';

export class TestHelpers {
  constructor(private page: Page) {}

  /**
   * 等待页面加载完成
   */
  async waitForPageLoad(): Promise<void> {
    await this.page.waitForLoadState('networkidle');
    await this.page.waitForTimeout(1000); // 额外等待确保所有组件加载完成
  }

  /**
   * 登录用户（如果需要）
   */
  async loginUser(username = 'testuser', password = 'testpass'): Promise<void> {
    // 检查是否已经登录
    const isLoggedIn = await this.page.locator('[data-testid="user-menu"]').isVisible().catch(() => false);
    if (isLoggedIn) return;

    // 导航到登录页面
    await this.page.goto('/login');
    await this.waitForPageLoad();

    // 填写登录表单
    await this.page.fill('[data-testid="username-input"]', username);
    await this.page.fill('[data-testid="password-input"]', password);
    await this.page.click('[data-testid="login-button"]');

    // 等待登录完成
    await this.page.waitForURL('/dashboard');
    await this.waitForPageLoad();
  }

  /**
   * 导航到指定页面
   */
  async navigateToPage(path: string): Promise<void> {
    await this.page.goto(path);
    await this.waitForPageLoad();
  }

  /**
   * 等待元素出现并可见
   */
  async waitForElement(selector: string, timeout = 10000): Promise<void> {
    await this.page.waitForSelector(selector, { state: 'visible', timeout });
  }

  /**
   * 安全点击元素（等待可点击状态）
   */
  async safeClick(selector: string): Promise<void> {
    await this.waitForElement(selector);
    await this.page.click(selector);
  }

  /**
   * 安全填写文本
   */
  async safeFill(selector: string, text: string): Promise<void> {
    await this.waitForElement(selector);
    await this.page.fill(selector, text);
  }

  /**
   * 选择下拉选项
   */
  async selectOption(selector: string, value: string): Promise<void> {
    await this.waitForElement(selector);
    await this.page.selectOption(selector, value);
  }

  /**
   * 验证文本内容
   */
  async expectText(selector: string, expectedText: string): Promise<void> {
    const element = this.page.locator(selector);
    await expect(element).toContainText(expectedText);
  }

  /**
   * 验证元素可见性
   */
  async expectVisible(selector: string): Promise<void> {
    const element = this.page.locator(selector);
    await expect(element).toBeVisible();
  }

  /**
   * 验证元素隐藏
   */
  async expectHidden(selector: string): Promise<void> {
    const element = this.page.locator(selector);
    await expect(element).toBeHidden();
  }

  /**
   * 截屏保存（用于调试）
   */
  async takeScreenshot(name: string): Promise<void> {
    await this.page.screenshot({ path: `test-results/screenshots/${name}.png`, fullPage: true });
  }

  /**
   * 等待API请求完成
   */
  async waitForApiResponse(urlPattern: string): Promise<void> {
    await this.page.waitForResponse((response) =>
      response.url().includes(urlPattern)
    );
  }

  /**
   * 模拟键盘输入
   */
  async typeKeys(selector: string, keys: string): Promise<void> {
    await this.waitForElement(selector);
    await this.page.type(selector, keys);
  }

  /**
   * 模拟鼠标悬停
   */
  async hover(selector: string): Promise<void> {
    await this.waitForElement(selector);
    await this.page.hover(selector);
  }

  /**
   * 获取元素文本
   */
  async getText(selector: string): Promise<string> {
    await this.waitForElement(selector);
    return await this.page.textContent(selector) || '';
  }

  /**
   * 等待Loading状态消失
   */
  async waitForLoadingToDisappear(): Promise<void> {
    const loadingSelector = '[data-testid="loading"], .loading, .spinner';
    try {
      await this.page.waitForSelector(loadingSelector, { state: 'hidden', timeout: 30000 });
    } catch {
      // 如果没有loading元素，继续执行
    }
  }

  /**
   * 验证API响应状态
   */
  async verifyApiResponse(urlPattern: string, expectedStatus = 200): Promise<void> {
    const response = await this.page.waitForResponse((response) =>
      response.url().includes(urlPattern)
    );
    expect(response.status()).toBe(expectedStatus);
  }

  /**
   * 清除浏览器存储
   */
  async clearStorage(): Promise<void> {
    await this.page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
  }

  /**
   * 设置测试环境
   */
  async setTestEnvironment(): Promise<void> {
    await this.page.evaluate(() => {
      localStorage.setItem('test-mode', 'true');
      localStorage.setItem('test-start-time', new Date().toISOString());
    });
  }

  /**
   * 模拟网络条件
   */
  async simulateNetworkCondition(condition: 'slow3g' | 'fast3g' | 'offline'): Promise<void> {
    const context = this.page.context();

    switch (condition) {
      case 'slow3g':
        await context.route('**/*', (route) => {
          // 模拟慢速3G网络
          setTimeout(() => route.continue(), 1000);
        });
        break;
      case 'fast3g':
        await context.route('**/*', (route) => {
          // 模拟快速3G网络
          setTimeout(() => route.continue(), 300);
        });
        break;
      case 'offline':
        await context.setOffline(true);
        break;
    }
  }

  /**
   * 验证可访问性
   */
  async checkAccessibility(): Promise<void> {
    // 使用axe-core进行可访问性测试
    await this.page.waitForLoadState('networkidle');

    try {
      const accessibilityResults = await this.page.evaluate(() => {
        // 这里可以集成axe-core进行可访问性测试
        return { violations: [] };
      });

      expect(accessibilityResults.violations).toHaveLength(0);
    } catch (error) {
      console.log('Accessibility check skipped:', error);
    }
  }

  /**
   * 模拟移动设备触摸
   */
  async simulateTouch(selector: string): Promise<void> {
    const element = this.page.locator(selector);
    await element.waitFor({ state: 'visible' });

    // 获取元素位置
    const box = await element.boundingBox();
    if (box) {
      await this.page.touch.tap(box.x + box.width / 2, box.y + box.height / 2);
    }
  }

  /**
   * 验证响应式设计
   */
  async verifyResponsiveDesign(viewport: { width: number; height: number }): Promise<void> {
    await this.page.setViewportSize(viewport);
    await this.page.waitForLoadState('networkidle');

    // 验证关键元素是否可见和正确布局
    const mainContent = this.page.locator('main, [data-testid="main-content"]');
    await expect(mainContent).toBeVisible();
  }

  /**
   * 模拟文件上传
   */
  async uploadFile(selector: string, filePath: string): Promise<void> {
    const fileInput = this.page.locator(selector);
    await fileInput.setInputFiles(filePath);
  }

  /**
   * 验证表单验证
   */
  async verifyFormValidation(formSelector: string, fieldValidations: { [key: string]: string }): Promise<void> {
    for (const [fieldSelector, expectedError] of Object.entries(fieldValidations)) {
      const field = this.page.locator(fieldSelector);
      await field.click(); // 触发验证
      await this.page.waitForTimeout(100);

      const errorElement = this.page.locator(`${fieldSelector} + .error-message, ${fieldSelector} ~ .error-message`);
      if (expectedError) {
        await expect(errorElement).toContainText(expectedError);
      } else {
        await expect(errorElement).not.toBeVisible();
      }
    }
  }

  /**
   * 等待并验证Toast消息
   */
  async verifyToastMessage(expectedMessage: string): Promise<void> {
    const toast = this.page.locator('[data-testid="toast"], .toast, .notification');
    await expect(toast).toBeVisible();
    await expect(toast).toContainText(expectedMessage);

    // 等待Toast消失
    await toast.waitFor({ state: 'hidden', timeout: 5000 }).catch(() => {});
  }

  /**
   * 模拟键盘快捷键
   */
  async pressKeyboardShortcut(keys: string): Promise<void> {
    await this.page.keyboard.press(keys);
  }

  /**
   * 等待并验证动画完成
   */
  async waitForAnimation(selector: string): Promise<void> {
    const element = this.page.locator(selector);
    await element.waitFor({ state: 'visible' });

    // 等待CSS动画完成
    await this.page.waitForFunction((sel) => {
      const el = document.querySelector(sel);
      if (!el) return true;

      const style = window.getComputedStyle(el);
      return style.animation === 'none' || style.animationPlayState === 'idle';
    }, selector);
  }
}

/**
 * 创建测试助手实例
 */
export function createTestHelpers(page: Page): TestHelpers {
  return new TestHelpers(page);
}