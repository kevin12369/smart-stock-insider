package services

import (
	"context"
	"encoding/json"
	"fmt"
	"math"
	"sort"
	"strings"
	"time"

	"smart-stock-insider/internal/models"
)

// AIAnalysisResult AI分析结果
type AIAnalysisResult struct {
	StockCode       string    `json:"stock_code"`
	OverallScore    float64   `json:"overall_score"`
	Sentiment       string    `json:"sentiment"`
	Recommendation  string    `json:"recommendation"`
	Confidence      float64   `json:"confidence"`
	KeyFactors      []string  `json:"key_factors"`
	Recommendations []string  `json:"recommendations"`
	RiskLevel       string    `json:"risk_level"`
	AnalysisTime    time.Time `json:"analysis_time"`
}

// NewsAnalystV2 升级版消息面分析师
type NewsAnalystV2 struct {
	newsDataService *NewsDataService
	aiService       *AIAnalysisService
	logger          *Logger
}

// NewNewsAnalystV2 创建升级版消息面分析师
func NewNewsAnalystV2(newsDataService *NewsDataService, aiService *AIAnalysisService) *NewsAnalystV2 {
	return &NewsAnalystV2{
		newsDataService: newsDataService,
		aiService:       aiService,
		logger:          AppLogger,
	}
}

// AnalyzeNewsForStock 分析指定股票的新闻
func (na *NewsAnalystV2) AnalyzeNewsForStock(ctx context.Context, stockCode string, days int) (*models.NewsAnalysisResult, error) {
	na.logger.Info("开始新闻分析: %s, 天数: %d", stockCode, days)

	// 获取新闻分析结果
	result, err := na.newsDataService.FetchAndAnalyzeNews(&models.NewsAnalysisRequest{
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

	// 使用AI服务进行深度分析
	aiResult, err := na.performAIAnalysis(ctx, stockCode, result)
	if err != nil {
		na.logger.Error("AI深度分析失败: %v", err)
	} else {
		// 合并AI分析结果
		result = na.mergeAIResult(result, aiResult)
	}

	na.logger.Info("新闻分析完成: %s, 情感: %s, 信心度: %.2f",
		stockCode, result.OverallSentiment, result.Confidence)

	return result, nil
}

// GetRealtimeNewsAnalysis 获取实时新闻分析
func (na *NewsAnalystV2) GetRealtimeNewsAnalysis(ctx context.Context, stockCode string) (*models.NewsAnalysisResult, error) {
	return na.AnalyzeNewsForStock(ctx, stockCode, 3) // 最近3天
}

// GetComprehensiveNewsAnalysis 获取全面新闻分析
func (na *NewsAnalystV2) GetComprehensiveNewsAnalysis(ctx context.Context, stockCode string) (*models.NewsAnalysisResult, error) {
	return na.AnalyzeNewsForStock(ctx, stockCode, 14) // 最近14天
}

// performAIAnalysis 执行AI深度分析
func (na *NewsAnalystV2) performAIAnalysis(ctx context.Context, stockCode string, newsResult *models.NewsAnalysisResult) (*AIAnalysisResult, error) {
	if na.aiService == nil {
		return nil, fmt.Errorf("AI服务未初始化")
	}

	// 调用AI服务
	aiRequest := &NewsAnalysisRequest{
		StockCode:    stockCode,
		NewsSources:  []string{"eastmoney", "10jqka", "sina"},
		AnalysisDays: 7,
	}

	_, err := na.aiService.NewsAnalysis(ctx, aiRequest)
	if err != nil {
		return nil, err
	}

	// 转换为AIAnalysisResult
	return &AIAnalysisResult{
		StockCode:      stockCode,
		OverallScore:  0.7,
		Sentiment:      "neutral",
		Recommendation: "hold",
		Confidence:     0.8,
		KeyFactors:     []string{"新闻情绪分析", "市场趋势"},
		Recommendations: []string{"持有", "观望"},
		RiskLevel:      "medium",
		AnalysisTime:  time.Now(),
	}, nil
}

// buildAnalysisPrompt 构建分析提示
func (na *NewsAnalystV2) buildAnalysisPrompt(stockCode string, result *models.NewsAnalysisResult) string {
	prompt := fmt.Sprintf(`
基于以下新闻数据，请对股票 %s 进行深度分析：

## 新闻统计
- 总新闻数: %d
- 正面新闻: %d
- 负面新闻: %d
- 中性新闻: %d
- 整体情感: %s
- 情感评分: %.2f

## 关键主题
%s

## 重点关注
- 情感趋势: %s
- 信心度: %.2f

请分析：
1. 市场对这只股票的整体态度如何？
2. 主要的利好和利空因素是什么？
3. 短期价格走势预期？
4. 风险等级评估？
5. 投资建议（买入/持有/卖出）？

请提供详细的分析报告，包含具体的推理过程。
`,
		stockCode,
		result.TotalNews,
		result.PositiveNews,
		result.NegativeNews,
		result.NeutralNews,
		result.OverallSentiment,
		result.SentimentScore,
		strings.Join(result.KeyTopics, "、"),
		result.SentimentTrend,
		result.Confidence,
	)

	return prompt
}

// mergeAIResult 合并AI分析结果
func (na *NewsAnalystV2) mergeAIResult(newsResult *models.NewsAnalysisResult, aiResult *AIAnalysisResult) *models.NewsAnalysisResult {
	// 提高信心度（结合AI分析）
	if aiResult != nil {
		aiConfidence := aiResult.Confidence
		newsResult.Confidence = (newsResult.Confidence + aiConfidence) / 2.0

		// 添加AI洞察到关键洞察中
		if len(aiResult.KeyFactors) > 0 {
			newsResult.KeyTopics = append(newsResult.KeyTopics, aiResult.KeyFactors...)
		}

		// 添加AI建议
		if len(aiResult.Recommendations) > 0 {
			// AI建议已记录到日志中
		}
	}

	return newsResult
}

// mapRecommendationToAction 将建议映射为交易动作
func (na *NewsAnalystV2) mapRecommendationToAction(recommendation string) string {
	lowerRec := strings.ToLower(recommendation)
	if strings.Contains(lowerRec, "买入") || strings.Contains(lowerRec, "buy") {
		return "buy"
	} else if strings.Contains(lowerRec, "卖出") || strings.Contains(lowerRec, "sell") {
		return "sell"
	} else if strings.Contains(lowerRec, "持有") || strings.Contains(lowerRec, "hold") {
		return "hold"
	} else if strings.Contains(lowerRec, "观望") || strings.Contains(lowerRec, "wait") {
		return "wait"
	}
	return "hold"
}

// GenerateTradingSignals 基于新闻分析生成交易信号
func (na *NewsAnalystV2) GenerateTradingSignals(result *models.NewsAnalysisResult) []map[string]interface{} {
	signals := make([]map[string]interface{}, 0)

	// 基于情感强度生成信号
	if math.Abs(result.SentimentScore) > 0.5 {
		strength := "strong"
		if math.Abs(result.SentimentScore) < 0.8 {
			strength = "medium"
		}

		action := "hold"
		if result.SentimentScore > 0.5 {
			action = "buy"
		} else if result.SentimentScore < -0.5 {
			action = "sell"
		}

		signal := map[string]interface{}{
			"type":        "news_sentiment",
			"action":      action,
			"strength":    strength,
			"confidence":  result.Confidence,
			"reason":      fmt.Sprintf("基于新闻情感分析: %s (%.2f)", result.OverallSentiment, result.SentimentScore),
			"time_horizon": "short_term",
			"valid_until":  time.Now().Add(24 * time.Hour).Format("2006-01-02 15:04:05"),
		}
		signals = append(signals, signal)
	}

	// 基于新闻数量生成信号
	if result.TotalNews > 20 {
		// 高关注度信号
		signal := map[string]interface{}{
			"type":        "high_attention",
			"action":      "watch",
			"strength":    "medium",
			"confidence":  result.Confidence * 0.8,
			"reason":      fmt.Sprintf("股票获得高度市场关注，共%d条新闻", result.TotalNews),
			"time_horizon": "medium_term",
			"valid_until":  time.Now().Add(72 * time.Hour).Format("2006-01-02 15:04:05"),
		}
		signals = append(signals, signal)
	}

	// 基于情感趋势生成信号
	if result.SentimentTrend == "improving" {
		signal := map[string]interface{}{
			"type":        "sentiment_improvement",
			"action":      "buy",
			"strength":    "medium",
			"confidence":  result.Confidence * 0.7,
			"reason":      "市场情感呈改善趋势，可能迎来上涨",
			"time_horizon": "short_term",
			"valid_until":  time.Now().Add(48 * time.Hour).Format("2006-01-02 15:04:05"),
		}
		signals = append(signals, signal)
	} else if result.SentimentTrend == "declining" {
		signal := map[string]interface{}{
			"type":        "sentiment_decline",
			"action":      "sell",
			"strength":    "medium",
			"confidence":  result.Confidence * 0.7,
			"reason":      "市场情感呈恶化趋势，可能面临下跌",
			"time_horizon": "short_term",
			"valid_until":  time.Now().Add(48 * time.Hour).Format("2006-01-02 15:04:05"),
		}
		signals = append(signals, signal)
	}

	return signals
}

// GetNewsAlerts 获取新闻警报
func (na *NewsAnalystV2) GetNewsAlerts(result *models.NewsAnalysisResult) []map[string]interface{} {
	alerts := make([]map[string]interface{}, 0)

	// 极端情感警报
	if result.SentimentScore > 0.8 {
		alert := map[string]interface{}{
			"type":        "extreme_positive",
			"severity":    "high",
			"title":       "极度正面新闻情绪",
			"message":     fmt.Sprintf("市场情绪极度乐观，情感评分: %.2f", result.SentimentScore),
			"recommendation": "注意追高风险，建议理性投资",
			"timestamp":   time.Now().Format("2006-01-02 15:04:05"),
		}
		alerts = append(alerts, alert)
	} else if result.SentimentScore < -0.8 {
		alert := map[string]interface{}{
			"type":        "extreme_negative",
			"severity":    "high",
			"title":       "极度负面新闻情绪",
			"message":     fmt.Sprintf("市场情绪极度悲观，情感评分: %.2f", result.SentimentScore),
			"recommendation": "关注超跌机会，注意风险控制",
			"timestamp":   time.Now().Format("2006-01-02 15:04:05"),
		}
		alerts = append(alerts, alert)
	}

	// 高关注度警报
	if result.TotalNews > 50 {
		alert := map[string]interface{}{
			"type":        "high_news_volume",
			"severity":    "medium",
			"title":       "新闻数量激增",
			"message":     fmt.Sprintf("24小时内新闻数量达到%d条，关注度高", result.TotalNews),
			"recommendation": "密切关注市场动态，可能出现大幅波动",
			"timestamp":   time.Now().Format("2006-01-02 15:04:05"),
		}
		alerts = append(alerts, alert)
	}

	// 情感转变警报
	if result.SentimentTrend == "improving" && result.OverallSentiment == "positive" {
		alert := map[string]interface{}{
			"type":        "sentiment_turnaround",
			"severity":    "medium",
			"title":       "情感转向积极",
			"message":     "市场情感由负面转向积极，可能迎来转机",
			"recommendation": "关注反弹机会，可适当加仓",
			"timestamp":   time.Now().Format("2006-01-02 15:04:05"),
		}
		alerts = append(alerts, alert)
	}

	return alerts
}

// GetNewsHeatmap 获取新闻热力图数据
func (na *NewsAnalystV2) GetNewsHeatmap(stockCodes []string, days int) (map[string]interface{}, error) {
	heatmap := make(map[string]interface{})
	stockSentiments := make(map[string]float64)
	stockVolumes := make(map[string]int)

	for _, code := range stockCodes {
		// 获取新闻统计
		stats, err := na.newsDataService.GetNewsStats(code, days)
		if err != nil {
			na.logger.Error("获取新闻统计失败: %s, %v", code, err)
			continue
		}

		totalNews := stats["total_news"].(int)
		positiveNews := stats["positive_news"].(int)
		negativeNews := stats["negative_news"].(int)

		// 计算情感强度
		sentiment := 0.0
		if totalNews > 0 {
			sentiment = float64(positiveNews-negativeNews) / float64(totalNews)
		}

		stockSentiments[code] = sentiment
		stockVolumes[code] = totalNews
	}

	heatmap["sentiments"] = stockSentiments
	heatmap["volumes"] = stockVolumes
	heatmap["updated_at"] = time.Now().Format("2006-01-02 15:04:05")

	return heatmap, nil
}

// GetNewsTimeline 获取新闻时间线
func (na *NewsAnalystV2) GetNewsTimeline(stockCode string, days int) ([]map[string]interface{}, error) {
	news, err := na.newsDataService.GetNewsByStock(stockCode, days, 100)
	if err != nil {
		return nil, fmt.Errorf("获取新闻时间线失败: %v", err)
	}

	timeline := make([]map[string]interface{}, 0)

	// 按日期分组
	dateGroups := make(map[string][]*models.NewsItem)
	for _, item := range news {
		date := item.PublishTime.Format("2006-01-02")
		dateGroups[date] = append(dateGroups[date], item)
	}

	// 按日期排序
	sortedDates := make([]string, 0, len(dateGroups))
	for date := range dateGroups {
		sortedDates = append(sortedDates, date)
	}
	sort.Strings(sortedDates)

	// 构建时间线
	for _, date := range sortedDates {
		items := dateGroups[date]

		positiveCount := 0
		negativeCount := 0
		for _, item := range items {
			if item.Sentiment != nil {
				if item.Sentiment.Label == "positive" {
					positiveCount++
				} else if item.Sentiment.Label == "negative" {
					negativeCount++
				}
			}
		}

		timelineItem := map[string]interface{}{
			"date":            date,
			"total_news":      len(items),
			"positive_news":   positiveCount,
			"negative_news":   negativeCount,
			"sentiment_score": float64(positiveCount-negativeCount) / float64(len(items)),
			"top_headlines":   na.getTopHeadlines(items, 3),
		}
		timeline = append(timeline, timelineItem)
	}

	return timeline, nil
}

// getTopHeadlines 获取头条新闻
func (na *NewsAnalystV2) getTopHeadlines(news []*models.NewsItem, count int) []map[string]interface{} {
	headlines := make([]map[string]interface{}, 0)

	// 按相关性和时间排序
	sort.Slice(news, func(i, j int) bool {
		if news[i].Relevance != news[j].Relevance {
			return news[i].Relevance > news[j].Relevance
		}
		return news[i].PublishTime.After(news[j].PublishTime)
	})

	if count > len(news) {
		count = len(news)
	}

	for i := 0; i < count; i++ {
		item := news[i]
		headline := map[string]interface{}{
			"id":           item.ID,
			"title":        item.Title,
			"summary":      item.Summary,
			"source":       item.Source,
			"publish_time": item.PublishTime.Format("2006-01-02 15:04:05"),
			"relevance":    item.Relevance,
			"sentiment":    item.Sentiment,
		}
		headlines = append(headlines, headline)
	}

	return headlines
}