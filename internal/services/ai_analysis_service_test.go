package services

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"smart-stock-insider/internal/utils"
)

// 创建测试服务器
func createTestServer() *httptest.Server {
	mux := http.NewServeMux()

	// 技术分析接口
	mux.HandleFunc("/api/ai/technical-analysis", func(w http.ResponseWriter, r *http.Request) {
		response := map[string]interface{}{
			"success": true,
			"data": map[string]interface{}{
				"stock_code":     "000001",
				"trend":          "上涨",
				"strength":       0.75,
				"confidence":     0.82,
				"signals": []map[string]interface{}{
					{
						"type":     "MACD金叉",
						"action":   "买入",
						"strength": 0.8,
						"price":    10.50,
					},
				},
				"indicators": map[string]interface{}{
					"MACD": map[string]interface{}{
						"signal": "金叉",
						"value":  0.15,
					},
					"RSI": map[string]interface{}{
						"value": 65.5,
					},
				},
				"summary":      "技术面显示上涨趋势",
				"risk_level":   "中等",
				"update_time":  time.Now().Format("2006-01-02 15:04:05"),
				"data_quality": "良好",
			},
			"message": "技术分析完成",
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(response)
	})

	// 基本面分析接口
	mux.HandleFunc("/api/ai/fundamental-analysis", func(w http.ResponseWriter, r *http.Request) {
		response := map[string]interface{}{
			"success": true,
			"data": map[string]interface{}{
				"stock_code":       "000001",
				"valuation":        "合理",
				"valuation_score":  0.75,
				"financial_health": "健康",
				"health_score":     0.82,
				"profitability": map[string]interface{}{
					"ROE":     0.156,
					"ROA":     0.082,
					"毛利率":  0.285,
					"净利率":  0.125,
				},
				"leverage": map[string]interface{}{
					"资产负债率": 0.45,
					"流动比率":   1.85,
					"速动比率":   1.25,
				},
				"valuation_metrics": map[string]interface{}{
					"PE": 18.5,
					"PB": 2.3,
					"PS": 1.8,
				},
				"summary":      "基本面分析显示公司财务健康",
				"risk_factors": []string{"行业竞争"},
				"opportunities": []string{"市场份额提升"},
				"update_time":  time.Now().Format("2006-01-02 15:04:05"),
				"data_quality": "良好",
			},
			"message": "基本面分析完成",
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(response)
	})

	// 新闻分析接口
	mux.HandleFunc("/api/ai/news-analysis", func(w http.ResponseWriter, r *http.Request) {
		response := map[string]interface{}{
			"success": true,
			"data": map[string]interface{}{
				"stock_code":          "000001",
				"overall_sentiment":   "积极",
				"sentiment_score":     0.65,
				"news_count":          15,
				"positive_count":      8,
				"negative_count":      3,
				"neutral_count":       4,
				"key_events": []map[string]interface{}{
					{
						"type":        "业绩预告",
						"sentiment":   "积极",
						"impact":      "高",
						"description": "公司预告上半年净利润增长50%",
						"date":        time.Now().AddDate(0, 0, -2).Format("2006-01-02"),
					},
				},
				"keywords":     []string{"业绩增长", "新产品"},
				"risk_alerts":  []string{"监管政策变化"},
				"summary":      "消息面整体积极",
				"update_time":  time.Now().Format("2006-01-02 15:04:05"),
				"data_quality": "良好",
			},
			"message": "新闻分析完成",
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(response)
	})

	// 投资组合分析接口
	mux.HandleFunc("/api/ai/portfolio-analysis", func(w http.ResponseWriter, r *http.Request) {
		response := map[string]interface{}{
			"success": true,
			"data": map[string]interface{}{
				"portfolio_id":        "test_portfolio",
				"total_value":         100000.0,
				"total_return":        0.085,
				"annualized_return":   0.125,
				"volatility":          0.185,
				"sharpe_ratio":        0.68,
				"max_drawdown":        -0.125,
				"risk_metrics": map[string]interface{}{
					"VaR_95":         2500.0,
					"VaR_99":         4200.0,
					"beta":           1.15,
					"tracking_error": 0.025,
				},
				"diversification": map[string]interface{}{
					"concentration_ratio": 0.25,
					"effective_positions":  8.5,
					"correlation_avg":      0.35,
				},
				"allocation_analysis": []map[string]interface{}{
					{
						"sector":        "科技",
						"weight":        0.35,
						"return":        0.125,
						"contribution":  0.04375,
						"risk":          0.225,
						"recommendation": "适度超配",
					},
				},
				"optimization_suggestions": []string{
					"建议降低集中度风险",
					"增加防御性资产配置",
				},
				"summary":      "投资组合表现良好",
				"update_time":  time.Now().Format("2006-01-02 15:04:05"),
				"data_quality": "良好",
			},
			"message": "投资组合分析完成",
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(response)
	})

	// AI能力接口
	mux.HandleFunc("/api/ai/capabilities", func(w http.ResponseWriter, r *http.Request) {
		response := map[string]interface{}{
			"success": true,
			"data": map[string]interface{}{
				"available_models": []string{
					"技术分析模型v2.0",
					"基本面分析模型v1.5",
					"新闻分析模型v1.2",
					"组合分析模型v2.1",
				},
				"supported_analysis_types": []string{
					"technical", "fundamental", "news", "portfolio",
				},
				"features": []string{
					"趋势识别",
					"信号生成",
					"风险评估",
					"投资建议",
				},
				"status": "healthy",
			},
			"message": "获取AI能力成功",
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(response)
	})

	return httptest.NewServer(mux)
}

// TestAIAnalysisServiceCreation 测试AI分析服务创建
func TestAIAnalysisServiceCreation(t *testing.T) {
	logger := utils.NewStandardLogger()
	logger.SetLevel(utils.InfoLevel)

	// 创建测试服务器
	testServer := createTestServer()
	defer testServer.Close()

	// 创建AI分析服务
	service := NewAIAnalysisService(testServer.URL, "", logger)

	if service == nil {
		t.Fatal("AI分析服务创建失败")
	}

	// 验证服务配置
	if service.baseURL != testServer.URL {
		t.Errorf("BaseURL错误，期望 %s，实际 %s", testServer.URL, service.baseURL)
	}

	if service.client == nil {
		t.Error("HTTP客户端未初始化")
	}

	if service.logger == nil {
		t.Error("日志记录器未初始化")
	}

	t.Log("AI分析服务创建测试通过")
}

// TestTechnicalAnalysis 测试技术分析
func TestTechnicalAnalysis(t *testing.T) {
	logger := utils.NewStandardLogger()
	logger.SetLevel(utils.InfoLevel)

	testServer := createTestServer()
	defer testServer.Close()

	service := NewAIAnalysisService(testServer.URL, "", logger)
	ctx := context.Background()

	// 创建技术分析请求
	req := &TechnicalAnalysisRequest{
		StockCode:    "000001",
		Period:       "60d",
		Indicators:   []string{"MACD", "RSI", "MA"},
		PriceData:    []float64{10.0, 10.5, 10.3, 10.8, 10.6},
		VolumeData:   []int64{1000000, 1200000, 1100000, 1300000, 1150000},
		UserRequest:  "请分析技术面情况",
		Options: map[string]interface{}{
			"include_signals": true,
			"risk_assessment": true,
		},
	}

	// 执行技术分析
	result, err := service.TechnicalAnalysis(ctx, req)
	if err != nil {
		t.Errorf("技术分析失败: %v", err)
		return
	}

	if result == nil {
		t.Error("技术分析结果为空")
		return
	}

	// 验证结果
	if result.StockCode != "000001" {
		t.Errorf("股票代码错误，期望 000001，实际 %s", result.StockCode)
	}

	if result.Trend == "" {
		t.Error("趋势分析不应为空")
	}

	if result.Strength <= 0 {
		t.Error("信号强度应该大于0")
	}

	if result.Confidence <= 0 {
		t.Error("置信度应该大于0")
	}

	if len(result.Signals) == 0 {
		t.Error("应该提供交易信号")
	}

	if len(result.Indicators) == 0 {
		t.Error("应该提供技术指标")
	}

	if result.Summary == "" {
		t.Error("应该提供分析摘要")
	}

	t.Logf("技术分析测试通过: 股票 %s, 趋势 %s, 信号数量 %d, 置信度 %.2f",
		result.StockCode, result.Trend, len(result.Signals), result.Confidence)
}

// TestFundamentalAnalysis 测试基本面分析
func TestFundamentalAnalysis(t *testing.T) {
	logger := utils.NewStandardLogger()
	logger.SetLevel(utils.InfoLevel)

	testServer := createTestServer()
	defer testServer.Close()

	service := NewAIAnalysisService(testServer.URL, "", logger)
	ctx := context.Background()

	// 创建基本面分析请求
	req := &FundamentalAnalysisRequest{
		StockCode:   "000001",
		Period:      "3y",
		Financials: map[string]interface{}{
			"revenue":      []float64{100, 120, 140, 160},
			"net_profit":   []float64{10, 15, 20, 25},
			"total_assets": []float64{200, 220, 250, 280},
			"total_debt":   []float64{80, 85, 90, 95},
		},
		Valuation: map[string]interface{}{
			"market_cap":  50000,
			"pe_ratio":   18.5,
			"pb_ratio":   2.3,
			"ps_ratio":   1.8,
		},
		UserRequest: "请分析基本面情况",
		Options: map[string]interface{}{
			"include_industry_comparison": true,
			"include_growth_prospects":    true,
		},
	}

	// 执行基本面分析
	result, err := service.FundamentalAnalysis(ctx, req)
	if err != nil {
		t.Errorf("基本面分析失败: %v", err)
		return
	}

	if result == nil {
		t.Error("基本面分析结果为空")
		return
	}

	// 验证结果
	if result.StockCode != "000001" {
		t.Errorf("股票代码错误，期望 000001，实际 %s", result.StockCode)
	}

	if result.Valuation == "" {
		t.Error("估值评估不应为空")
	}

	if result.ValuationScore <= 0 {
		t.Error("估值评分应该大于0")
	}

	if result.FinancialHealth == "" {
		t.Error("财务健康度不应为空")
	}

	if result.HealthScore <= 0 {
		t.Error("健康评分应该大于0")
	}

	if len(result.Profitability) == 0 {
		t.Error("应该提供盈利能力分析")
	}

	if len(result.ValuationMetrics) == 0 {
		t.Error("应该提供估值指标")
	}

	if result.Summary == "" {
		t.Error("应该提供分析摘要")
	}

	t.Logf("基本面分析测试通过: 股票 %s, 估值 %s, 健康度 %s, 评分 %.2f",
		result.StockCode, result.Valuation, result.FinancialHealth, result.ValuationScore)
}

// TestNewsAnalysis 测试新闻分析
func TestNewsAnalysis(t *testing.T) {
	logger := utils.NewStandardLogger()
	logger.SetLevel(utils.InfoLevel)

	testServer := createTestServer()
	defer testServer.Close()

	service := NewAIAnalysisService(testServer.URL, "", logger)
	ctx := context.Background()

	// 创建新闻分析请求
	req := &NewsAnalysisRequest{
		StockCode:    "000001",
		Period:       "7d",
		NewsItems:    []string{
			"公司发布业绩预告，预计上半年净利润增长50%",
			"公司新产品获得市场认可，订单量大幅增长",
			"行业监管政策可能发生变化，需密切关注",
		},
		UserRequest:  "请分析新闻面情况",
		Options: map[string]interface{}{
			"sentiment_analysis": true,
			"event_extraction":   true,
			"risk_assessment":    true,
		},
	}

	// 执行新闻分析
	result, err := service.NewsAnalysis(ctx, req)
	if err != nil {
		t.Errorf("新闻分析失败: %v", err)
		return
	}

	if result == nil {
		t.Error("新闻分析结果为空")
		return
	}

	// 验证结果
	if result.StockCode != "000001" {
		t.Errorf("股票代码错误，期望 000001，实际 %s", result.StockCode)
	}

	if result.OverallSentiment == "" {
		t.Error("整体情绪不应为空")
	}

	if result.SentimentScore < -1 || result.SentimentScore > 1 {
		t.Error("情绪评分应该在[-1, 1]范围内")
	}

	if result.NewsCount <= 0 {
		t.Error("新闻数量应该大于0")
	}

	if len(result.KeyEvents) == 0 {
		t.Error("应该提供关键事件")
	}

	if len(result.Keywords) == 0 {
		t.Error("应该提供关键词")
	}

	if result.Summary == "" {
		t.Error("应该提供分析摘要")
	}

	t.Logf("新闻分析测试通过: 股票 %s, 情绪 %s, 新闻数量 %d, 关键事件 %d",
		result.StockCode, result.OverallSentiment, result.NewsCount, len(result.KeyEvents))
}

// TestPortfolioAnalysis 测试投资组合分析
func TestPortfolioAnalysis(t *testing.T) {
	logger := utils.NewStandardLogger()
	logger.SetLevel(utils.InfoLevel)

	testServer := createTestServer()
	defer testServer.Close()

	service := NewAIAnalysisService(testServer.URL, "", logger)
	ctx := context.Background()

	// 创建投资组合分析请求
	req := &PortfolioAnalysisRequest{
		PortfolioID: "test_portfolio",
		Positions: []PortfolioPosition{
			{
				StockCode:  "000001",
				Shares:     1000,
				CostPrice:  10.00,
				CurrentPrice: 10.50,
				Weight:     0.105,
				Sector:     "科技",
			},
			{
				StockCode:  "000002",
				Shares:     2000,
				CostPrice:  15.00,
				CurrentPrice: 16.20,
				Weight:     0.324,
				Sector:     "金融",
			},
		},
		TotalValue: 100000.0,
		UserRequest: "请分析投资组合情况",
		Options: map[string]interface{}{
			"risk_analysis":     true,
			"correlation_check": true,
			"optimization":      true,
		},
	}

	// 执行投资组合分析
	result, err := service.PortfolioAnalysis(ctx, req)
	if err != nil {
		t.Errorf("投资组合分析失败: %v", err)
		return
	}

	if result == nil {
		t.Error("投资组合分析结果为空")
		return
	}

	// 验证结果
	if result.PortfolioID != "test_portfolio" {
		t.Errorf("投资组合ID错误，期望 test_portfolio，实际 %s", result.PortfolioID)
	}

	if result.TotalValue <= 0 {
		t.Error("总价值应该大于0")
	}

	if result.AnnualizedReturn < -1 || result.AnnualizedReturn > 10 {
		t.Error("年化收益率应该在合理范围内")
	}

	if result.Volatility <= 0 {
		t.Error("波动率应该大于0")
	}

	if result.SharpeRatio < -1 || result.SharpeRatio > 10 {
		t.Error("夏普比率应该在合理范围内")
	}

	if len(result.RiskMetrics) == 0 {
		t.Error("应该提供风险指标")
	}

	if len(result.AllocationAnalysis) == 0 {
		t.Error("应该提供配置分析")
	}

	if result.Summary == "" {
		t.Error("应该提供分析摘要")
	}

	t.Logf("投资组合分析测试通过: 组合 %s, 总价值 %.2f, 夏普比率 %.2f",
		result.PortfolioID, result.TotalValue, result.SharpeRatio)
}

// TestGetCapabilities 测试获取AI能力
func TestGetCapabilities(t *testing.T) {
	logger := utils.NewStandardLogger()
	logger.SetLevel(utils.InfoLevel)

	testServer := createTestServer()
	defer testServer.Close()

	service := NewAIAnalysisService(testServer.URL, "", logger)
	ctx := context.Background()

	// 获取AI能力
	capabilities, err := service.GetCapabilities(ctx)
	if err != nil {
		t.Errorf("获取AI能力失败: %v", err)
		return
	}

	if capabilities == nil {
		t.Error("AI能力为空")
		return
	}

	// 验证能力信息
	if len(capabilities.AvailableModels) == 0 {
		t.Error("应该有可用模型")
	}

	if len(capabilities.SupportedAnalysisTypes) == 0 {
		t.Error("应该有支持的分析类型")
	}

	if len(capabilities.Features) == 0 {
		t.Error("应该有功能特性")
	}

	if capabilities.Status == "" {
		t.Error("状态不应为空")
	}

	t.Logf("AI能力测试通过: 模型数量 %d, 分析类型 %d, 功能特性 %d, 状态 %s",
		len(capabilities.AvailableModels), len(capabilities.SupportedAnalysisTypes),
		len(capabilities.Features), capabilities.Status)
}

// TestErrorHandling 测试错误处理
func TestErrorHandling(t *testing.T) {
	logger := utils.NewStandardLogger()
	logger.SetLevel(utils.InfoLevel)

	// 创建无效URL的服务
	service := NewAIAnalysisService("http://invalid-url-that-does-not-exist.com", "", logger)
	ctx := context.Background()

	// 测试技术分析错误处理
	req := &TechnicalAnalysisRequest{
		StockCode: "000001",
		Period:    "60d",
	}

	_, err := service.TechnicalAnalysis(ctx, req)
	if err == nil {
		t.Error("应该返回连接错误")
	}

	// 测试空请求
	_, err = service.TechnicalAnalysis(ctx, nil)
	if err == nil {
		t.Error("空请求应该返回错误")
	}

	t.Log("错误处理测试通过")
}

// TestTimeoutHandling 测试超时处理
func TestTimeoutHandling(t *testing.T) {
	logger := utils.NewStandardLogger()
	logger.SetLevel(utils.InfoLevel)

	// 创建慢响应的测试服务器
	mux := http.NewServeMux()
	mux.HandleFunc("/api/ai/technical-analysis", func(w http.ResponseWriter, r *http.Request) {
		time.Sleep(5 * time.Second) // 模拟慢响应
		w.WriteHeader(http.StatusOK)
	})

	testServer := httptest.NewServer(mux)
	defer testServer.Close()

	service := NewAIAnalysisService(testServer.URL, "", logger)

	// 创建短超时的上下文
	ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
	defer cancel()

	req := &TechnicalAnalysisRequest{
		StockCode: "000001",
		Period:    "60d",
	}

	start := time.Now()
	_, err := service.TechnicalAnalysis(ctx, req)
	duration := time.Since(start)

	if err == nil {
		t.Error("应该返回超时错误")
	}

	if duration > 2*time.Second {
		t.Errorf("超时处理时间过长，实际 %v", duration)
	}

	t.Logf("超时处理测试通过: 耗时 %v", duration)
}

// TestConcurrentRequests 测试并发请求
func TestConcurrentRequests(t *testing.T) {
	logger := utils.NewStandardLogger()
	logger.SetLevel(utils.InfoLevel)

	testServer := createTestServer()
	defer testServer.Close()

	service := NewAIAnalysisService(testServer.URL, "", logger)
	ctx := context.Background()

	// 并发测试
	const numGoroutines = 10
	const requestsPerGoroutine = 5

	results := make(chan *TechnicalAnalysisResponse, numGoroutines*requestsPerGoroutine)
	errors := make(chan error, numGoroutines*requestsPerGoroutine)

	for i := 0; i < numGoroutines; i++ {
		go func(id int) {
			for j := 0; j < requestsPerGoroutine; j++ {
				req := &TechnicalAnalysisRequest{
					StockCode: "000001",
					Period:    "60d",
				}

				result, err := service.TechnicalAnalysis(ctx, req)
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
			if result != nil && result.StockCode == "000001" {
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

// TestServiceHealthCheck 测试服务健康检查
func TestServiceHealthCheck(t *testing.T) {
	logger := utils.NewStandardLogger()
	logger.SetLevel(utils.InfoLevel)

	testServer := createTestServer()
	defer testServer.Close()

	service := NewAIAnalysisService(testServer.URL, "", logger)
	ctx := context.Background()

	// 执行健康检查
	isHealthy, err := service.HealthCheck(ctx)
	if err != nil {
		t.Errorf("健康检查失败: %v", err)
		return
	}

	if !isHealthy {
		t.Error("服务应该是健康状态")
	}

	t.Log("服务健康检查测试通过")
}

// BenchmarkTechnicalAnalysis 技术分析性能基准测试
func BenchmarkTechnicalAnalysis(b *testing.B) {
	logger := utils.NewStandardLogger()
	logger.SetLevel(utils.ErrorLevel) // 减少日志输出

	testServer := createTestServer()
	defer testServer.Close()

	service := NewAIAnalysisService(testServer.URL, "", logger)
	ctx := context.Background()

	req := &TechnicalAnalysisRequest{
		StockCode:  "000001",
		Period:     "60d",
		Indicators: []string{"MACD", "RSI", "MA"},
	}

	b.ResetTimer()

	for i := 0; i < b.N; i++ {
		_, err := service.TechnicalAnalysis(ctx, req)
		if err != nil {
			b.Errorf("基准测试失败: %v", err)
		}
	}
}