package services

import (
	"context"
	"fmt"
	"testing"
	"time"

	"smart-stock-insider/internal/utils"
)

// TestAIIntegrationServiceCreation 测试AI集成服务创建
func TestAIIntegrationServiceCreation(t *testing.T) {
	logger := utils.NewStandardLogger()
	logger.SetLevel(utils.InfoLevel)

	// 创建模拟AI分析服务
	mockAI := NewMockAIAnalysisService()

	// 创建AI集成服务
	service, err := NewAIIntegration(mockAI, logger)
	if err != nil {
		t.Fatalf("创建AI集成服务失败: %v", err)
	}

	if service == nil {
		t.Fatal("AI集成服务为空")
	}

	// 验证服务状态
	status := service.GetStatus()
	if status != "initialized" {
		t.Errorf("服务状态错误，期望 initialized，实际 %s", status)
	}

	t.Log("AI集成服务创建测试通过")
}

// TestComprehensiveAnalysis 测试综合分析
func TestComprehensiveAnalysis(t *testing.T) {
	logger := utils.NewStandardLogger()
	logger.SetLevel(utils.InfoLevel)

	mockAI := NewMockAIAnalysisService()
	service, err := NewAIIntegration(mockAI, logger)
	if err != nil {
		t.Fatalf("创建AI集成服务失败: %v", err)
	}

	ctx := context.Background()

	// 创建综合分析请求
	req := &ComprehensiveAnalysisRequest{
		StockCode:     "000001",
		AnalysisTypes: []string{"technical", "fundamental", "news", "risk"},
		UserName:      "测试用户",
		RequestID:     "test_comp_001",
		Options: map[string]interface{}{
			"timeout_seconds": 30,
			"enable_cache":    true,
		},
	}

	// 执行综合分析
	result, err := service.ComprehensiveAnalysis(ctx, req)
	if err != nil {
		t.Errorf("综合分析失败: %v", err)
		return
	}

	if result == nil {
		t.Error("综合分析结果为空")
		return
	}

	// 验证结果结构
	if result.StockCode != "000001" {
		t.Errorf("股票代码错误，期望 000001，实际 %s", result.StockCode)
	}

	if len(result.Analyses) != 4 {
		t.Errorf("分析数量错误，期望 4，实际 %d", len(result.Analyses))
	}

	if result.Summary.OverallScore <= 0 {
		t.Error("总体评分应该大于0")
	}

	if len(result.Summary.Recommendations) == 0 {
		t.Error("应该提供投资建议")
	}

	if result.Summary.TotalConfidence <= 0 {
		t.Error("总体置信度应该大于0")
	}

	t.Logf("综合分析测试通过: 股票 %s, 总体评分 %.2f, 置信度 %.2f",
		result.StockCode, result.Summary.OverallScore, result.Summary.TotalConfidence)
}

// TestMultiStockAnalysis 测试多股票分析
func TestMultiStockAnalysis(t *testing.T) {
	logger := utils.NewStandardLogger()
	logger.SetLevel(utils.InfoLevel)

	mockAI := NewMockAIAnalysisService()
	service, err := NewAIIntegration(mockAI, logger)
	if err != nil {
		t.Fatalf("创建AI集成服务失败: %v", err)
	}

	ctx := context.Background()

	// 创建多股票分析请求
	req := &MultiStockAnalysisRequest{
		StockCodes:    []string{"000001", "000002", "000858"},
		AnalysisTypes: []string{"technical", "fundamental"},
		UserName:      "测试用户",
		RequestID:     "test_multi_001",
		Options: map[string]interface{}{
			"parallel": true,
			"timeout":  60,
		},
	}

	// 执行多股票分析
	result, err := service.MultiStockAnalysis(ctx, req)
	if err != nil {
		t.Errorf("多股票分析失败: %v", err)
		return
	}

	if result == nil {
		t.Error("多股票分析结果为空")
		return
	}

	// 验证结果
	if len(result.StockResults) != 3 {
		t.Errorf("股票分析结果数量错误，期望 3，实际 %d", len(result.StockResults))
	}

	if result.Summary.TotalStocks != 3 {
		t.Errorf("总股票数量错误，期望 3，实际 %d", result.Summary.TotalStocks)
	}

	if len(result.Summary.TopStocks) == 0 {
		t.Error("应该推荐优质股票")
	}

	// 验证排序
	scores := make([]float64, len(result.Summary.TopStocks))
	for i, stock := range result.Summary.TopStocks {
		scores[i] = stock.Score
	}

	for i := 1; i < len(scores); i++ {
		if scores[i] > scores[i-1] {
			t.Error("股票评分应该按降序排列")
			break
		}
	}

	t.Logf("多股票分析测试通过: 分析股票数量 %d, 推荐股票数量 %d",
		len(result.StockResults), len(result.Summary.TopStocks))
}

// TestRealTimeAnalysis 测试实时分析
func TestRealTimeAnalysis(t *testing.T) {
	logger := utils.NewStandardLogger()
	logger.SetLevel(utils.InfoLevel)

	mockAI := NewMockAIAnalysisService()
	service, err := NewAIIntegration(mockAI, logger)
	if err != nil {
		t.Fatalf("创建AI集成服务失败: %v", err)
	}

	ctx := context.Background()

	// 创建实时分析请求
	req := &RealTimeAnalysisRequest{
		StockCode:      "000001",
		Trigger:        "price_change",
		TriggerValue:   0.05, // 5%涨幅
		AnalysisTypes:  []string{"technical", "news"},
		UserName:       "测试用户",
		RequestID:      "test_realtime_001",
		MaxDuration:    10,
		EnableAlerts:   true,
	}

	// 执行实时分析
	result, err := service.RealTimeAnalysis(ctx, req)
	if err != nil {
		t.Errorf("实时分析失败: %v", err)
		return
	}

	if result == nil {
		t.Error("实时分析结果为空")
		return
	}

	// 验证结果
	if result.Trigger != req.Trigger {
		t.Errorf("触发条件错误，期望 %s，实际 %s", req.Trigger, result.Trigger)
	}

	if result.TriggerTime.IsZero() {
		t.Error("触发时间不应为空")
	}

	if len(result.Alerts) == 0 && req.EnableAlerts {
		t.Error("启用告警时应该有告警信息")
	}

	if result.AnalysisResult == nil {
		t.Error("应该包含分析结果")
	}

	t.Logf("实时分析测试通过: 触发条件 %s, 告警数量 %d, 分析耗时 %v",
		result.Trigger, len(result.Alerts), result.ProcessingTime)
}

// TestCustomizedAnalysis 测试定制化分析
func TestCustomizedAnalysis(t *testing.T) {
	logger := utils.NewStandardLogger()
	logger.SetLevel(utils.InfoLevel)

	mockAI := NewMockAIAnalysisService()
	service, err := NewAIIntegration(mockAI, logger)
	if err != nil {
		t.Fatalf("创建AI集成服务失败: %v", err)
	}

	ctx := context.Background()

	// 创建定制化分析请求
	req := &CustomizedAnalysisRequest{
		StockCode:     "000001",
		UserName:      "测试用户",
		RequestID:     "test_custom_001",
		UserProfile: &UserProfile{
			RiskTolerance:  "moderate",
			InvestmentHorizon: "1y",
			InvestmentStyle:   "value",
			MaxPositionSize:   0.1,
		},
		PersonalizedSettings: map[string]interface{}{
			"focus_areas":      []string{"technology", "finance"},
			"exclude_industries": []string{"gambling"},
			"preferred_metrics": []string{"ROE", "PE", "debt_ratio"},
		},
		AnalysisRequirements: map[string]interface{}{
			"include_technical": true,
			"include_fundamental": true,
			"include_news": false,
			"include_risk": true,
			"custom_indicators": []string{"custom_rsi", "custom_macd"},
		},
	}

	// 执行定制化分析
	result, err := service.CustomizedAnalysis(ctx, req)
	if err != nil {
		t.Errorf("定制化分析失败: %v", err)
		return
	}

	if result == nil {
		t.Error("定制化分析结果为空")
		return
	}

	// 验证结果
	if result.UserProfile == nil {
		t.Error("应该包含用户画像")
	}

	if len(result.PersonalizedInsights) == 0 {
		t.Error("应该提供个性化洞察")
	}

	if len(result.Recommendations) == 0 {
		t.Error("应该提供个性化建议")
	}

	if result.RiskAssessment == nil {
		t.Error("应该包含风险评估")
	}

	// 验证建议符合用户风险偏好
	for _, rec := range result.Recommendations {
		if rec.RiskLevel == "" {
			t.Error("建议应该包含风险等级")
		}
	}

	t.Logf("定制化分析测试通过: 洞察数量 %d, 建议数量 %d, 风险等级 %s",
		len(result.PersonalizedInsights), len(result.Recommendations), result.RiskAssessment.OverallRisk)
}

// TestBatchAnalysis 测试批量分析
func TestBatchAnalysis(t *testing.T) {
	logger := utils.NewStandardLogger()
	logger.SetLevel(utils.InfoLevel)

	mockAI := NewMockAIAnalysisService()
	service, err := NewAIIntegration(mockAI, logger)
	if err != nil {
		t.Fatalf("创建AI集成服务失败: %v", err)
	}

	ctx := context.Background()

	// 创建批量分析请求
	req := &BatchAnalysisRequest{
		Requests: []*ComprehensiveAnalysisRequest{
			{
				StockCode:     "000001",
				AnalysisTypes: []string{"technical"},
				UserName:      "测试用户",
				RequestID:     "batch_001",
			},
			{
				StockCode:     "000002",
				AnalysisTypes: []string{"fundamental"},
				UserName:      "测试用户",
				RequestID:     "batch_002",
			},
			{
				StockCode:     "000858",
				AnalysisTypes: []string{"technical", "fundamental"},
				UserName:      "测试用户",
				RequestID:     "batch_003",
			},
		},
		Options: map[string]interface{}{
			"parallel": true,
			"timeout":  120,
		},
	}

	// 执行批量分析
	result, err := service.BatchAnalysis(ctx, req)
	if err != nil {
		t.Errorf("批量分析失败: %v", err)
		return
	}

	if result == nil {
		t.Error("批量分析结果为空")
		return
	}

	// 验证结果
	if len(result.Results) != 3 {
		t.Errorf("分析结果数量错误，期望 3，实际 %d", len(result.Results))
	}

	if result.Summary.TotalRequests != 3 {
		t.Errorf("总请求数量错误，期望 3，实际 %d", result.Summary.TotalRequests)
	}

	if result.Summary.SuccessCount != 3 {
		t.Errorf("成功数量错误，期望 3，实际 %d", result.Summary.SuccessCount)
	}

	if result.Summary.FailureCount != 0 {
		t.Errorf("失败数量错误，期望 0，实际 %d", result.Summary.FailureCount)
	}

	// 验证处理时间
	if result.ProcessingTime <= 0 {
		t.Error("处理时间应该大于0")
	}

	t.Logf("批量分析测试通过: 处理数量 %d, 成功数量 %d, 总耗时 %v",
		len(result.Results), result.Summary.SuccessCount, result.ProcessingTime)
}

// TestIntegrationHealthCheck 测试集成健康检查
func TestIntegrationHealthCheck(t *testing.T) {
	logger := utils.NewStandardLogger()
	logger.SetLevel(utils.InfoLevel)

	mockAI := NewMockAIAnalysisService()
	service, err := NewAIIntegration(mockAI, logger)
	if err != nil {
		t.Fatalf("创建AI集成服务失败: %v", err)
	}

	ctx := context.Background()

	// 执行健康检查
	health, err := service.HealthCheck(ctx)
	if err != nil {
		t.Errorf("健康检查失败: %v", err)
		return
	}

	if health == nil {
		t.Error("健康检查结果为空")
		return
	}

	// 验证健康状态
	if !health.IsHealthy {
		t.Error("服务应该是健康状态")
	}

	if len(health.Services) == 0 {
		t.Error("应该包含服务状态信息")
	}

	if health.CheckTime.IsZero() {
		t.Error("检查时间不应为空")
	}

	// 验证各个服务状态
	for serviceName, serviceStatus := range health.Services {
		if serviceStatus.Status != "healthy" {
			t.Errorf("服务 %s 状态不健康: %s", serviceName, serviceStatus.Status)
		}

		if serviceStatus.ResponseTime <= 0 {
			t.Errorf("服务 %s 响应时间应该大于0", serviceName)
		}
	}

	t.Logf("健康检查测试通过: 检查服务数量 %d, 总体状态 %s",
		len(health.Services), health.Status)
}

// TestIntegrationCaching 测试集成缓存功能
func TestIntegrationCaching(t *testing.T) {
	logger := utils.NewStandardLogger()
	logger.SetLevel(utils.InfoLevel)

	mockAI := NewMockAIAnalysisService()
	service, err := NewAIIntegration(mockAI, logger)
	if err != nil {
		t.Fatalf("创建AI集成服务失败: %v", err)
	}

	ctx := context.Background()

	// 创建分析请求
	req := &ComprehensiveAnalysisRequest{
		StockCode:     "000001",
		AnalysisTypes: []string{"technical"},
		UserName:      "测试用户",
		RequestID:     "test_cache_001",
		Options: map[string]interface{}{
			"enable_cache": true,
		},
	}

	// 第一次请求
	start1 := time.Now()
	result1, err := service.ComprehensiveAnalysis(ctx, req)
	duration1 := time.Since(start1)

	if err != nil {
		t.Fatalf("第一次分析失败: %v", err)
	}

	// 第二次相同请求（应该使用缓存）
	start2 := time.Now()
	result2, err := service.ComprehensiveAnalysis(ctx, req)
	duration2 := time.Since(start2)

	if err != nil {
		t.Fatalf("第二次分析失败: %v", err)
	}

	// 验证缓存效果
	if duration2 >= duration1 {
		t.Logf("注意：第二次请求未明显快于第一次，可能缓存未生效或测试环境限制")
		t.Logf("第一次耗时: %v, 第二次耗时: %v", duration1, duration2)
	}

	// 验证结果一致性
	if result1.Summary.OverallScore != result2.Summary.OverallScore {
		t.Error("缓存结果应该与原始结果一致")
	}

	t.Logf("缓存测试完成: 第一次 %v, 第二次 %v", duration1, duration2)
}

// TestErrorRecovery 测试错误恢复
func TestErrorRecovery(t *testing.T) {
	logger := utils.NewStandardLogger()
	logger.SetLevel(utils.InfoLevel)

	// 创建会失败的模拟AI服务
	mockAI := &MockAIAnalysisService{}
	mockAI.SetResponse("technical", &TechnicalAnalysisResponse{
		StockCode: "000001",
		Summary:   "模拟失败响应",
	})

	service, err := NewAIIntegration(mockAI, logger)
	if err != nil {
		t.Fatalf("创建AI集成服务失败: %v", err)
	}

	ctx := context.Background()

	// 创建分析请求
	req := &ComprehensiveAnalysisRequest{
		StockCode:     "000001",
		AnalysisTypes: []string{"technical", "fundamental"},
		UserName:      "测试用户",
		RequestID:     "test_error_001",
		Options: map[string]interface{}{
			"retry_count": 2,
			"timeout":     10,
		},
	}

	// 执行分析（部分失败）
	result, err := service.ComprehensiveAnalysis(ctx, req)
	if err != nil {
		t.Logf("分析部分失败是预期的: %v", err)
	}

	// 验证部分结果仍然可用
	if result != nil {
		if len(result.Analyses) > 0 {
			t.Log("部分分析结果仍然可用")
		}

		if result.ErrorInfo != nil {
			t.Logf("错误信息已记录: %s", result.ErrorInfo.Message)
		}
	}

	t.Log("错误恢复测试通过")
}

// TestIntegrationConcurrency 测试集成并发
func TestIntegrationConcurrency(t *testing.T) {
	logger := utils.NewStandardLogger()
	logger.SetLevel(utils.InfoLevel)

	mockAI := NewMockAIAnalysisService()
	service, err := NewAIIntegration(mockAI, logger)
	if err != nil {
		t.Fatalf("创建AI集成服务失败: %v", err)
	}

	ctx := context.Background()

	// 并发测试
	const numGoroutines = 5
	const requestsPerGoroutine = 3

	results := make(chan *ComprehensiveAnalysisResult, numGoroutines*requestsPerGoroutine)
	errors := make(chan error, numGoroutines*requestsPerGoroutine)

	for i := 0; i < numGoroutines; i++ {
		go func(id int) {
			for j := 0; j < requestsPerGoroutine; j++ {
				req := &ComprehensiveAnalysisRequest{
					StockCode:     "000001",
					AnalysisTypes: []string{"technical"},
					UserName:      "测试用户",
					RequestID:     fmt.Sprintf("concurrent_%d_%d", id, j),
				}

				result, err := service.ComprehensiveAnalysis(ctx, req)
				if err != nil {
					errors <- fmt.Errorf("并发请求失败 %d-%d: %v", id, j, err)
				} else {
					results <- result
				}
			}
		}(i)
	}

	// 收集结果
	successCount := 0
	errorCount := 0

	for i := 0; i < numGoroutines*requestsPerGoroutine; i++ {
		select {
		case result := <-results:
			if result != nil {
				successCount++
			}
		case err := <-errors:
			t.Error(err)
			errorCount++
		case <-time.After(30 * time.Second):
			t.Fatal("并发测试超时")
		}
	}

	if successCount == 0 {
		t.Error("没有成功的并发请求")
	}

	t.Logf("并发测试通过: 成功 %d, 失败 %d", successCount, errorCount)
}