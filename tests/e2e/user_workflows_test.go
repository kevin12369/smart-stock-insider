package e2e

import (
	"context"
	"fmt"
	"testing"
	"time"

	"github.com/chromedp/chromedp"
)

// TestUserWorkflow_CompletePortfolioManagement 测试完整的投资组合管理工作流
func TestUserWorkflow_CompletePortfolioManagement(t *testing.T) {
	// 创建上下文和取消函数
	ctx, cancel := chromedp.NewContext(context.Background())
	defer cancel()

	// 设置超时
	ctx, cancel = context.WithTimeout(ctx, 60*time.Second)
	defer cancel()

	// 启动浏览器（无头模式）
	allocator, err := chromedp.NewExecAllocator(ctx, append(chromedp.DefaultExecAllocatorOptions[:],
		chromedp.Flag("headless", true),
		chromedp.Flag("disable-gpu", true),
	)...)
	if err != nil {
		t.Fatalf("创建allocator失败: %v", err)
	}

	// 创建新的浏览器实例
	ctx, cancel = chromedp.NewContext(ctx, chromedp.WithAllocator(allocator))
	defer cancel()

	// 定义工作流步骤
	steps := []struct {
		name string
		tasks []chromedp.Action
	}{
		{
			name: "导航到投资组合页面",
			tasks: []chromedp.Action{
				chromedp.Navigate("http://localhost:3000/portfolio"),
				chromedp.WaitVisible(`//h1[contains(text(),'投资组合管理')]`, chromedp.ByQuery),
			},
		},
		{
			name: "创建新投资组合",
			tasks: []chromedp.Action{
				chromedp.Click(`//button[contains(text(),'创建组合')]`, chromedp.ByQuery),
				chromedp.WaitVisible(`//input[@placeholder='请输入组合名称']`, chromedp.ByQuery),
				chromedp.SendKeys(`//input[@placeholder='请输入组合名称']`, "E2E测试组合", chromedp.ByQuery),
				chromedp.SendKeys(`//textarea[@placeholder='请输入组合描述']`, "端到端测试创建的投资组合", chromedp.ByQuery),
				chromedp.Click(`//button[contains(text(),'确定')]`, chromedp.ByQuery),
				chromedp.WaitVisible(`//div[contains(text(),'投资组合创建成功')]`, chromedp.ByQuery),
			},
		},
		{
			name: "添加持仓",
			tasks: []chromedp.Action{
				chromedp.Click(`//button[contains(text(),'添加持仓')]`, chromedp.ByQuery),
				chromedp.WaitVisible(`//input[@placeholder='请输入股票代码']`, chromedp.ByQuery),
				chromedp.SendKeys(`//input[@placeholder='请输入股票代码']`, "000001", chromedp.ByQuery),
				chromedp.SendKeys(`//input[@placeholder='请输入股票名称']`, "平安银行", chromedp.ByQuery),
				chromedp.SendKeys(`//input[@placeholder='请输入买入数量']`, "1000", chromedp.ByQuery),
				chromedp.SendKeys(`//input[@placeholder='请输入成本价']`, "15.50", chromedp.ByQuery),
				chromedp.Click(`//button[contains(text(),'确定')]`, chromedp.ByQuery),
				chromedp.WaitVisible(`//div[contains(text(),'持仓添加成功')]`, chromedp.ByQuery),
			},
		},
		{
			name: "验证持仓显示",
			tasks: []chromedp.Action{
				chromedp.WaitVisible(`//td[contains(text(),'000001')]`, chromedp.ByQuery),
				chromedp.WaitVisible(`//td[contains(text(),'平安银行')]`, chromedp.ByQuery),
				chromedp.WaitVisible(`//td[contains(text(),'1000')]`, chromedp.ByQuery),
			},
		},
	}

	// 执行工作流步骤
	for _, step := range steps {
		t.Run(step.name, func(t *testing.T) {
			if err := chromedp.Run(ctx, step.tasks...); err != nil {
				t.Errorf("步骤 %s 失败: %v", step.name, err)
				return
			}
			t.Logf("步骤 %s 执行成功", step.name)
		})
	}
}

// TestUserWorkflow_NewsBrowsing 测试新闻浏览工作流
func TestUserWorkflow_NewsBrowsing(t *testing.T) {
	ctx, cancel := chromedp.NewContext(context.Background())
	defer cancel()

	ctx, cancel = context.WithTimeout(ctx, 45*time.Second)
	defer cancel()

	allocator, err := chromedp.NewExecAllocator(ctx, append(chromedp.DefaultExecAllocatorOptions[:],
		chromedp.Flag("headless", true),
	)...)
	if err != nil {
		t.Fatalf("创建allocator失败: %v", err)
	}

	ctx, cancel = chromedp.NewContext(ctx, chromedp.WithAllocator(allocator))
	defer cancel()

	// 新闻浏览工作流
	newsWorkflow := []chromedp.Action{
		// 1. 导航到新闻页面
		chromedp.Navigate("http://localhost:3000/news"),
		chromedp.WaitVisible(`//h1[contains(text(),'新闻中心')]`, chromedp.ByQuery),

		// 2. 等待新闻加载
		chromedp.WaitVisible(`//div[contains(@class,'ant-list-item')]`, chromedp.ByQuery),

		// 3. 搜索新闻
		chromedp.Click(`//input[@placeholder='搜索新闻标题、摘要或标签']`, chromedp.ByQuery),
		chromedp.SendKeys(`//input[@placeholder='搜索新闻标题、摘要或标签']`, "平安银行", chromedp.ByQuery),
		chromedp.Click(`//button[@aria-label='search']`, chromedp.ByQuery),

		// 4. 验证搜索结果
		chromedp.WaitVisible(`//div[contains(text(),'平安银行')]`, chromedp.ByQuery),

		// 5. 点击新闻详情
		chromedp.Click(`//button[contains(text(),'查看详情')]`, chromedp.ByQuery),
		chromedp.WaitVisible(`//div[contains(@class,'ant-modal')]`, chromedp.ByQuery),

		// 6. 关闭新闻详情
		chromedp.Click(`//button[contains(@aria-label,'Close')]`, chromedp.ByQuery),
	}

	if err := chromedp.Run(ctx, newsWorkflow...); err != nil {
		t.Errorf("新闻浏览工作流失败: %v", err)
	} else {
		t.Log("新闻浏览工作流执行成功")
	}
}

// TestUserWorkflow_DashboardNavigation 测试仪表盘导航工作流
func TestUserWorkflow_DashboardNavigation(t *testing.T) {
	ctx, cancel := chromedp.NewContext(context.Background())
	defer cancel()

	ctx, cancel = context.WithTimeout(ctx, 30*time.Second)
	defer cancel()

	allocator, err := chromedp.NewExecAllocator(ctx, append(chromedp.DefaultExecAllocatorOptions[:],
		chromedp.Flag("headless", true),
	)...)
	if err != nil {
		t.Fatalf("创建allocator失败: %v", err)
	}

	ctx, cancel = chromedp.NewContext(ctx, chromedp.WithAllocator(allocator))
	defer cancel()

	// 导航工作流
	navigationWorkflow := []chromedp.Action{
		// 1. 导航到首页
		chromedp.Navigate("http://localhost:3000"),
		chromedp.WaitVisible(`//h1[contains(text(),'智股通控制台')]`, chromedp.ByQuery),

		// 2. 验证页面元素
		chromedp.WaitVisible(`//div[contains(text(),'投资组合总值')]`, chromedp.ByQuery),
		chromedp.WaitVisible(`//div[contains(text(),'市场概览')]`, chromedp.ByQuery),
		chromedp.WaitVisible(`//div[contains(text(),'最新财经要闻')]`, chromedp.ByQuery),

		// 3. 测试侧边栏导航
		chromedp.Click(`//li[contains(.,'投资组合')]`, chromedp.ByQuery),
		chromedp.WaitVisible(`//h1[contains(text(),'投资组合管理')]`, chromedp.ByQuery),

		// 4. 导航到新闻中心
		chromedp.Click(`//li[contains(.,'新闻中心')]`, chromedp.ByQuery),
		chromedp.WaitVisible(`//h1[contains(text(),'新闻中心')]`, chromedp.ByQuery),

		// 5. 导航到推送通知
		chromedp.Click(`//li[contains(.,'推送通知')]`, chromedp.ByQuery),
		chromedp.WaitVisible(`//h1[contains(text(),'推送通知中心')]`, chromedp.ByQuery),

		// 6. 返回首页
		chromedp.Click(`//li[contains(.,'仪表盘')]`, chromedp.ByQuery),
		chromedp.WaitVisible(`//h1[contains(text(),'智股通控制台')]`, chromedp.ByQuery),
	}

	if err := chromedp.Run(ctx, navigationWorkflow...); err != nil {
		t.Errorf("导航工作流失败: %v", err)
	} else {
		t.Log("导航工作流执行成功")
	}
}

// TestUserWorkflow_ErrorHandling 测试错误处理工作流
func TestUserWorkflow_ErrorHandling(t *testing.T) {
	ctx, cancel := chromedp.NewContext(context.Background())
	defer cancel()

	ctx, cancel = context.WithTimeout(ctx, 30*time.Second)
	defer cancel()

	allocator, err := chromedp.NewExecAllocator(ctx, append(chromedp.DefaultExecAllocatorOptions[:],
		chromedp.Flag("headless", true),
	)...)
	if err != nil {
		t.Fatalf("创建allocator失败: %v", err)
	}

	ctx, cancel = chromedp.NewContext(ctx, chromedp.WithAllocator(allocator))
	defer cancel()

	// 错误处理测试工作流
	errorHandlingWorkflow := []chromedp.Action{
		// 1. 导航到投资组合页面
		chromedp.Navigate("http://localhost:3000/portfolio"),
		chromedp.WaitVisible(`//h1[contains(text(),'投资组合管理')]`, chromedp.ByQuery),

		// 2. 尝试创建无效的投资组合（空名称）
		chromedp.Click(`//button[contains(text(),'创建组合')]`, chromedp.ByQuery),
		chromedp.WaitVisible(`//input[@placeholder='请输入组合名称']`, chromedp.ByQuery),
		chromedp.Click(`//button[contains(text(),'确定')]`, chromedp.ByQuery),

		// 3. 验证错误提示
		chromedp.WaitVisible(`//div[contains(text(),'请输入组合名称')]`, chromedp.ByQuery),

		// 4. 关闭错误提示
		chromedp.Click(`//button[contains(@aria-label,'Close')]`, chromedp.ByQuery),

		// 5. 尝试添加无效持仓（空股票代码）
		chromedp.Click(`//button[contains(text(),'添加持仓')]`, chromedp.ByQuery),
		chromedp.WaitVisible(`//input[@placeholder='请输入股票代码']`, chromedp.ByQuery),
		chromedp.Click(`//button[contains(text(),'确定')]`, chromedp.ByQuery),

		// 6. 验证错误提示
		chromedp.WaitVisible(`//div[contains(text(),'请输入股票代码')]`, chromedp.ByQuery),
	}

	if err := chromedp.Run(ctx, errorHandlingWorkflow...); err != nil {
		t.Errorf("错误处理工作流失败: %v", err)
	} else {
		t.Log("错误处理工作流执行成功")
	}
}

// TestUserWorkflow_Performance 测试性能工作流
func TestUserWorkflow_Performance(t *testing.T) {
	ctx, cancel := chromedp.NewContext(context.Background())
	defer cancel()

	ctx, cancel = context.WithTimeout(ctx, 30*time.Second)
	defer cancel()

	allocator, err := chromedp.NewExecAllocator(ctx, append(chromedp.DefaultExecAllocatorOptions[:],
		chromedp.Flag("headless", true),
		chromedp.Flag("disable-gpu", true),
	)...)
	if err != nil {
		t.Fatalf("创建allocator失败: %v", err)
	}

	ctx, cancel = chromedp.NewContext(ctx, chromedp.WithAllocator(allocator))
	defer cancel()

	// 性能测试
	var startTime, loadTime, navigationTime time.Duration

	performanceWorkflow := []chromedp.Action{
		// 记录导航开始时间
		chromedp.ActionFunc(func(ctx context.Context) error {
			startTime = time.Now()
			return nil
		}),

		// 导航到页面
		chromedp.Navigate("http://localhost:3000/enhanced-dashboard"),
		chromedp.WaitVisible(`//h1[contains(text(),'智股通控制台')]`, chromedp.ByQuery),

		// 记录加载时间
		chromedp.ActionFunc(func(ctx context.Context) error {
			loadTime = time.Since(startTime)
			return nil
		}),

		// 测试快速导航
		chromedp.ActionFunc(func(ctx context.Context) error {
			startTime = time.Now()
			return nil
		}),
		chromedp.Click(`//li[contains(.,'投资组合')]`, chromedp.ByQuery),
		chromedp.WaitVisible(`//h1[contains(text(),'投资组合管理')]`, chromedp.ByQuery),
		chromedp.ActionFunc(func(ctx context.Context) error {
			navigationTime = time.Since(startTime)
			return nil
		}),

		// 记录性能指标
		chromedp.ActionFunc(func(ctx context.Context) error {
			t.Logf("页面加载时间: %v", loadTime)
			t.Logf("导航响应时间: %v", navigationTime)

			// 性能断言
			if loadTime > 5*time.Second {
				t.Errorf("页面加载时间过长: %v", loadTime)
			}

			if navigationTime > 2*time.Second {
				t.Errorf("导航响应时间过长: %v", navigationTime)
			}

			return nil
		}),
	}

	if err := chromedp.Run(ctx, performanceWorkflow...); err != nil {
		t.Errorf("性能工作流失败: %v", err)
	} else {
		t.Log("性能工作流执行成功")
	}
}

// TestUserWorkflow_DataPersistence 测试数据持久化工作流
func TestUserWorkflow_DataPersistence(t *testing.T) {
	ctx, cancel := chromedp.NewContext(context.Background())
	defer cancel()

	ctx, cancel = context.WithTimeout(ctx, 45*time.Second)
	defer cancel()

	allocator, err := chromedp.NewExecAllocator(ctx, append(chromedp.DefaultExecAllocatorOptions[:],
		chromedp.Flag("headless", true),
	)...)
	if err != nil {
		t.Fatalf("创建allocator失败: %v", err)
	}

	ctx, cancel = chromedp.NewContext(ctx, chromedp.WithAllocator(allocator))
	defer cancel()

	// 数据持久化测试
	persistenceWorkflow := []chromedp.Action{
		// 1. 导航到投资组合页面
		chromedp.Navigate("http://localhost:3000/portfolio"),
		chromedp.WaitVisible(`//h1[contains(text(),'投资组合管理')]`, chromedp.ByQuery),

		// 2. 创建测试投资组合
		chromedp.Click(`//button[contains(text(),'创建组合')]`, chromedp.ByQuery),
		chromedp.WaitVisible(`//input[@placeholder='请输入组合名称']`, chromedp.ByQuery),
		chromedp.SendKeys(`//input[@placeholder='请输入组合名称']`, "持久化测试组合", chromedp.ByQuery),
		chromedp.SendKeys(`//textarea[@placeholder='请输入组合描述']`, "测试数据持久化功能", chromedp.ByQuery),
		chromedp.Click(`//button[contains(text(),'确定')]`, chromedp.ByQuery),
		chromedp.WaitVisible(`//div[contains(text(),'投资组合创建成功')]`, chromedp.ByQuery),

		// 3. 刷新页面
		chromedp.Reload(),
		chromedp.WaitVisible(`//h1[contains(text(),'投资组合管理')]`, chromedp.ByQuery),

		// 4. 验证数据持久化
		chromedp.WaitVisible(`//td[contains(text(),'持久化测试组合')]`, chromedp.ByQuery),

		// 5. 清理测试数据（在实际测试中可能需要API调用）
		chromedp.Click(`//button[contains(text(),'删除')]`, chromedp.ByQuery),
		chromedp.Click(`//button[contains(text(),'确定')]`, chromedp.ByQuery),
	}

	if err := chromedp.Run(ctx, persistenceWorkflow...); err != nil {
		t.Errorf("数据持久化工作流失败: %v", err)
	} else {
		t.Log("数据持久化工作流执行成功")
	}
}