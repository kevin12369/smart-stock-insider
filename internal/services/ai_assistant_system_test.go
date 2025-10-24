package services

import (
	"context"
	"encoding/json"
	"testing"
	"time"

	"smart-stock-insider/internal/utils"
)

// MockAIAnalysisService 模拟AI分析服务
type MockAIAnalysisService struct {
	responses map[string]interface{}
}

func NewMockAIAnalysisService() *MockAIAnalysisService {
	return &MockAIAnalysisService{
		responses: make(map[string]interface{}),
	}
}

func (m *MockAIAnalysisService) SetResponse(key string, response interface{}) {
	m.responses[key] = response
}

func (m *MockAIAnalysisService) TechnicalAnalysis(ctx context.Context, req *TechnicalAnalysisRequest) (*TechnicalAnalysisResponse, error) {
	if resp, exists := m.responses["technical"]; exists {
		return resp.(*TechnicalAnalysisResponse), nil
	}

	// 返回默认模拟响应
	return &TechnicalAnalysisResponse{
		StockCode:     req.StockCode,
		AnalysisDate:  time.Now().Format("2006-01-02"),
		Trend:         "上涨",
		Strength:      0.75,
		Confidence:    0.82,
		Signals: []TechnicalSignal{
			{
				Type:     "MACD金叉",
				Action:   "买入",
				Strength: 0.8,
				Price:    10.50,
			},
		},
		Indicators: map[string]interface{}{
			"MACD": map[string]interface{}{
				"signal": "金叉",
				"value":  0.15,
			},
			"RSI": map[string]interface{}{
				"value":     65.5,
				"signal":    "正常",
				"oversold":  30,
				"overbought": 70,
			},
		},
		Summary:      "技术面显示上涨趋势，MACD金叉买入信号",
		RiskLevel:    "中等",
		UpdateTime:   time.Now().Format("2006-01-02 15:04:05"),
		DataQuality:  "良好",
		Confidence:   0.82,
		AnalysisModel: "技术分析模型v2.0",
		Recommendations: []string{
			"关注MACD金叉信号",
			"控制仓位风险",
		},
	}, nil
}

func (m *MockAIAnalysisService) FundamentalAnalysis(ctx context.Context, req *FundamentalAnalysisRequest) (*FundamentalAnalysisResponse, error) {
	if resp, exists := m.responses["fundamental"]; exists {
		return resp.(*FundamentalAnalysisResponse), nil
	}

	return &FundamentalAnalysisResponse{
		StockCode:       req.StockCode,
		AnalysisDate:    time.Now().Format("2006-01-02"),
		Valuation:       "合理",
		ValuationScore:  0.75,
		FinancialHealth: "健康",
		HealthScore:     0.82,
		GrowthProspects: "良好",
		GrowthScore:     0.70,
		Profitability: map[string]interface{}{
			"ROE":      0.156,
			"ROA":      0.082,
			"毛利率":   0.285,
			"净利率":   0.125,
			"score":    0.78,
		},
		Leverage: map[string]interface{}{
			"资产负债率": 0.45,
			"流动比率":   1.85,
			"速动比率":   1.25,
			"score":     0.82,
		},
		ValuationMetrics: map[string]interface{}{
			"PE":     18.5,
			"PB":     2.3,
			"PS":     1.8,
			"score":  0.72,
		},
		Summary:         "基本面分析显示公司财务健康，估值合理",
		RiskFactors:     []string{"行业竞争加剧", "原材料价格波动"},
		Opportunities:   []string{"市场份额提升", "新产品推出"},
		UpdateTime:      time.Now().Format("2006-01-02 15:04:05"),
		DataQuality:     "良好",
		Confidence:      0.79,
		AnalysisModel:   "基本面分析模型v1.5",
		Recommendations: []string{
			"长期持有",
			"关注财报数据",
		},
	}, nil
}

func (m *MockAIAnalysisService) NewsAnalysis(ctx context.Context, req *NewsAnalysisRequest) (*NewsAnalysisResponse, error) {
	if resp, exists := m.responses["news"]; exists {
		return resp.(*NewsAnalysisResponse), nil
	}

	return &NewsAnalysisResponse{
		StockCode:     req.StockCode,
		AnalysisDate:  time.Now().Format("2006-01-02"),
		OverallSentiment: "积极",
		SentimentScore: 0.65,
		NewsCount:     15,
		PositiveCount: 8,
		NegativeCount: 3,
		NeutralCount:  4,
		KeyEvents: []NewsEvent{
			{
				Type:        "业绩预告",
				Sentiment:   "积极",
				Impact:      "高",
				Description: "公司预告上半年净利润增长50%",
				Date:        time.Now().AddDate(0, 0, -2).Format("2006-01-02"),
			},
		},
		Keywords: []string{
			"业绩增长", "新产品", "市场份额",
		},
		RiskAlerts: []string{
			"监管政策变化",
		},
		Summary:      "消息面整体积极，公司业绩预告超预期",
		UpdateTime:   time.Now().Format("2006-01-02 15:04:05"),
		DataQuality:  "良好",
		Confidence:   0.75,
		AnalysisModel: "新闻分析模型v1.2",
		Recommendations: []string{
			"关注业绩兑现情况",
			"跟踪行业动态",
		},
	}, nil
}

func (m *MockAIAnalysisService) PortfolioAnalysis(ctx context.Context, req *PortfolioAnalysisRequest) (*PortfolioAnalysisResponse, error) {
	if resp, exists := m.responses["portfolio"]; exists {
		return resp.(*PortfolioAnalysisResponse), nil
	}

	return &PortfolioAnalysisResponse{
		PortfolioID:    req.PortfolioID,
		AnalysisDate:   time.Now().Format("2006-01-02"),
		TotalValue:     100000.0,
		TotalReturn:    0.085,
		AnnualizedReturn: 0.125,
		Volatility:     0.185,
		SharpeRatio:    0.68,
		MaxDrawdown:    -0.125,
		RiskMetrics: map[string]interface{}{
			"VaR_95":        2500.0,
			"VaR_99":        4200.0,
			"beta":          1.15,
			"tracking_error": 0.025,
		},
		Diversification: map[string]interface{}{
			"concentration_ratio": 0.25,
			"effective_positions":  8.5,
			"correlation_avg":      0.35,
			"diversification_ratio": 0.78,
		},
		PerformanceMetrics: map[string]interface{}{
			"alpha":            0.025,
			"information_ratio": 0.45,
			"treynor_ratio":    0.152,
			"win_rate":         0.65,
		},
		AllocationAnalysis: []AllocationAnalysis{
			{
				Sector:     "科技",
				Weight:     0.35,
				Return:     0.125,
				Contribution: 0.04375,
				Risk:       0.225,
				Recommendation: "适度超配",
			},
		},
		RiskAnalysis: map[string]interface{}{
			"risk_factors": []string{
				"集中度风险偏高",
				"科技股波动较大",
			},
			"suggestions": []string{
				"增加债券配置",
				"分散行业风险",
			},
		},
		OptimizationSuggestions: []string{
			"建议降低集中度风险",
			"增加防御性资产配置",
			"定期再平衡",
		},
		Summary:      "投资组合表现良好，建议优化风险配置",
		UpdateTime:   time.Now().Format("2006-01-02 15:04:05"),
		DataQuality:  "良好",
		Confidence:   0.85,
		AnalysisModel: "组合分析模型v2.1",
	}, nil
}

// MockDataService 模拟数据服务
type MockDataService struct{}

func (m *MockDataService) GetStockBasicData(ctx context.Context, stockCode string) (map[string]interface{}, error) {
	return map[string]interface{}{
		"code":      stockCode,
		"name":      "测试股票",
		"industry":  "科技",
		"market":    "深圳",
		"price":     10.50,
		"change":    0.05,
		"change_pct": 0.48,
	}, nil
}

func (m *MockDataService) GetTechnicalIndicators(ctx context.Context, stockCode string) (map[string]interface{}, error) {
	return map[string]interface{}{
		"MACD": map[string]interface{}{
			"signal": "金叉",
			"value":  0.15,
		},
		"RSI": map[string]interface{}{
			"value": 65.5,
		},
	}, nil
}

func (m *MockDataService) GetFinancialData(ctx context.Context, stockCode string) (map[string]interface{}, error) {
	return map[string]interface{}{
		"ROE":   0.156,
		"PE":    18.5,
		"PB":    2.3,
		"debt":  0.45,
	}, nil
}

func (m *MockDataService) GetMarketData(ctx context.Context, stockCode string) (map[string]interface{}, error) {
	return map[string]interface{}{
		"price":    10.50,
		"volume":   1500000,
		"turnover": 15750000,
	}, nil
}

// TestAIAssistantSystemCreation 测试AI助手系统创建
func TestAIAssistantSystemCreation(t *testing.T) {
	logger := utils.NewStandardLogger()
	logger.SetLevel(utils.InfoLevel)

	// 创建模拟服务
	mockAI := NewMockAIAnalysisService()
	mockData := &MockDataService{}

	// 创建AI助手系统
	system, err := NewAIAssistantSystem(mockAI, mockData, logger)
	if err != nil {
		t.Fatalf("创建AI助手系统失败: %v", err)
	}

	if system == nil {
		t.Fatal("AI助手系统为空")
	}

	// 验证所有助手都已注册
	expectedAssistants := []AIAssistantType{
		TechnicalAnalyst,
		FundamentalAnalyst,
		NewsAnalyst,
		RiskController,
	}

	for _, assistantType := range expectedAssistants {
		if !system.IsAssistantAvailable(assistantType) {
			t.Errorf("助手 %s 未注册", assistantType)
		}
	}

	// 验证角色定义
	for _, assistantType := range expectedAssistants {
		role := system.GetAssistantRole(assistantType)
		if role == nil {
			t.Errorf("助手 %s 角色定义未找到", assistantType)
		}
	}

	t.Log("AI助手系统创建测试通过")
}

// TestIndividualAssistantTesting 测试各个助手功能
func TestIndividualAssistantTesting(t *testing.T) {
	logger := utils.NewStandardLogger()
	logger.SetLevel(utils.InfoLevel)

	mockAI := NewMockAIAnalysisService()
	mockData := &MockDataService{}

	system, err := NewAIAssistantSystem(mockAI, mockData, logger)
	if err != nil {
		t.Fatalf("创建AI助手系统失败: %v", err)
	}

	ctx := context.Background()

	// 测试技术分析师
	t.Run("测试技术分析师", func(t *testing.T) {
		req := &AIAssistantRequest{
			SessionID:   "test_session_1",
			StockCode:   "000001",
			Question:    "请分析000001的技术面情况",
			RequestType: "technical_analysis",
			Parameters: map[string]interface{}{
				"period": "60d",
				"indicators": []string{"MACD", "RSI", "MA"},
			},
			UserName: "测试用户",
		}

		resp, err := system.ProcessRequest(ctx, TechnicalAnalyst, req)
		if err != nil {
			t.Errorf("技术分析师处理请求失败: %v", err)
			return
		}

		if resp == nil {
			t.Error("技术分析师响应为空")
			return
		}

		if resp.AssistantType != TechnicalAnalyst {
			t.Errorf("期望助手类型 %s，实际 %s", TechnicalAnalyst, resp.AssistantType)
		}

		if resp.Confidence <= 0 {
			t.Error("技术分析师置信度应该大于0")
		}

		if len(resp.Content) == 0 {
			t.Error("技术分析师响应内容不应为空")
		}

		t.Logf("技术分析师测试通过: 置信度 %.2f, 内容长度 %d", resp.Confidence, len(resp.Content))
	})

	// 测试基本面分析师
	t.Run("测试基本面分析师", func(t *testing.T) {
		req := &AIAssistantRequest{
			SessionID:   "test_session_2",
			StockCode:   "000001",
			Question:    "请分析000001的基本面情况",
			RequestType: "fundamental_analysis",
			Parameters: map[string]interface{}{
				"include_financials": true,
				"include_valuation": true,
			},
			UserName: "测试用户",
		}

		resp, err := system.ProcessRequest(ctx, FundamentalAnalyst, req)
		if err != nil {
			t.Errorf("基本面分析师处理请求失败: %v", err)
			return
		}

		if resp == nil {
			t.Error("基本面分析师响应为空")
			return
		}

		if resp.AssistantType != FundamentalAnalyst {
			t.Errorf("期望助手类型 %s，实际 %s", FundamentalAnalyst, resp.AssistantType)
		}

		if len(resp.Insights) == 0 {
			t.Error("基本面分析师应该提供分析洞察")
		}

		t.Logf("基本面分析师测试通过: 洞察数量 %d, 置信度 %.2f", len(resp.Insights), resp.Confidence)
	})

	// 测试新闻分析师
	t.Run("测试新闻分析师", func(t *testing.T) {
		req := &AIAssistantRequest{
			SessionID:   "test_session_3",
			StockCode:   "000001",
			Question:    "请分析000001的新闻面情况",
			RequestType: "news_analysis",
			Parameters: map[string]interface{}{
				"days":    7,
				"sources": []string{"财经网", "证券时报"},
			},
			UserName: "测试用户",
		}

		resp, err := system.ProcessRequest(ctx, NewsAnalyst, req)
		if err != nil {
			t.Errorf("新闻分析师处理请求失败: %v", err)
			return
		}

		if resp == nil {
			t.Error("新闻分析师响应为空")
			return
		}

		if resp.AssistantType != NewsAnalyst {
			t.Errorf("期望助手类型 %s，实际 %s", NewsAnalyst, resp.AssistantType)
		}

		if len(resp.KeyPoints) == 0 {
			t.Error("新闻分析师应该提供关键信息点")
		}

		t.Logf("新闻分析师测试通过: 关键点数量 %d, 置信度 %.2f", len(resp.KeyPoints), resp.Confidence)
	})

	// 测试风险控制专员
	t.Run("测试风险控制专员", func(t *testing.T) {
		req := &AIAssistantRequest{
			SessionID:   "test_session_4",
			StockCode:   "000001",
			Question:    "请分析000001的投资风险",
			RequestType: "risk_analysis",
			Parameters: map[string]interface{}{
				"risk_types":   []string{"市场风险", "流动性风险", "信用风险"},
				"time_horizon": "3m",
			},
			UserName: "测试用户",
		}

		resp, err := system.ProcessRequest(ctx, RiskController, req)
		if err != nil {
			t.Errorf("风险控制专员处理请求失败: %v", err)
			return
		}

		if resp == nil {
			t.Error("风险控制专员响应为空")
			return
		}

		if resp.AssistantType != RiskController {
			t.Errorf("期望助手类型 %s，实际 %s", RiskController, resp.AssistantType)
		}

		if len(resp.RiskLevel) == 0 {
			t.Error("风险控制专员应该提供风险等级")
		}

		t.Logf("风险控制专员测试通过: 风险等级 %s, 置信度 %.2f", resp.RiskLevel, resp.Confidence)
	})
}

// TestCollaborativeAnalysis 测试协作分析
func TestCollaborativeAnalysis(t *testing.T) {
	logger := utils.NewStandardLogger()
	logger.SetLevel(utils.InfoLevel)

	mockAI := NewMockAIAnalysisService()
	mockData := &MockDataService{}

	system, err := NewAIAssistantSystem(mockAI, mockData, logger)
	if err != nil {
		t.Fatalf("创建AI助手系统失败: %v", err)
	}

	ctx := context.Background()

	// 创建协作分析请求
	req := &CollaborativeRequest{
		SessionID: "test_collab_session",
		StockCode: "000001",
		Question:  "请全面分析000001的投资价值",
		Analysts:  []AIAssistantType{TechnicalAnalyst, FundamentalAnalyst, NewsAnalyst, RiskController},
		Options: &CollaborativeOptions{
			EnableDiscussion: true,
			MaxRounds:        2,
			TimeoutMinutes:   5,
			RequireConsensus: false,
		},
		UserName: "测试用户",
	}

	// 执行协作分析
	result, err := system.CollaborativeAnalysis(ctx, req)
	if err != nil {
		t.Errorf("协作分析失败: %v", err)
		return
	}

	if result == nil {
		t.Error("协作分析结果为空")
		return
	}

	// 验证结果
	if len(result.IndividualAnalyses) != 4 {
		t.Errorf("期望4个独立分析，实际 %d", len(result.IndividualAnalyses))
	}

	if len(result.Discussion) == 0 && req.Options.EnableDiscussion {
		t.Error("启用讨论时应该有讨论内容")
	}

	if result.Summary.TotalConfidence <= 0 {
		t.Error("总体置信度应该大于0")
	}

	if len(result.Summary.Insights) == 0 {
		t.Error("协作分析应该提供综合洞察")
	}

	t.Logf("协作分析测试通过: 分析师数量 %d, 讨论轮次 %d, 总体置信度 %.2f",
		len(result.IndividualAnalyses), result.Summary.DiscussionRounds, result.Summary.TotalConfidence)
}

// TestSessionManagement 测试会话管理
func TestSessionManagement(t *testing.T) {
	logger := utils.NewStandardLogger()
	logger.SetLevel(utils.InfoLevel)

	mockAI := NewMockAIAnalysisService()
	mockData := &MockDataService{}

	system, err := NewAIAssistantSystem(mockAI, mockData, logger)
	if err != nil {
		t.Fatalf("创建AI助手系统失败: %v", err)
	}

	ctx := context.Background()

	// 创建会话
	sessionID := "test_session_mgmt"
	req := &AIAssistantRequest{
		SessionID:   sessionID,
		StockCode:   "000001",
		Question:    "测试会话管理",
		RequestType: "test",
		UserName:    "测试用户",
	}

	// 第一次请求
	resp1, err := system.ProcessRequest(ctx, TechnicalAnalyst, req)
	if err != nil {
		t.Fatalf("第一次请求失败: %v", err)
	}

	// 验证会话创建
	session := system.GetSession(sessionID)
	if session == nil {
		t.Error("会话未创建")
		return
	}

	if session.StockCode != "000001" {
		t.Errorf("会话股票代码错误，期望 000001，实际 %s", session.StockCode)
	}

	if len(session.ConversationHistory) != 1 {
		t.Errorf("会话历史记录数量错误，期望 1，实际 %d", len(session.ConversationHistory))
	}

	// 第二次请求
	req.Question = "继续分析"
	resp2, err := system.ProcessRequest(ctx, FundamentalAnalyst, req)
	if err != nil {
		t.Fatalf("第二次请求失败: %v", err)
	}

	// 验证会话更新
	session = system.GetSession(sessionID)
	if len(session.ConversationHistory) != 2 {
		t.Errorf("会话历史记录数量错误，期望 2，实际 %d", len(session.ConversationHistory))
	}

	// 获取会话历史
	history := system.GetSessionHistory(sessionID, 10)
	if len(history) != 2 {
		t.Errorf("获取历史记录数量错误，期望 2，实际 %d", len(history))
	}

	// 清理会话
	system.ClearSession(sessionID)
	session = system.GetSession(sessionID)
	if session != nil {
		t.Error("会话清理失败")
	}

	t.Log("会话管理测试通过")
}

// TestKnowledgeBase 测试知识库功能
func TestKnowledgeBase(t *testing.T) {
	logger := utils.NewStandardLogger()
	logger.SetLevel(utils.InfoLevel)

	kb := NewKnowledgeBase(logger)

	// 测试添加知识
	knowledge := &KnowledgeItem{
		ID:          "test_001",
		Type:        "technical_indicator",
		Title:       "MACD指标",
		Content:     "MACD是指数平滑移动平均线，用于判断买卖时机",
		Category:    "技术分析",
		Keywords:    []string{"MACD", "指标", "技术分析"},
		Relevance:   1.0,
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}

	err := kb.AddKnowledge(knowledge)
	if err != nil {
		t.Fatalf("添加知识失败: %v", err)
	}

	// 测试搜索知识
	results := kb.Search("MACD", 5)
	if len(results) == 0 {
		t.Error("搜索知识失败")
	}

	found := false
	for _, result := range results {
		if result.ID == "test_001" {
			found = true
			break
		}
	}

	if !found {
		t.Error("未找到添加的知识")
	}

	// 测试获取知识
	retrieved, err := kb.GetKnowledge("test_001")
	if err != nil {
		t.Errorf("获取知识失败: %v", err)
	}

	if retrieved == nil {
		t.Error("获取的知识为空")
	}

	if retrieved.Title != "MACD指标" {
		t.Errorf("知识标题错误，期望 MACD指标，实际 %s", retrieved.Title)
	}

	t.Log("知识库功能测试通过")
}

// TestErrorHandling 测试错误处理
func TestErrorHandling(t *testing.T) {
	logger := utils.NewStandardLogger()
	logger.SetLevel(utils.InfoLevel)

	mockAI := NewMockAIAnalysisService()
	mockData := &MockDataService{}

	system, err := NewAIAssistantSystem(mockAI, mockData, logger)
	if err != nil {
		t.Fatalf("创建AI助手系统失败: %v", err)
	}

	ctx := context.Background()

	// 测试无效助手类型
	req := &AIAssistantRequest{
		SessionID:   "test_error",
		StockCode:   "000001",
		Question:    "测试错误处理",
		RequestType: "test",
		UserName:    "测试用户",
	}

	_, err = system.ProcessRequest(ctx, "invalid_assistant", req)
	if err == nil {
		t.Error("应该返回错误")
	}

	// 测试空请求
	_, err = system.ProcessRequest(ctx, TechnicalAnalyst, nil)
	if err == nil {
		t.Error("空请求应该返回错误")
	}

	// 测试空股票代码
	req.StockCode = ""
	_, err = system.ProcessRequest(ctx, TechnicalAnalyst, req)
	if err == nil {
		t.Error("空股票代码应该返回错误")
	}

	t.Log("错误处理测试通过")
}

// TestConcurrentRequests 测试并发请求
func TestConcurrentRequests(t *testing.T) {
	logger := utils.NewStandardLogger()
	logger.SetLevel(utils.InfoLevel)

	mockAI := NewMockAIAnalysisService()
	mockData := &MockDataService{}

	system, err := NewAIAssistantSystem(mockAI, mockData, logger)
	if err != nil {
		t.Fatalf("创建AI助手系统失败: %v", err)
	}

	ctx := context.Background()

	// 并发请求测试
	const numGoroutines = 10
	const requestsPerGoroutine = 5

	errChan := make(chan error, numGoroutines)

	for i := 0; i < numGoroutines; i++ {
		go func(id int) {
			for j := 0; j < requestsPerGoroutine; j++ {
				req := &AIAssistantRequest{
					SessionID:   fmt.Sprintf("concurrent_%d_%d", id, j),
					StockCode:   "000001",
					Question:    fmt.Sprintf("并发测试请求 %d-%d", id, j),
					RequestType: "test",
					UserName:    "测试用户",
				}

				assistantType := AIAssistantType(TechnicalAnalyst)
				_, err := system.ProcessRequest(ctx, assistantType, req)
				if err != nil {
					errChan <- fmt.Errorf("并发请求失败 %d-%d: %v", id, j, err)
					return
				}
			}
			errChan <- nil
		}(i)
	}

	// 收集结果
	for i := 0; i < numGoroutines; i++ {
		err := <-errChan
		if err != nil {
			t.Errorf(err.Error())
		}
	}

	t.Logf("并发测试通过: %d个协程，每个协程%d个请求", numGoroutines, requestsPerGoroutine)
}

// TestPerformance 测试性能
func TestPerformance(t *testing.T) {
	logger := utils.NewStandardLogger()
	logger.SetLevel(utils.InfoLevel)

	mockAI := NewMockAIAnalysisService()
	mockData := &MockDataService{}

	system, err := NewAIAssistantSystem(mockAI, mockData, logger)
	if err != nil {
		t.Fatalf("创建AI助手系统失败: %v", err)
	}

	ctx := context.Background()

	// 性能测试
	const numRequests = 100
	start := time.Now()

	for i := 0; i < numRequests; i++ {
		req := &AIAssistantRequest{
			SessionID:   fmt.Sprintf("perf_%d", i),
			StockCode:   "000001",
			Question:    "性能测试",
			RequestType: "test",
			UserName:    "测试用户",
		}

		_, err := system.ProcessRequest(ctx, TechnicalAnalyst, req)
		if err != nil {
			t.Errorf("性能测试请求失败 %d: %v", i, err)
		}
	}

	duration := time.Since(start)
	avgDuration := duration / numRequests

	t.Logf("性能测试完成: %d个请求，总耗时 %v，平均耗时 %v",
		numRequests, duration, avgDuration)

	// 性能要求：平均响应时间小于100ms
	if avgDuration > 100*time.Millisecond {
		t.Errorf("性能不达标，平均响应时间 %v 大于 100ms", avgDuration)
	}
}

// BenchmarkProcessRequest 性能基准测试
func BenchmarkProcessRequest(b *testing.B) {
	logger := utils.NewStandardLogger()
	logger.SetLevel(utils.ErrorLevel) // 减少日志输出

	mockAI := NewMockAIAnalysisService()
	mockData := &MockDataService{}

	system, err := NewAIAssistantSystem(mockAI, mockData, logger)
	if err != nil {
		b.Fatalf("创建AI助手系统失败: %v", err)
	}

	ctx := context.Background()
	req := &AIAssistantRequest{
		SessionID:   "benchmark",
		StockCode:   "000001",
		Question:    "基准测试",
		RequestType: "test",
		UserName:    "测试用户",
	}

	b.ResetTimer()

	for i := 0; i < b.N; i++ {
		req.SessionID = fmt.Sprintf("benchmark_%d", i)
		_, err := system.ProcessRequest(ctx, TechnicalAnalyst, req)
		if err != nil {
			b.Errorf("基准测试请求失败: %v", err)
		}
	}
}