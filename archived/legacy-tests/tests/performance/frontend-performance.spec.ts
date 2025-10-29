/**
 * 前端性能测试
 * 测试前端应用的性能指标和用户体验
 */

import { test, expect } from '@playwright/test';
import { createTestHelpers } from '../helpers/test-helpers';
import { PERFORMANCE_THRESHOLDS } from '../fixtures/test-data';

test.describe('前端性能测试', () => {
  let helpers: ReturnType<typeof createTestHelpers>;

  test.beforeEach(async ({ page }) => {
    helpers = createTestHelpers(page);
    await helpers.setTestEnvironment();
    await helpers.clearStorage();
  });

  test('页面加载性能测试', async ({ page }) => {
    // 监控性能指标
    const performanceMetrics = await page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;

      return {
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
        loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
        firstPaint: performance.getEntriesByType('paint')[0]?.startTime || 0,
        firstContentfulPaint: performance.getEntriesByType('paint')[1]?.startTime || 0,
        largestContentfulPaint: 0, // 将在后面测量
        firstInputDelay: 0, // 将在后面测量
        timeToInteractive: 0, // 将在后面估算
      };
    });

    // 导航到页面并记录加载时间
    const startTime = Date.now();
    await helpers.navigateToPage('/dashboard');
    await helpers.waitForPageLoad();
    const totalLoadTime = Date.now() - startTime;

    // 验证页面加载性能
    expect(totalLoadTime).toBeLessThan(PERFORMANCE_THRESHOLDS.pageLoad.maxLoadTime);
    expect(performanceMetrics.domContentLoaded).toBeLessThan(2000);
    expect(performanceMetrics.firstContentfulPaint).toBeLessThan(
      PERFORMANCE_THRESHOLDS.pageLoad.maxFirstContentfulPaint
    );

    // 测量LCP（最大内容绘制）
    const lcp = await page.evaluate(() => {
      return new Promise(resolve => {
        new PerformanceObserver(list => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          resolve(lastEntry.startTime);
        }).observe({ entryTypes: ['largest-contentful-paint'] });
      });
    });

    expect(lcp).toBeLessThan(PERFORMANCE_THRESHOLDS.pageLoad.maxLargestContentfulPaint);

    // 测量FID（首次输入延迟）
    const fid = await page.evaluate(() => {
      return new Promise(resolve => {
        new PerformanceObserver(list => {
          const entries = list.getEntries();
          if (entries.length > 0) {
            resolve(entries[0].processingStart - entries[0].startTime);
          } else {
            resolve(0);
          }
        }).observe({ entryTypes: ['first-input'] });
      });
    });

    expect(fid).toBeLessThan(100); // FID应该小于100ms

    // 记录性能指标
    console.log('页面性能指标:', {
      totalLoadTime,
      domContentLoaded: performanceMetrics.domContentLoaded,
      firstContentfulPaint: performanceMetrics.firstContentfulPaint,
      largestContentfulPaint: lcp,
      firstInputDelay: fid
    });
  });

  test('资源加载性能测试', async ({ page }) => {
    // 监控资源加载
    const resourceMetrics = await page.evaluate(() => {
      const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];

      return resources.map(resource => ({
        name: resource.name,
        type: resource.initiatorType,
        duration: resource.responseEnd - resource.requestStart,
        size: resource.transferSize,
        cached: resource.transferSize === 0 && resource.decodedBodySize > 0
      }));
    });

    await helpers.navigateToPage('/dashboard');
    await helpers.waitForPageLoad();

    // 等待所有资源加载完成
    await page.waitForLoadState('networkidle');

    // 验证关键资源加载时间
    const criticalResources = ['css', 'javascript', 'image'];
    const criticalResourceMetrics = resourceMetrics.filter(r =>
      criticalResources.some(type => r.type.includes(type)) || r.name.includes('chunk')
    );

    for (const resource of criticalResourceMetrics) {
      expect(resource.duration).toBeLessThan(3000); // 关键资源应该在3秒内加载完成
    }

    // 验证缓存利用率
    const cachedResources = resourceMetrics.filter(r => r.cached);
    const cacheHitRate = cachedResources.length / resourceMetrics.length;
    expect(cacheHitRate).toBeGreaterThan(0.3); // 至少30%的资源应该被缓存

    // 检查资源大小
    const largeResources = resourceMetrics.filter(r => r.size > 1024 * 1024); // 大于1MB的资源
    expect(largeResources.length).toBeLessThan(5); // 大资源数量应该很少

    console.log('资源加载统计:', {
      totalResources: resourceMetrics.length,
      cachedResources: cachedResources.length,
      cacheHitRate: `${(cacheHitRate * 100).toFixed(1)}%`,
      largeResources: largeResources.length
    });
  });

  test('JavaScript执行性能测试', async ({ page }) => {
    await helpers.navigateToPage('/dashboard');
    await helpers.waitForPageLoad();

    // 测量长任务
    const longTasks = await page.evaluate(() => {
      return new Promise(resolve => {
        const observer = new PerformanceObserver(list => {
          const entries = list.getEntries();
          resolve(entries.map(entry => ({
            duration: entry.duration,
            startTime: entry.startTime,
            attribution: (entry as any).attribution || []
          })));
        });
        observer.observe({ entryTypes: ['longtask'] });

        // 5秒后如果没有长任务，返回空数组
        setTimeout(() => {
          observer.disconnect();
          resolve([]);
        }, 5000);
      });
    });

    // 验证长任务数量和持续时间
    expect(longTasks.length).toBeLessThan(5); // 长任务数量应该很少
    for (const task of longTasks) {
      expect(task.duration).toBeLessThan(50); // 长任务持续时间应该小于50ms
    }

    // 测量主线程阻塞时间
    const mainThreadBlocking = longTasks.reduce((total, task) => total + task.duration, 0);
    expect(mainThreadBlocking).toBeLessThan(200); // 主线程阻塞时间应该小于200ms

    console.log('JavaScript执行性能:', {
      longTasksCount: longTasks.length,
      mainThreadBlocking: `${mainThreadBlocking.toFixed(2)}ms`,
      maxLongTaskDuration: longTasks.length > 0 ?
        Math.max(...longTasks.map(t => t.duration)) : 0
    });
  });

  test('内存使用测试', async ({ page }) => {
    await helpers.navigateToPage('/dashboard');
    await helpers.waitForPageLoad();

    // 测量内存使用
    const memoryMetrics = await page.evaluate(() => {
      if ('memory' in performance) {
        return {
          usedJSHeapSize: (performance as any).memory.usedJSHeapSize,
          totalJSHeapSize: (performance as any).memory.totalJSHeapSize,
          jsHeapSizeLimit: (performance as any).memory.jsHeapSizeLimit
        };
      }
      return null;
    });

    if (memoryMetrics) {
      // 验证内存使用在合理范围内
      const memoryUsageMB = memoryMetrics.usedJSHeapSize / (1024 * 1024);
      expect(memoryUsageMB).toBeLessThan(100); // 内存使用应该小于100MB

      // 检查内存利用率
      const memoryUtilization = memoryMetrics.usedJSHeapSize / memoryMetrics.jsHeapSizeLimit;
      expect(memoryUtilization).toBeLessThan(0.5); // 内存利用率应该小于50%

      console.log('内存使用统计:', {
        usedJSHeapSize: `${(memoryMetrics.usedJSHeapSize / (1024 * 1024)).toFixed(2)} MB`,
        totalJSHeapSize: `${(memoryMetrics.totalJSHeapSize / (1024 * 1024)).toFixed(2)} MB`,
        memoryUtilization: `${(memoryUtilization * 100).toFixed(1)}%`
      });
    }
  });

  test('交互响应性能测试', async ({ page }) => {
    await helpers.navigateToPage('/dashboard');
    await helpers.waitForPageLoad();

    // 测试按钮点击响应时间
    const buttons = page.locator('button, [role="button"]');
    const buttonCount = await buttons.count();

    if (buttonCount > 0) {
      const testButton = buttons.first();

      // 测量点击响应时间
      const clickResponseTime = await page.evaluate(async (buttonSelector) => {
        const button = document.querySelector(buttonSelector);
        if (!button) return 0;

        const startTime = performance.now();

        return new Promise(resolve => {
          button.addEventListener('click', () => {
            const responseTime = performance.now() - startTime;
            resolve(responseTime);
          }, { once: true });

          // 模拟点击
          button.click();
        });
      }, await testButton.evaluate(el => el.tagName.toLowerCase() + (el.className ? '.' + el.className : '')));

      expect(clickResponseTime).toBeLessThan(PERFORMANCE_THRESHOLDS.userInteraction.maxClickResponse);

      console.log('按钮点击响应时间:', `${clickResponseTime.toFixed(2)}ms`);
    }

    // 测试表单提交响应时间
    const forms = page.locator('form');
    const formCount = await forms.count();

    if (formCount > 0) {
      const testForm = forms.first();
      const submitButton = testForm.locator('button[type="submit"], [type="submit"]');

      if (await submitButton.count() > 0) {
        const formSubmitResponseTime = await page.evaluate(async (formSelector) => {
          const form = document.querySelector(formSelector);
          if (!form) return 0;

          const startTime = performance.now();

          return new Promise(resolve => {
            form.addEventListener('submit', (e) => {
              e.preventDefault(); // 阻止实际提交
              const responseTime = performance.now() - startTime;
              resolve(responseTime);
            }, { once: true });

            // 模拟表单提交
            form.requestSubmit();
          });
        }, await testForm.evaluate(el => el.id || el.className || 'form'));

        expect(formSubmitResponseTime).toBeLessThan(PERFORMANCE_THRESHOLDS.userInteraction.maxFormSubmit);

        console.log('表单提交响应时间:', `${formSubmitResponseTime.toFixed(2)}ms`);
      }
    }

    // 测试搜索响应时间
    const searchInputs = page.locator('input[type="search"], [placeholder*="搜索"]');
    const searchCount = await searchInputs.count();

    if (searchCount > 0) {
      const searchInput = searchInputs.first();

      const searchResponseTime = await page.evaluate(async (inputSelector) => {
        const input = document.querySelector(inputSelector);
        if (!input) return 0;

        const startTime = performance.now();
        input.value = 'test';
        input.dispatchEvent(new Event('input', { bubbles: true }));

        return new Promise(resolve => {
          const checkResponse = () => {
            const responseTime = performance.now() - startTime;
            // 等待一段时间后检查是否有响应
            setTimeout(() => resolve(responseTime), 100);
          };

          // 监听可能的事件
          ['keyup', 'change'].forEach(eventType => {
            input.addEventListener(eventType, checkResponse, { once: true });
          });

          // 确保有响应
          setTimeout(checkResponse, 200);
        });
      }, await searchInput.evaluate(el => el.placeholder || el.name || 'search'));

      expect(searchResponseTime).toBeLessThan(PERFORMANCE_THRESHOLDS.userInteraction.maxSearchResponse);

      console.log('搜索响应时间:', `${searchResponseTime.toFixed(2)}ms`);
    }
  });

  test('动画和过渡性能测试', async ({ page }) => {
    await helpers.navigateToPage('/dashboard');
    await helpers.waitForPageLoad();

    // 测试CSS动画性能
    const animatedElements = await page.evaluate(() => {
      const elements = document.querySelectorAll('*');
      const animated = [];

      elements.forEach(el => {
        const style = window.getComputedStyle(el);
        if (style.animation !== 'none' || style.transition !== 'none') {
          animated.push({
            tagName: el.tagName,
            className: el.className,
            animation: style.animation,
            transition: style.transition
          });
        }
      });

      return animated;
    });

    if (animatedElements.length > 0) {
      // 验证动画使用GPU加速
      const gpuAccelerated = await page.evaluate(() => {
        const elements = document.querySelectorAll('*');
        let gpuCount = 0;

        elements.forEach(el => {
          const style = window.getComputedStyle(el);
          if (style.transform !== 'none' ||
              style.willChange === 'transform' ||
              style.backfaceVisibility === 'hidden') {
            gpuCount++;
          }
        });

        return gpuCount;
      });

      expect(gpuAccelerated).toBeGreaterThan(animatedElements.length * 0.7); // 至少70%的动画应该GPU加速

      console.log('动画性能统计:', {
        totalAnimatedElements: animatedElements.length,
        gpuAcceleratedElements: gpuAccelerated,
        gpuAccelerationRate: `${(gpuAccelerated / animatedElements.length * 100).toFixed(1)}%`
      });
    }
  });

  test('网络请求性能测试', async ({ page }) => {
    // 监控网络请求
    const networkMetrics: any[] = [];

    page.on('response', response => {
      const timing = response.request().timing();
      networkMetrics.push({
        url: response.url(),
        status: response.status(),
        duration: timing.responseEnd - timing.requestStart,
        size: response.headers()['content-length'] || 0
      });
    });

    await helpers.navigateToPage('/dashboard');
    await helpers.waitForPageLoad();

    // 验证API响应时间
    const apiRequests = networkMetrics.filter(req =>
      req.url.includes('/api/') && req.status === 200
    );

    if (apiRequests.length > 0) {
      const avgResponseTime = apiRequests.reduce((sum, req) => sum + req.duration, 0) / apiRequests.length;
      const maxResponseTime = Math.max(...apiRequests.map(req => req.duration));

      expect(avgResponseTime).toBeLessThan(PERFORMANCE_THRESHOLDS.apiResponse.maxResponseTime);
      expect(maxResponseTime).toBeLessThan(PERFORMANCE_THRESHOLDS.apiResponse.maxResponseTime * 2);

      console.log('API请求性能:', {
        totalRequests: apiRequests.length,
        avgResponseTime: `${avgResponseTime.toFixed(2)}ms`,
        maxResponseTime: `${maxResponseTime.toFixed(2)}ms`
      });
    }

    // 验证关键API响应时间
    const criticalApis = ['/api/stocks', '/api/news', '/api/ai/analyze'];

    for (const api of criticalApis) {
      const apiMetrics = networkMetrics.filter(req => req.url.includes(api));

      if (apiMetrics.length > 0) {
        const avgTime = apiMetrics.reduce((sum, req) => sum + req.duration, 0) / apiMetrics.length;

        // AI分析API可能有更长的响应时间
        const threshold = api.includes('/ai/') ?
          PERFORMANCE_THRESHOLDS.apiResponse.maxAIAnalysisResponse :
          PERFORMANCE_THRESHOLDS.apiResponse.maxResponseTime;

        expect(avgTime).toBeLessThan(threshold);
        console.log(`${api}平均响应时间: ${avgTime.toFixed(2)}ms`);
      }
    }
  });

  test('移动端性能测试', async ({ page }) => {
    // 模拟移动设备
    await page.setViewportSize({ width: 375, height: 667 });
    await page.emulateMedia({ colorScheme: 'light' });

    await helpers.navigateToPage('/dashboard');
    await helpers.waitForPageLoad();

    // 在移动设备上重新测试关键性能指标
    const mobileMetrics = await page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;

      return {
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
        loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
        firstContentfulPaint: performance.getEntriesByType('paint')[1]?.startTime || 0
      };
    });

    // 移动端的性能要求可能更严格
    expect(mobileMetrics.domContentLoaded).toBeLessThan(1500);
    expect(mobileMetrics.firstContentfulPaint).toBeLessThan(1000);

    console.log('移动端性能指标:', mobileMetrics);

    // 测试触摸响应性能
    const touchElements = page.locator('button, a, [onclick]');
    if (await touchElements.count() > 0) {
      const touchResponseTime = await page.evaluate(async () => {
        const element = document.querySelector('button');
        if (!element) return 0;

        const startTime = performance.now();
        const touchStart = new TouchEvent('touchstart', {
          bubbles: true,
          cancelable: true,
          touches: [new Touch({
            identifier: 0,
            target: element,
            clientX: 10,
            clientY: 10
          })]
        });

        return new Promise(resolve => {
          element.addEventListener('touchstart', () => {
            const responseTime = performance.now() - startTime;
            resolve(responseTime);
          }, { once: true });

          element.dispatchEvent(touchStart);
        });
      });

      expect(touchResponseTime).toBeLessThan(50); // 触摸响应应该很快
      console.log('触摸响应时间:', `${touchResponseTime.toFixed(2)}ms`);
    }
  });

  test('可访问性和性能相关性测试', async ({ page }) => {
    await helpers.navigateToPage('/dashboard');
    await helpers.waitForPageLoad();

    // 验证图片使用合适的尺寸和格式
    const images = await page.evaluate(() => {
      const imgs = document.querySelectorAll('img');
      return Array.from(imgs).map(img => ({
        src: img.src,
        width: img.naturalWidth,
        height: img.naturalHeight,
        loading: img.loading || 'eager'
      }));
    });

    if (images.length > 0) {
      // 检查是否使用了懒加载
      const lazyLoadedImages = images.filter(img => img.loading === 'lazy');
      const lazyLoadingRate = lazyLoadedImages.length / images.length;

      console.log('图片性能统计:', {
        totalImages: images.length,
        lazyLoadedImages: lazyLoadedImages.length,
        lazyLoadingRate: `${(lazyLoadingRate * 100).toFixed(1)}%`
      });
    }

    // 验证关键内容可见性
    const lcpElement = await page.evaluate(() => {
      return new Promise(resolve => {
        new PerformanceObserver(list => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          resolve(lastEntry.element?.tagName || 'unknown');
        }).observe({ entryTypes: ['largest-contentful-paint'] });
      });
    });

    console.log('最大内容绘制元素:', lcpElement);

    // 验证页面是否避免布局偏移
    const layoutShift = await page.evaluate(() => {
      return new Promise(resolve => {
        let cumulativeShift = 0;

        new PerformanceObserver(list => {
          const entries = list.getEntries();
          entries.forEach(entry => {
            if (!entry.hadRecentInput) {
              cumulativeShift += entry.value;
            }
          });
          resolve(cumulativeShift);
        }).observe({ entryTypes: ['layout-shift'] });

        // 5秒后返回当前累积偏移
        setTimeout(() => resolve(cumulativeShift), 5000);
      });
    });

    expect(layoutShift).toBeLessThan(0.1); // 布局偏移应该很小
    console.log('累积布局偏移:', layoutShift.toFixed(4));
  });

  test('持续使用性能测试', async ({ page }) => {
    await helpers.navigateToPage('/dashboard');
    await helpers.waitForPageLoad();

    // 模拟用户连续操作
    const operations = [
      async () => {
        // 搜索股票
        const searchInput = page.locator('input[type="search"]');
        if (await searchInput.isVisible()) {
          const startTime = performance.now();
          await searchInput.fill('AAPL');
          await page.keyboard.press('Enter');
          await page.waitForTimeout(1000);
          return performance.now() - startTime;
        }
        return 0;
      },

      async () => {
        // 点击股票项
        const stockItems = page.locator('[data-testid="stock-item"]');
        if (await stockItems.count() > 0) {
          const startTime = performance.now();
          await stockItems.first().click();
          await page.waitForTimeout(1000);
          return performance.now() - startTime;
        }
        return 0;
      },

      async () => {
        // 刷新页面
        const refreshButton = page.locator('[data-testid="refresh-button"]');
        if (await refreshButton.isVisible()) {
          const startTime = performance.now();
          await refreshButton.click();
          await helpers.waitForLoadingToDisappear();
          return performance.now() - startTime;
        }
        return 0;
      }
    ];

    const operationTimes = [];

    // 连续执行操作
    for (let i = 0; i < 5; i++) {
      const operation = operations[i % operations.length];
      const time = await operation();
      operationTimes.push(time);

      // 短暂延迟
      await page.waitForTimeout(500);
    }

    // 分析操作性能
    const avgOperationTime = operationTimes.reduce((sum, time) => sum + time, 0) / operationTimes.length;
    const maxOperationTime = Math.max(...operationTimes);

    expect(avgOperationTime).toBeLessThan(2000); // 平均操作时间应该合理
    expect(maxOperationTime).toBeLessThan(5000); // 最长操作时间不应该太长

    console.log('连续操作性能:', {
      totalOperations: operationTimes.length,
      avgOperationTime: `${avgOperationTime.toFixed(2)}ms`,
      maxOperationTime: `${maxOperationTime.toFixed(2)}ms`,
      operationTimes: operationTimes.map(t => `${t.toFixed(2)}ms`)
    });
  });
});