package services

import (
	"fmt"
	"os"
	"testing"
)

// TestMain 测试主入口
func TestMain(m *testing.M) {
	fmt.Println("🤖 AI助手系统测试套件")
	fmt.Println("智股通 (Smart Stock Insider)")
	fmt.Println("Version: 1.0.0")
	fmt.Println("Author: AI Assistant System Team")
	fmt.Println()

	// 运行所有测试
	fmt.Println("🧪 开始执行单元测试...")
	code := m.Run()

	// 运行性能测试（如果单元测试通过）
	if code == 0 {
		fmt.Println("\n" + "="*60)
		RunPerformanceTests()

		fmt.Println("\n" + "="*60)
		RunStressTest()

		fmt.Println("\n" + "="*60)
		// 运行完整测试套件
		report, err := RunAllTests()
		if err != nil {
			fmt.Printf("❌ 运行完整测试套件失败: %v\n", err)
			code = 1
		} else {
			// 根据测试结果设置退出码
			if report.PassRate < 0.8 {
				fmt.Println("❌ 测试通过率过低，系统需要优化")
				code = 1
			} else {
				fmt.Println("✅ 所有测试通过，系统运行良好")
			}
		}
	}

	// 退出
	os.Exit(code)
}

// 运行特定测试的便捷函数
func RunAIAssistantSystemTests(t *testing.T) {
	t.Run("AIAssistantSystem", func(t *testing.T) {
		TestAIAssistantSystemCreation(t)
		TestIndividualAssistantTesting(t)
		TestCollaborativeAnalysis(t)
		TestSessionManagement(t)
		TestKnowledgeBase(t)
		TestErrorHandling(t)
		TestConcurrentRequests(t)
	})
}

func RunAIIntegrationTests(t *testing.T) {
	t.Run("AIIntegration", func(t *testing.T) {
		TestAIIntegrationServiceCreation(t)
		TestComprehensiveAnalysis(t)
		TestMultiStockAnalysis(t)
		TestRealTimeAnalysis(t)
		TestCustomizedAnalysis(t)
		TestBatchAnalysis(t)
		TestIntegrationHealthCheck(t)
		TestIntegrationCaching(t)
		TestErrorRecovery(t)
		TestIntegrationConcurrency(t)
	})
}

func RunAIAnalysisServiceTests(t *testing.T) {
	t.Run("AIAnalysisService", func(t *testing.T) {
		TestAIAnalysisServiceCreation(t)
		TestTechnicalAnalysis(t)
		TestFundamentalAnalysis(t)
		TestNewsAnalysis(t)
		TestPortfolioAnalysis(t)
		TestGetCapabilities(t)
		TestErrorHandling(t)
		TestTimeoutHandling(t)
		TestConcurrentRequests(t)
		TestServiceHealthCheck(t)
	})
}

// TestAllGroups 运行所有测试组
func TestAllGroups(t *testing.T) {
	t.Run("CompleteTestSuite", func(t *testing.T) {
		t.Run("AIAssistantSystem", RunAIAssistantSystemTests)
		t.Run("AIIntegration", RunAIIntegrationTests)
		t.Run("AIAnalysisService", RunAIAnalysisServiceTests)
	})
}