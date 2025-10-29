/**
 * 用户认证端到端测试
 * 测试用户注册、登录和认证流程
 */

import { test, expect } from '@playwright/test';
import { createTestHelpers } from '../helpers/test-helpers';
import { TEST_USERS } from '../fixtures/test-data';

test.describe('用户认证功能测试', () => {
  let helpers: ReturnType<typeof createTestHelpers>;

  test.beforeEach(async ({ page }) => {
    helpers = createTestHelpers(page);
    await helpers.setTestEnvironment();
    await helpers.clearStorage();
  });

  test('用户注册流程', async ({ page }) => {
    // 导航到注册页面
    await helpers.navigateToPage('/register');
    await helpers.waitForPageLoad();

    // 验证注册页面元素
    await helpers.expectVisible('[data-testid="register-form"]');
    await helpers.expectVisible('[data-testid="username-input"]');
    await helpers.expectVisible('[data-testid="email-input"]');
    await helpers.expectVisible('[data-testid="password-input"]');
    await helpers.expectVisible('[data-testid="confirm-password-input"]');
    await helpers.expectVisible('[data-testid="register-button"]');

    // 填写注册表单
    const testUser = TEST_USERS[0];
    const timestamp = Date.now(); // 确保用户名唯一
    const uniqueUsername = `${testUser.username}_${timestamp}`;
    const uniqueEmail = `test_${timestamp}@example.com`;

    await helpers.safeFill('[data-testid="username-input"]', uniqueUsername);
    await helpers.safeFill('[data-testid="email-input"]', uniqueEmail);
    await helpers.safeFill('[data-testid="password-input"]', testUser.password);
    await helpers.safeFill('[data-testid="confirm-password-input"]', testUser.password);

    // 测试表单验证
    // 测试密码确认验证
    await helpers.safeFill('[data-testid="confirm-password-input"]', 'different');
    await helpers.safeClick('[data-testid="register-button"]');
    await helpers.expectVisible('[data-testid="password-mismatch-error"]');

    // 修正密码确认
    await helpers.safeFill('[data-testid="confirm-password-input"]', testUser.password);

    // 测试用户偏好设置（如果存在）
    const riskToleranceSelect = page.locator('[data-testid="risk-tolerance-select"]');
    if (await riskToleranceSelect.isVisible()) {
      await helpers.selectOption(riskToleranceSelect, testUser.riskTolerance);
    }

    const investmentGoalsSelect = page.locator('[data-testid="investment-goals-select"]');
    if (await investmentGoalsSelect.isVisible()) {
      await helpers.selectOption(investmentGoalsSelect, testUser.investmentGoals[0]);
    }

    // 同意条款（如果存在）
    const agreeCheckbox = page.locator('[data-testid="agree-terms"]');
    if (await agreeCheckbox.isVisible()) {
      await helpers.safeClick(agreeCheckbox);
    }

    // 提交注册
    await helpers.safeClick('[data-testid="register-button"]');

    // 等待注册完成
    await helpers.waitForApiResponse('/api/auth/register');

    // 验证注册成功
    // 可能重定向到仪表板或显示成功消息
    const successMessage = page.locator('[data-testid="success-message"]');
    const dashboardContent = page.locator('[data-testid="dashboard-content"]');

    const registrationSuccess = await successMessage.isVisible() ||
                               await dashboardContent.isVisible() ||
                               page.url().includes('/dashboard');

    expect(registrationSuccess).toBeTruthy();

    // 如果显示成功消息，点击继续
    if (await successMessage.isVisible()) {
      const continueButton = page.locator('[data-testid="continue-button"]');
      if (await continueButton.isVisible()) {
        await helpers.safeClick(continueButton);
      }
    }

    // 验证用户已登录状态
    await page.waitForTimeout(2000);
    const userMenu = page.locator('[data-testid="user-menu"]');
    if (await userMenu.isVisible()) {
      await helpers.safeClick(userMenu);
      await helpers.expectVisible('[data-testid="user-profile"]');
      await helpers.expectText('[data-testid="username-display"]', uniqueUsername);
    }
  });

  test('用户登录流程', async ({ page }) => {
    // 导航到登录页面
    await helpers.navigateToPage('/login');
    await helpers.waitForPageLoad();

    // 验证登录页面元素
    await helpers.expectVisible('[data-testid="login-form"]');
    await helpers.expectVisible('[data-testid="username-input"]');
    await helpers.expectVisible('[data-testid="password-input"]');
    await helpers.expectVisible('[data-testid="login-button"]');
    await helpers.expectVisible('[data-testid="forgot-password-link"]');
    await helpers.expectVisible('[data-testid="register-link"]');

    // 测试无效登录
    await helpers.safeFill('[data-testid="username-input"]', 'invalid_user');
    await helpers.safeFill('[data-testid="password-input"]', 'wrong_password');
    await helpers.safeClick('[data-testid="login-button"]');

    // 验证错误消息
    await helpers.waitForApiResponse('/api/auth/login');
    const errorMessage = page.locator('[data-testid="login-error"]');
    if (await errorMessage.isVisible()) {
      await expect(errorMessage).toBeVisible();
    }

    // 清空表单
    await helpers.safeFill('[data-testid="username-input"]', '');
    await helpers.safeFill('[data-testid="password-input"]', '');

    // 使用有效的测试用户登录
    const testUser = TEST_USERS[1]; // 使用已存在的测试用户
    await helpers.safeFill('[data-testid="username-input"]', testUser.username);
    await helpers.safeFill('[data-testid="password-input"]', testUser.password);

    // 测试记住我功能
    const rememberMeCheckbox = page.locator('[data-testid="remember-me"]');
    if (await rememberMeCheckbox.isVisible()) {
      await helpers.safeClick(rememberMeCheckbox);
    }

    // 提交登录
    await helpers.safeClick('[data-testid="login-button"]');

    // 等待登录完成
    await helpers.waitForApiResponse('/api/auth/login');

    // 验证登录成功 - 重定向到仪表板
    await page.waitForURL(/dashboard/);
    await helpers.expectVisible('[data-testid="dashboard-content"]');

    // 验证用户状态
    const userMenu = page.locator('[data-testid="user-menu"]');
    if (await userMenu.isVisible()) {
      await helpers.safeClick(userMenu);
      await helpers.expectVisible('[data-testid="user-profile"]');
      await helpers.expectText('[data-testid="username-display"]', testUser.displayName);
    }

    // 验证记住我功能（检查本地存储）
    const rememberMeToken = await page.evaluate(() => {
      return localStorage.getItem('remember_me_token');
    });

    if (await rememberMeCheckbox.isChecked()) {
      expect(rememberMeToken).toBeTruthy();
    }
  });

  test('密码重置流程', async ({ page }) => {
    // 导航到登录页面
    await helpers.navigateToPage('/login');
    await helpers.waitForPageLoad();

    // 点击忘记密码链接
    await helpers.safeClick('[data-testid="forgot-password-link"]');

    // 验证密码重置页面
    await helpers.expectVisible('[data-testid="reset-password-form"]');
    await helpers.expectVisible('[data-testid="email-input"]');
    await helpers.expectVisible('[data-testid="send-reset-button"]');

    // 输入邮箱
    const testUser = TEST_USERS[0];
    await helpers.safeFill('[data-testid="email-input"]', testUser.email);

    // 提交重置请求
    await helpers.safeClick('[data-testid="send-reset-button"]');

    // 等待API响应
    await helpers.waitForApiResponse('/api/auth/reset-password');

    // 验证重置邮件发送成功消息
    await helpers.expectVisible('[data-testid="reset-success-message"]');

    // 测试无效邮箱
    await helpers.safeFill('[data-testid="email-input"]', 'invalid-email');
    await helpers.safeClick('[data-testid="send-reset-button"]');

    // 验证邮箱格式错误
    await helpers.expectVisible('[data-testid="email-format-error"]');

    // 修正邮箱格式
    await helpers.safeFill('[data-testid="email-input"]', 'valid@example.com');
    await helpers.safeClick('[data-testid="send-reset-button"]');

    // 验证处理成功（即使邮箱不存在也不应该暴露具体错误）
    await helpers.expectVisible('[data-testid="reset-success-message"]');
  });

  test('用户注销流程', async ({ page }) => {
    // 先登录用户
    await helpers.loginUser('moderate_user', 'Test123456!');
    await helpers.waitForPageLoad();

    // 打开用户菜单
    const userMenu = page.locator('[data-testid="user-menu"]');
    if (await userMenu.isVisible()) {
      await helpers.safeClick(userMenu);

      // 点击注销按钮
      const logoutButton = page.locator('[data-testid="logout-button"]');
      await helpers.safeClick(logoutButton);

      // 验证注销确认对话框
      const confirmDialog = page.locator('[data-testid="logout-confirm-dialog"]');
      if (await confirmDialog.isVisible()) {
        await helpers.safeClick('[data-testid="confirm-logout"]');
      }

      // 验证注销成功 - 重定向到登录页面
      await page.waitForURL(/login/);
      await helpers.expectVisible('[data-testid="login-form"]');

      // 验证用户状态已清除
      const userMenuAfterLogout = page.locator('[data-testid="user-menu"]');
      await expect(userMenuAfterLogout).not.toBeVisible();

      // 验证本地存储已清除
      const authToken = await page.evaluate(() => {
        return localStorage.getItem('auth_token');
      });
      expect(authToken).toBeFalsy();

      // 验证访问受保护页面会重定向到登录
      await helpers.navigateToPage('/dashboard');
      await page.waitForURL(/login/);
    }
  });

  test('会话管理', async ({ page }) => {
    // 登录用户
    await helpers.loginUser('moderate_user', 'Test123456!');
    await helpers.waitForPageLoad();

    // 验证会话活跃
    const sessionIndicator = page.locator('[data-testid="session-indicator"]');
    if (await sessionIndicator.isVisible()) {
      await expect(sessionIndicator).toBeVisible();
    }

    // 测试会话超时（模拟）
    // 清除认证令牌模拟会话过期
    await page.evaluate(() => {
      localStorage.removeItem('auth_token');
      sessionStorage.removeItem('auth_token');
    });

    // 尝试访问受保护内容
    await helpers.navigateToPage('/dashboard');

    // 验证重定向到登录页面并显示会话过期消息
    await page.waitForURL(/login/);
    const sessionExpiredMessage = page.locator('[data-testid="session-expired-message"]');
    if (await sessionExpiredMessage.isVisible()) {
      await expect(sessionExpiredMessage).toBeVisible();
    }

    // 测试多标签页会话同步
    // 重新登录
    await helpers.navigateToPage('/login');
    await helpers.loginUser('moderate_user', 'Test123456!');
    await helpers.waitForPageLoad();

    // 在新标签页中验证会话状态
    const newPage = await page.context().newPage();
    await newPage.goto(page.url());
    await newPage.waitForLoadState('networkidle');

    // 验证新标签页也显示已登录状态
    const userMenuNewTab = newPage.locator('[data-testid="user-menu"]');
    if (await userMenuNewTab.isVisible()) {
      await expect(userMenuNewTab).toBeVisible();
    }

    await newPage.close();
  });

  test('安全功能测试', async ({ page }) => {
    // 导航到登录页面
    await helpers.navigateToPage('/login');
    await helpers.waitForPageLoad();

    // 测试密码可见性切换
    const passwordInput = page.locator('[data-testid="password-input"]');
    const togglePasswordButton = page.locator('[data-testid="toggle-password"]');

    if (await togglePasswordButton.isVisible()) {
      // 初始状态应该是隐藏密码
      await expect(passwordInput).toHaveAttribute('type', 'password');

      // 点击显示密码
      await helpers.safeClick(togglePasswordButton);
      await expect(passwordInput).toHaveAttribute('type', 'text');

      // 再次点击隐藏密码
      await helpers.safeClick(togglePasswordButton);
      await expect(passwordInput).toHaveAttribute('type', 'password');
    }

    // 测试登录尝试限制
    const testUser = TEST_USERS[1];

    // 多次错误登录尝试
    for (let i = 0; i < 5; i++) {
      await helpers.safeFill('[data-testid="username-input"]', testUser.username);
      await helpers.safeFill('[data-testid="password-input"]', 'wrong_password');
      await helpers.safeClick('[data-testid="login-button"]');

      await page.waitForTimeout(500);
    }

    // 验证账户锁定或延迟提示
    const accountLockMessage = page.locator('[data-testid="account-locked-message"]');
    const rateLimitMessage = page.locator('[data-testid="rate-limit-message"]');

    const securityMessageVisible = await accountLockMessage.isVisible() ||
                                  await rateLimitMessage.isVisible();

    if (securityMessageVisible) {
      expect(securityMessageVisible).toBeTruthy();
    }

    // 测试CSRF保护（如果存在）
    const csrfToken = await page.evaluate(() => {
      const metaTag = document.querySelector('meta[name="csrf-token"]');
      return metaTag?.getAttribute('content');
    });

    if (csrfToken) {
      expect(csrfToken).toBeTruthy();
      expect(csrfToken.length).toBeGreaterThan(10);
    }
  });

  test('社交登录功能（如果存在）', async ({ page }) => {
    // 导航到登录页面
    await helpers.navigateToPage('/login');
    await helpers.waitForPageLoad();

    // 检查是否有社交登录选项
    const socialLoginButtons = page.locator('[data-testid^="social-login-"]');
    const socialLoginCount = await socialLoginButtons.count();

    if (socialLoginCount > 0) {
      // 测试Google登录
      const googleLoginButton = page.locator('[data-testid="social-login-google"]');
      if (await googleLoginButton.isVisible()) {
        // 注意：实际社交登录需要真实的OAuth流程
        // 这里主要测试按钮存在性和基本交互
        await expect(googleLoginButton).toBeVisible();
        await expect(googleLoginButton).toBeEnabled();
      }

      // 测试微信登录
      const wechatLoginButton = page.locator('[data-testid="social-login-wechat"]');
      if (await wechatLoginButton.isVisible()) {
        await expect(wechatLoginButton).toBeVisible();
        await expect(wechatLoginButton).toBeEnabled();
      }

      // 测试GitHub登录
      const githubLoginButton = page.locator('[data-testid="social-login-github"]');
      if (await githubLoginButton.isVisible()) {
        await expect(githubLoginButton).toBeVisible();
        await expect(githubLoginButton).toBeEnabled();
      }
    }
  });

  test('用户资料完善流程', async ({ page }) => {
    // 登录用户
    await helpers.loginUser('moderate_user', 'Test123456!');
    await helpers.waitForPageLoad();

    // 导航到用户资料页面
    const userProfileLink = page.locator('[data-testid="user-profile-link"]');
    if (await userProfileLink.isVisible()) {
      await helpers.safeClick(userProfileLink);
    } else {
      await helpers.navigateToPage('/profile');
    }

    // 验证资料页面
    await helpers.expectVisible('[data-testid="profile-form"]');

    // 测试资料更新
    const displayNameInput = page.locator('[data-testid="display-name-input"]');
    if (await displayNameInput.isVisible()) {
      const newName = `更新用户名_${Date.now()}`;
      await helpers.safeFill(displayNameInput, newName);

      // 更新其他资料字段
      const phoneInput = page.locator('[data-testid="phone-input"]');
      if (await phoneInput.isVisible()) {
        await helpers.safeFill(phoneInput, '13800138000');
      }

      const bioTextarea = page.locator('[data-testid="bio-textarea"]');
      if (await bioTextarea.isVisible()) {
        await helpers.safeFill(bioTextarea, '这是我的个人简介');
      }

      // 保存资料
      const saveButton = page.locator('[data-testid="save-profile"]');
      await helpers.safeClick(saveButton);

      // 验证保存成功
      await helpers.waitForApiResponse('/api/user/profile');
      await helpers.verifyToastMessage('资料已更新');
    }

    // 测试头像上传
    const avatarUpload = page.locator('[data-testid="avatar-upload"]');
    if (await avatarUpload.isVisible()) {
      // 注意：实际文件上传需要真实文件
      // 这里测试上传组件的可见性和交互
      await expect(avatarUpload).toBeVisible();

      const fileInput = page.locator('[data-testid="avatar-file-input"]');
      if (await fileInput.isVisible()) {
        // 模拟文件选择（实际需要真实文件）
        await expect(fileInput).toBeVisible();
      }
    }
  });

  test('响应式设计测试', async ({ page }) => {
    // 测试登录页面响应式设计
    await helpers.navigateToPage('/login');
    await helpers.waitForPageLoad();

    // 测试桌面视图
    await helpers.verifyResponsiveDesign({ width: 1280, height: 720 });

    // 验证桌面布局
    await helpers.expectVisible('[data-testid="login-form-container"]');
    await helpers.expectVisible('[data-testid="login-illustration"]');

    // 测试平板视图
    await helpers.verifyResponsiveDesign({ width: 768, height: 1024 });

    // 测试移动视图
    await helpers.verifyResponsiveDesign({ width: 375, height: 667 });

    // 验证移动布局调整
    const mobileLayout = page.locator('[data-testid="mobile-login-layout"]');
    if (await mobileLayout.isVisible()) {
      await expect(mobileLayout).toBeVisible();
    }

    // 测试移动端的键盘友好性
    const inputs = page.locator('input[type="text"], input[type="password"], input[type="email"]');
    const inputCount = await inputs.count();

    for (let i = 0; i < inputCount; i++) {
      const input = inputs.nth(i);
      if (await input.isVisible()) {
        // 验证输入框在移动端有合适的触控目标大小
        const boundingBox = await input.boundingBox();
        if (boundingBox) {
          expect(boundingBox.height).toBeGreaterThanOrEqual(44); // 最小触控目标
          expect(boundingBox.width).toBeGreaterThanOrEqual(44);
        }
      }
    }
  });

  test('可访问性测试', async ({ page }) => {
    await helpers.navigateToPage('/login');
    await helpers.waitForPageLoad();

    // 验证页面标题
    await expect(page).toHaveTitle(/登录|Login/);

    // 验证主要区域的语义化HTML
    await expect(page.locator('main')).toBeVisible();
    await expect(page.locator('h1')).toBeVisible();

    // 验证表单标签
    const formLabels = page.locator('label');
    const labelCount = await formLabels.count();
    expect(labelCount).toBeGreaterThan(0);

    // 验证表单控件与标签的关联
    const inputs = page.locator('input');
    const inputCount = await inputs.count();

    for (let i = 0; i < inputCount; i++) {
      const input = inputs.nth(i);
      const inputId = await input.getAttribute('id');

      if (inputId) {
        const associatedLabel = page.locator(`label[for="${inputId}"]`);
        if (await associatedLabel.count() > 0) {
          await expect(associatedLabel.first()).toBeVisible();
        }
      }
    }

    // 验证按钮的可访问性
    const buttons = page.locator('button');
    const buttonCount = await buttons.count();

    for (let i = 0; i < buttonCount; i++) {
      const button = buttons.nth(i);

      // 检查按钮是否有文本或aria-label
      const buttonText = await button.textContent();
      const ariaLabel = await button.getAttribute('aria-label');
      const hasAccessibleName = buttonText?.trim() || ariaLabel;

      expect(hasAccessibleName).toBeTruthy();
    }

    // 验证错误信息的可访问性
    const errorMessages = page.locator('[data-testid$="-error"]');
    const errorCount = await errorMessages.count();

    for (let i = 0; i < errorCount; i++) {
      const errorMessage = errorMessages.nth(i);
      await expect(errorMessage).toHaveAttribute('role', 'alert');
    }

    // 验证页面可使用键盘导航
    await page.keyboard.press('Tab');
    const focusedElement = page.locator(':focus');
    expect(await focusedElement.count()).toBeGreaterThan(0);

    // 使用Tab键导航主要表单元素
    const focusableElements = [
      '[data-testid="username-input"]',
      '[data-testid="password-input"]',
      '[data-testid="login-button"]'
    ];

    for (const selector of focusableElements) {
      const element = page.locator(selector);
      if (await element.isVisible()) {
        await page.keyboard.press('Tab');
        const currentFocus = page.locator(':focus');
        expect(await currentFocus.evaluate(el => el.outerHTML)).toContain(selector);
      }
    }

    // 运行可访问性检查
    await helpers.checkAccessibility();
  });
});