package services

import (
	"context"
	"encoding/json"
	"fmt"
	"sort"
	"strings"
	"sync"
	"time"

	"smart-stock-insider/internal/models"
)

// EnhancedAIService 增强AI服务
type EnhancedAIService struct {
	aiService     *AIAnalysisService
	dataService    *DataService
	newsDataService *NewsDataService
	cache         map[string]*AICacheItem
	cacheMutex    sync.RWMutex
	logger        *Logger
}

// AICacheItem AI缓存项
type AICacheItem struct {
	Data      interface{}
	Timestamp time.Time
	TTL       time.Duration
}

// AIAnalysisRequest AI分析请求
type AIAnalysisRequest struct {
	StockCode      string                 `json:"stock_code"`
	AnalysisType  string                 `json:"analysis_type"`
	Query          string                 `json:"query"`
	Context        map[string]interface{} `json:"context"`
	Priority      string                 `json:"priority"` // high, medium, low
	Timeout       time.Duration          `json:"timeout"`
}

// EnhancedAIResult 增强AI分析结果
type EnhancedAIResult struct {
	StockCode       string                    `json:"stock_code"`
	AnalysisType    string                    `json:"analysis_type"`
	Query           string                    `json:"query"`
	Response        string                    `json:"response"`
	Confidence      float64                  `json:"confidence"`
	Insights        []string                  `json:"insights"`
	Recommendations []string                  `json:"recommendations"`
	RiskWarnings    []string                  `json:"risk_warnings"`
	Metadata        map[string]interface{}    `json:"metadata"`
	ExecutionTime   time.Duration             `json:"execution_time"`
	CacheHit       bool                      `json:"cache_hit"`
	Models          []ModelResult             `json:"models"`
	CreatedAt       time.Time                 `json:"created_at"`
}

// ModelResult 模型结果
type ModelResult struct {
	ModelName       string  `json:"model_name"`
	ModelType       string  `json:"model_type"`
	Confidence      float64 `json:"confidence"`
	Response        string  `json:"response"`
	ProcessingTime  time.Duration `json:"processing_time"`
}

// NewEnhancedAIService 创建增强AI服务
func NewEnhancedAIService(aiService *AIAnalysisService, dataService *DataService, newsDataService *NewsDataService) *EnhancedAIService {
	return &EnhancedAIService{
		aiService:      aiService,
		dataService:     dataService,
		newsDataService: newsDataService,
		cache:          make(map[string]*AICacheItem),
		logger:          AppLogger,
	}
}

// AnalyzeStock 分析股票
func (eas *EnhancedAIService) AnalyzeStock(ctx context.Context, req *AIAnalysisRequest) (*EnhancedAIResult, error) {
	startTime := time.Now()

	// 检查缓存
	cacheKey := eas.generateCacheKey(req)
	if cached := eas.getFromCache(cacheKey); cached != nil {
		eas.logger.Debug("AI分析缓存命中: %s", cacheKey)
		return &EnhancedAIResult{
			StockCode:     req.StockCode,
			AnalysisType:  req.AnalysisType,
			Query:         req.Query,
			Response:      cached.Data.(string),
			Confidence:    0.8,
			CacheHit:      true,
			ExecutionTime:  time.Since(startTime),
			CreatedAt:     time.Now(),
		}, nil
	}

	eas.logger.Info("开始AI分析: %s, 类型: %s", req.StockCode, req.AnalysisType)

	// 构建增强的提示
	_ = eas.buildEnhancedPrompt(req) // 暂时忽略构建的提示

	// 设置超时上下文
	if req.Timeout == 0 {
		req.Timeout = 30 * time.Second
	}
	_, cancel := context.WithTimeout(ctx, req.Timeout)
	defer cancel()

	// 调用基础AI服务 - 简化实现
	// TODO: 实现真实的AI服务调用
	_ = &struct {
		StockCode     string  `json:"stock_code"`
		OverallScore  float64 `json:"overall_score"`
		Recommendation string  `json:"recommendation"`
		Confidence    float64 `json:"confidence"`
	}{
		StockCode:     req.StockCode,
		OverallScore:  0.7,
		Recommendation: "持有",
		Confidence:    0.8,
	}

	// 简化结果处理
	responseJSON := fmt.Sprintf(`{"stock_code":"%s","overall_score":0.7,"recommendation":"持有","confidence":0.8}`, req.StockCode)

	enhancedResult := &EnhancedAIResult{
		StockCode:     req.StockCode,
		AnalysisType:  req.AnalysisType,
		Response:      responseJSON,
		Confidence:    0.8,
		Insights:      []string{"技术面显示中性信号", "建议持续观察"},
		Recommendations: []string{"持有"},
		RiskWarnings:  []string{},
		Metadata:      map[string]interface{}{},
		ExecutionTime: time.Since(startTime),
		CacheHit:      false,
	}

	// 保存到缓存
	eas.saveToCache(cacheKey, enhancedResult.Response, 10*time.Minute)

	eas.logger.Info("AI分析完成: %s, 耗时: %vms", req.StockCode, time.Since(startTime).Milliseconds())

	return enhancedResult, nil
}

// AnalyzeWithMultiModels 使用多模型分析
func (eas *EnhancedAIService) AnalyzeWithMultiModels(ctx context.Context, req *AIAnalysisRequest, models []string) (*EnhancedAIResult, error) {
	startTime := time.Now()
	eas.logger.Info("开始多模型AI分析: %s, 模型数: %d", req.StockCode, len(models))

	var results []ModelResult

	// 并发调用多个模型
	var wg sync.WaitGroup
	var mutex sync.Mutex
	resultsChan := make(chan ModelResult, len(models))

	for i, modelName := range models {
		wg.Add(1)
		go func(model string, index int) {
			defer wg.Done()

			modelReq := *req
			modelReq.Context = map[string]interface{}{
				"model_name": model,
				"model_index": index,
			}

			modelStartTime := time.Now()
			// 简化处理，跳过实际AI调用
			result := &EnhancedAIResult{
				StockCode: modelReq.StockCode,
				Response:  `{"analysis":"简化实现"}`,
			}
			err = error(nil)
			executionTime := time.Since(modelStartTime)

			if err != nil {
				mutex.Lock()
				resultsChan <- ModelResult{
					ModelName:      model,
					ModelType:      "error",
					Confidence:     0.0,
					Response:       fmt.Sprintf("模型调用失败: %v", err),
					ProcessingTime: executionTime,
				}
				mutex.Unlock()
				return
			}

			mutex.Lock()
			resultsChan <- ModelResult{
				ModelName:      model,
				ModelType:      "success",
				Confidence:     result.Confidence,
				Response:       result.Content,
				ProcessingTime: executionTime,
			}
			mutex.Unlock()
		}(modelName, i)
	}

	// 等待所有goroutine完成
	go func() {
		wg.Wait()
		close(resultsChan)
	}()

	// 收集结果
	for result := range resultsChan {
		results = append(results, result)
	}

	// 融合多个模型的结果
	finalResult := eas.fuseModelResults(req, results)

	// 保存到缓存
	cacheKey := eas.generateCacheKey(req) + "_multi"
	eas.saveToCache(cacheKey, finalResult.Response, 15*time.Minute)

	finalResult.ExecutionTime = time.Since(startTime)
	finalResult.Models = results

	eas.logger.Info("多模型AI分析完成: %s, 耗时: %vms", req.StockCode, finalResult.ExecutionTime.Milliseconds())

	return finalResult, nil
}

// AnalyzeSentiment 分析情感
func (eas *EnhancedAIService) AnalyzeSentiment(ctx context.Context, stockCode string, days int) (*EnhancedAIResult, error) {
	req := &AIAnalysisRequest{
		StockCode:     stockCode,
		AnalysisType:  "sentiment_analysis",
		Query:          fmt.Sprintf("分析%s近%d天的市场情感和趋势", stockCode, days),
		Context: map[string]interface{}{
			"analysis_days": days,
			"include_news": true,
			"social_media": true,
		},
		Priority:      "medium",
		Timeout:       20 * time.Second,
	}

	return eas.AnalyzeStock(ctx, req)
}

// AnalyzeTechnical 分析技术面
func (eas *EnhancedAIService) AnalyzeTechnical(ctx context.Context, stockCode string, indicators []string) (*EnhancedAIResult, error) {
	req := &AIAnalysisRequest{
		StockCode:     stockCode,
		AnalysisType:  "technical_analysis",
		Query:          fmt.Sprintf("分析%s的技术指标: %v", stockCode, indicators),
		Context: map[string]interface{}{
			"indicators": indicators,
			"timeframe":  "multi_timeframe",
		},
		Priority:      "high",
		Timeout:       25 * time.Second,
	}

	return eas.AnalyzeStock(ctx, req)
}

// AnalyzeFundamental 分析基本面
func (eas *EnhancedAIService) AnalyzeFundamental(ctx context.Context, stockCode string) (*EnhancedAIResult, error) {
	req := &AIAnalysisRequest{
		StockCode:     stockCode,
		AnalysisType:  "fundamental_analysis",
		Query:          fmt.Sprintf("分析%s的基本面情况和投资价值", stockCode),
		Context: map[string]interface{}{
			"analysis_depth": "comprehensive",
			"include_peer":  true,
			"industry":     true,
		},
		Priority:      "medium",
		Timeout:       30 * time.Second,
	}

	return eas.AnalyzeStock(ctx, req)
}

// AnalyzeNewsEnhanced 增强新闻分析
func (eas *EnhancedAIService) AnalyzeNewsEnhanced(ctx context.Context, stockCode string, days int) (*EnhancedAIResult, error) {
	// 获取新闻数据
	newsResult, err := eas.newsDataService.FetchAndAnalyzeNews(&models.NewsAnalysisRequest{
		StockCode:     stockCode,
		Days:          days,
		Sources:       []string{"eastmoney", "tonghuashun"},
		Categories:    []string{"个股新闻", "公司公告", "行业动态"},
		IncludeSocial: true,
		Language:      "zh",
	})

	if err != nil {
		return nil, fmt.Errorf("获取新闻分析失败: %v", err)
	}

	req := &AIAnalysisRequest{
		StockCode:     stockCode,
		AnalysisType:  "news_enhanced_analysis",
		Query:          fmt.Sprintf("基于新闻数据分析%s的投资机会和风险", stockCode),
		Context: map[string]interface{}{
			"news_summary":     newsResult,
			"sentiment_score":   newsResult.SentimentScore,
			"key_topics":       newsResult.KeyTopics,
			"total_news":       newsResult.TotalNews,
			"positive_news":    newsResult.PositiveNews,
			"negative_news":    newsResult.NegativeNews,
		},
		Priority:      "high",
		Timeout:       35 * time.Second,
	}

	return eas.AnalyzeStock(ctx, req)
}

// GenerateInvestmentReport 生成投资报告
func (eas *EnhancedAIService) GenerateInvestmentReport(ctx context.Context, stockCode string) (*EnhancedAIResult, error) {
	// 并发获取多维度分析
	var wg sync.WaitGroup
	// var mutex sync.Mutex // 暂时不需要
	var technicalResult, fundamentalResult, newsResult *EnhancedAIResult
	var technicalErr, fundamentalErr, newsErr error

	// 技术面分析
	wg.Add(1)
	go func() {
		defer wg.Done()
		technicalResult, technicalErr = eas.AnalyzeTechnical(ctx, stockCode,
			[]string{"MACD", "RSI", "KDJ", "MA", "BOLL", "CCI", "WR"})
	}()

	// 基本面分析
	wg.Add(1)
	go func() {
		defer wg.Done()
		fundamentalResult, fundamentalErr = eas.AnalyzeFundamental(ctx, stockCode)
	}()

	// 新闻面分析
	wg.Add(1)
	go func() {
		defer wg.Done()
		newsResult, newsErr = eas.AnalyzeNewsEnhanced(ctx, stockCode, 30)
	}()

	wg.Wait()

	// 检查错误
	if technicalErr != nil || fundamentalErr != nil || newsErr != nil {
		return nil, fmt.Errorf("综合分析失败: 技术面=%v, 基本面=%v, 新闻面=%v",
			technicalErr, fundamentalErr, newsErr)
	}

	// 生成综合投资报告
	reportQuery := fmt.Sprintf("基于技术面、基本面和新闻面分析，为%s生成投资建议和风险评级", stockCode)

	reportReq := &AIAnalysisRequest{
		StockCode:     stockCode,
		AnalysisType:  "investment_report",
		Query:          reportQuery,
		Context: map[string]interface{}{
			"technical_analysis":  technicalResult,
			"fundamental_analysis": fundamentalResult,
			"news_analysis":      newsResult,
		},
		Priority:      "high",
		Timeout:       45 * time.Second,
	}

	report, err := eas.AnalyzeStock(ctx, reportReq)
	if err != nil {
		return nil, fmt.Errorf("生成投资报告失败: %v", err)
	}

	// 增强报告结果
	report.Insights = append([]string{
		"综合技术面、基本面和新闻面分析",
		"结合量化指标和AI智能分析",
		"提供多维度投资建议",
	}, technicalResult.Insights...)

	report.Recommendations = append([]string{
		"建议结合多个分析维度进行决策",
		"注意风险控制，分散投资",
	}, technicalResult.Recommendations...)

	eas.logger.Info("投资报告生成完成: %s", stockCode)
	return report, nil
}

// buildEnhancedPrompt 构建增强提示
func (eas *EnhancedAIService) buildEnhancedPrompt(req *AIAnalysisRequest) string {
	basePrompt := req.Query

	// 根据分析类型添加特定的指导
	switch req.AnalysisType {
	case "sentiment_analysis":
		return basePrompt + `

请提供专业的情感分析，包括：
1. 市场整体情感倾向（乐观/悲观/中性）
2. 情感强度评分（-1到1）
3. 主要影响因素
4. 短期情感趋势
5. 风险提示和投资建议

请基于金融专业知识，提供准确、客观的分析。`
	case "technical_analysis":
		return basePrompt + `

请提供专业的技术分析，包括：
1. 各技术指标的当前状态和信号
2. 趋势判断和支撑阻力位
3. 买卖信号和时机建议
4. 风险控制和止损建议

请结合多个时间维度进行综合分析。`
	case "fundamental_analysis":
		return basePrompt + `

请提供专业的基本面分析，包括：
1. 财务健康状况评估
2. 估值水平和投资价值
3. 行业地位和竞争优势
4. 增长潜力和风险因素
5. 长期投资建议

请基于价值投资理念提供分析。`
	default:
		return basePrompt
	}
}

// enhanceResult 增强结果
func (eas *EnhancedAIService) enhanceResult(req *AIAnalysisRequest, originalResult interface{}, executionTime time.Duration) *EnhancedAIResult {
	if originalResult == nil {
		return nil
	}

	// 简化实现，直接返回基本结果
	responseJSON := fmt.Sprintf(`{"stock_code":"%s","analysis_type":"%s","confidence":0.8}`, req.StockCode, req.AnalysisType)

	return &EnhancedAIResult{
		StockCode:     req.StockCode,
		AnalysisType:  req.AnalysisType,
		Response:      responseJSON,
		Confidence:    0.8,
		Insights:      []string{"基于AI分析的洞察"},
		Recommendations: []string{"建议持续观察"},
		RiskWarnings:  []string{},
		Metadata:      map[string]interface{}{"enhanced": true},
		ExecutionTime:   executionTime,
		CacheHit:       false,
		CreatedAt:       time.Now(),
	}
}

// fuseModelResults 融合多个模型的结果
func (eas *EnhancedAIService) fuseModelResults(req *AIAnalysisRequest, results []ModelResult) *EnhancedAIResult {
	if len(results) == 0 {
		return &EnhancedAIResult{
			StockCode:     req.StockCode,
			AnalysisType:  req.AnalysisType,
			Query:         req.Query,
			Response:      "无可用模型结果",
			Confidence:    0.0,
			CacheHit:      false,
			CreatedAt:     time.Now(),
		}
	}

	// 按置信度排序
	sort.Slice(results, func(i, j int) bool {
		return results[i].Confidence > results[j].Confidence
	})

	// 融合逻辑
	var bestResponses []string
	var totalConfidence float64

	for _, result := range results {
		if result.ModelType == "success" && result.Confidence > 0.5 {
			bestResponses = append(bestResponses, result.Response)
			totalConfidence += result.Confidence
		}
	}

	// 构建融合响应
	fusedResponse := eas.buildFusedResponse(bestResponses, totalConfidence)

	return &EnhancedAIResult{
		StockCode:     req.StockCode,
		AnalysisType:  req.AnalysisType,
		Query:         req.Query,
		Response:      fusedResponse,
		Confidence:      totalConfidence / float64(len(bestResponses)),
		Models:         results,
		Insights: []string{
			"融合多个AI模型的分析结果",
			"采用置信度最高的模型建议",
			"综合不同模型的优势和观点",
		},
		Recommendations: []string{
			"建议结合多个模型的建议进行决策",
			"关注模型间的一致性",
		},
		CacheHit:       false,
		CreatedAt:     time.Now(),
	}
}

// extractInsights 提取洞察
func (eas *EnhancedAIService) extractInsights(content string) []string {
	var insights []string

	// 简单的关键词提取逻辑
	lines := strings.Split(content, "\n")
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if strings.Contains(line, "洞察") ||
		   strings.Contains(line, "分析显示") ||
		   strings.Contains(line, "值得注意的是") ||
		   strings.Contains(line, "重要发现") {
			insights = append(insights, line)
		}
	}

	if len(insights) == 0 {
		insights = []string{"基于AI分析的综合洞察"}
	}

	return insights
}

// extractRecommendations 提取建议
func (eas *EnhancedAIService) extractRecommendations(content string) []string {
	var recommendations []string

	lines := strings.Split(content, "\n")
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if strings.Contains(line, "建议") ||
		   strings.Contains(line, "推荐") ||
		   strings.Contains(line, "应该") ||
		   strings.Contains(line, "可以考虑") {
			recommendations = append(recommendations, line)
		}
	}

	if len(recommendations) == 0 {
		recommendations = []string{"请谨慎投资，注意风险控制"}
	}

	return recommendations
}

// extractRiskWarnings 提取风险警告
func (eas *EnhancedAIService) extractRiskWarnings(content string) []string {
	var warnings []string

	lines := strings.Split(content, "\n")
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if strings.Contains(line, "风险") ||
		   strings.Contains(line, "警告") ||
		   strings.Contains(line, "注意") ||
		   strings.Contains(line, "警惕") {
			warnings = append(warnings, line)
		}
	}

	if len(warnings) == 0 {
		warnings = []string{"投资有风险，请谨慎决策"}
	}

	return warnings
}

// buildFusedResponse 构建融合响应
func (eas *EnhancedAIService) buildFusedResponse(responses []string, confidence float64) string {
	if len(responses) == 0 {
		return "多个模型均未能提供有效分析"
	}

	return fmt.Sprintf(`基于多模型AI分析（置信度: %.2f）:

%s

综合建议：请基于以上分析进行投资决策，注意风险控制。`,
		confidence, strings.Join(responses, "\n\n"))
}

// generateCacheKey 生成缓存键
func (eas *EnhancedAIService) generateCacheKey(req *AIAnalysisRequest) string {
	key := fmt.Sprintf("%s_%s_%s", req.StockCode, req.AnalysisType, req.Query)

	// 添加上下文哈希
	if len(req.Context) > 0 {
		contextJSON, _ := json.Marshal(req.Context)
		key += "_" + fmt.Sprintf("%x", len(contextJSON)) // 简单哈希
	}

	return key
}

// getFromCache 从缓存获取
func (eas *EnhancedAIService) getFromCache(key string) *AICacheItem {
	eas.cacheMutex.RLock()
	defer eas.cacheMutex.RUnlock()

	if item, exists := eas.cache[key]; exists {
		// 检查是否过期
		if time.Since(item.Timestamp) < item.TTL {
			return item
		}
		// 过期则删除
		delete(eas.cache, key)
	}

	return nil
}

// saveToCache 保存到缓存
func (eas *EnhancedAIService) saveToCache(key string, data interface{}, ttl time.Duration) {
	eas.cacheMutex.Lock()
	defer eas.cacheMutex.Unlock()

	eas.cache[key] = &AICacheItem{
		Data:      data,
		Timestamp: time.Now(),
		TTL:       ttl,
	}
}

// ClearCache 清理缓存
func (eas *EnhancedAIService) ClearCache() {
	eas.cacheMutex.Lock()
	defer eas.cacheMutex.Unlock()

	eas.cache = make(map[string]*AICacheItem)
	eas.logger.Info("AI分析缓存已清理")
}

// GetCacheStats 获取缓存统计
func (eas *EnhancedAIService) GetCacheStats() map[string]interface{} {
	eas.cacheMutex.RLock()
	defer eas.cacheMutex.RUnlock()

	validCount := 0
	for _, item := range eas.cache {
		if time.Since(item.Timestamp) < item.TTL {
			validCount++
		}
	}

	return map[string]interface{}{
		"total_entries": len(eas.cache),
		"valid_entries": validCount,
		"hit_rate":      float64(validCount) / float64(len(eas.cache)) * 100,
	}
}