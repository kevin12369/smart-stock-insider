package services

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"strings"
	"sync"
	"time"

	"smart-stock-insider/internal/models"
)

// NewsDataService 新闻数据服务
type NewsDataService struct {
	repository *models.NewsRepository
	mutex      sync.RWMutex
	logger      *Logger
}

// NewNewsDataService 创建新闻数据服务
func NewNewsDataService(db *sql.DB) *NewsDataService {
	// 创建新闻相关表
	if err := models.CreateNewsTables(db); err != nil {
		AppLogger.Error("创建新闻表失败: %v", err)
	}

	repository := models.NewNewsRepository(db)

	return &NewsDataService{
		repository: repository,
		logger:     AppLogger,
	}
}

// FetchAndAnalyzeNews 获取并分析新闻
func (nds *NewsDataService) FetchAndAnalyzeNews(req *models.NewsAnalysisRequest) (*models.NewsAnalysisResult, error) {
	nds.logger.Info("开始获取和分析新闻: %s", req.StockCode)

	// 首先检查缓存
	cached, err := nds.repository.GetAnalysisCache(req.StockCode, req.Days)
	if err != nil {
		nds.logger.Error("获取分析缓存失败: %v", err)
	} else if cached != nil {
		// 检查缓存是否过期（1小时）
		if time.Since(cached.AnalysisTime) < time.Hour {
			nds.logger.Info("使用缓存的分析结果: %s", req.StockCode)
			return cached, nil
		}
	}

	// 创建新闻服务获取实时新闻
	// 这里需要传入DataService，暂时创建一个模拟的
	newsService := NewNewsService(nil) // 实际使用时应该传入真实的DataService

	// 获取新闻
	result, err := newsService.FetchNews(nil, req)
	if err != nil {
		return nil, fmt.Errorf("获取新闻失败: %v", err)
	}

	// 保存新闻到数据库
	err = nds.saveNewsItems(result.TopHeadlines)
	if err != nil {
		nds.logger.Error("保存新闻失败: %v", err)
		// 不影响主流程，继续返回分析结果
	}

	// 保存分析结果到缓存
	err = nds.repository.SaveAnalysisCache(result)
	if err != nil {
		nds.logger.Error("保存分析缓存失败: %v", err)
	}

	nds.logger.Info("新闻分析完成: %s, 总数: %d", req.StockCode, result.TotalNews)
	return result, nil
}

// saveNewsItems 保存新闻条目
func (nds *NewsDataService) saveNewsItems(newsItems []models.NewsItem) error {
	for i := range newsItems {
		err := nds.repository.SaveNewsItem(&newsItems[i])
		if err != nil {
			nds.logger.Error("保存新闻条目失败: %v", err)
			// 继续保存其他条目
		}
	}
	return nil
}

// GetNewsItems 获取新闻列表
func (nds *NewsDataService) GetNewsItems(filter *models.NewsFilter, limit, offset int) ([]*models.NewsItem, error) {
	nds.logger.Debug("获取新闻列表: limit=%d, offset=%d", limit, offset)

	return nds.repository.GetNewsItems(filter, limit, offset)
}

// GetNewsByStock 获取指定股票的新闻
func (nds *NewsDataService) GetNewsByStock(stockCode string, days int, limit int) ([]*models.NewsItem, error) {
	filter := &models.NewsFilter{
		StockCodes:   []string{stockCode},
		MinRelevance: 0.5,
	}

	if days > 0 {
		endTime := time.Now()
		startTime := endTime.AddDate(0, 0, -days)
		filter.StartTime = &startTime
		filter.EndTime = &endTime
	}

	items, err := nds.repository.GetNewsItems(filter, limit, 0)
	if err != nil {
		return nil, fmt.Errorf("获取股票新闻失败: %v", err)
	}

	return items, nil
}

// GetNewsSources 获取新闻源
func (nds *NewsDataService) GetNewsSources() ([]*models.NewsSource, error) {
	return nds.repository.GetNewsSources()
}

// AddNewsSource 添加新闻源
func (nds *NewsDataService) AddNewsSource(source *models.NewsSource) error {
	err := nds.repository.SaveNewsSource(source)
	if err != nil {
		return fmt.Errorf("添加新闻源失败: %v", err)
	}

	nds.logger.Info("添加新闻源成功: %s", source.Name)
	return nil
}

// GetNewsStats 获取新闻统计
func (nds *NewsDataService) GetNewsStats(stockCode string, days int) (map[string]interface{}, error) {
	stats, err := nds.repository.GetNewsStats(stockCode, days)
	if err != nil {
		return nil, fmt.Errorf("获取新闻统计失败: %v", err)
	}

	return stats, nil
}

// GetSentimentAnalysis 获取情感分析
func (nds *NewsDataService) GetSentimentAnalysis(stockCode string, days int) (*models.NewsAnalysisResult, error) {
	// 构建分析请求
	req := &models.NewsAnalysisRequest{
		StockCode:  stockCode,
		Days:       days,
		Sources:    []string{"eastmoney", "tonghuashun"},
		Categories: []string{},
		Language:   "zh",
	}

	return nds.FetchAndAnalyzeNews(req)
}

// SearchNews 搜索新闻
func (nds *NewsDataService) SearchNews(keyword string, stockCode string, limit int) ([]*models.NewsItem, error) {
	// 这里简化实现，实际应该添加全文搜索功能
	filter := &models.NewsFilter{
		MinRelevance: 0.3,
	}

	if stockCode != "" {
		filter.StockCodes = []string{stockCode}
	}

	items, err := nds.repository.GetNewsItems(filter, limit, 0)
	if err != nil {
		return nil, fmt.Errorf("搜索新闻失败: %v", err)
	}

	// 简单的关键词过滤
	if keyword != "" {
		var filteredItems []*models.NewsItem
		for _, item := range items {
			if strings.Contains(item.Title, keyword) ||
			   strings.Contains(item.Summary, keyword) ||
			   strings.Contains(item.Content, keyword) {
				filteredItems = append(filteredItems, item)
			}
		}
		return filteredItems, nil
	}

	return items, nil
}

// GetHotNews 获取热门新闻
func (nds *NewsDataService) GetHotNews(limit int) ([]*models.NewsItem, error) {
	filter := &models.NewsFilter{
		MinRelevance: 0.7,
	}

	items, err := nds.repository.GetNewsItems(filter, limit, 0)
	if err != nil {
		return nil, fmt.Errorf("获取热门新闻失败: %v", err)
	}

	return items, nil
}

// GetNewsByCategory 获取指定分类的新闻
func (nds *NewsDataService) GetNewsByCategory(category string, limit int) ([]*models.NewsItem, error) {
	filter := &models.NewsFilter{
		Categories:   []string{category},
		MinRelevance: 0.5,
	}

	items, err := nds.repository.GetNewsItems(filter, limit, 0)
	if err != nil {
		return nil, fmt.Errorf("获取分类新闻失败: %v", err)
	}

	return items, nil
}

// GetNewsBySentiment 获取指定情感的新闻
func (nds *NewsDataService) GetNewsBySentiment(sentiment string, limit int) ([]*models.NewsItem, error) {
	filter := &models.NewsFilter{
		Sentiment:    sentiment,
		MinRelevance: 0.5,
	}

	items, err := nds.repository.GetNewsItems(filter, limit, 0)
	if err != nil {
		return nil, fmt.Errorf("获取情感新闻失败: %v", err)
	}

	return items, nil
}

// GetLatestNews 获取最新新闻
func (nds *NewsDataService) GetLatestNews(limit int) ([]*models.NewsItem, error) {
	filter := &models.NewsFilter{
		MinRelevance: 0.3,
	}

	// 设置时间范围，获取最近24小时
	endTime := time.Now()
	startTime := endTime.Add(-24 * time.Hour)
	filter.StartTime = &startTime
	filter.EndTime = &endTime

	items, err := nds.repository.GetNewsItems(filter, limit, 0)
	if err != nil {
		return nil, fmt.Errorf("获取最新新闻失败: %v", err)
	}

	return items, nil
}

// CleanOldNews 清理旧新闻
func (nds *NewsDataService) CleanOldNews(days int) error {
	// 这里可以实现清理逻辑，删除超过指定天数的新闻
	nds.logger.Info("清理 %d 天前的旧新闻", days)

	// 示例SQL
	// query := `DELETE FROM news_items WHERE created_at < datetime('now', '-' || ? || ' days')`
	// _, err := nds.repository.db.Exec(query, days)
	// return err

	return nil
}

// RefreshNewsSources 刷新新闻源
func (nds *NewsDataService) RefreshNewsSources() error {
	sources, err := nds.GetNewsSources()
	if err != nil {
		return fmt.Errorf("获取新闻源失败: %v", err)
	}

	for _, source := range sources {
		// 更新新闻源的最后获取时间
		source.LastFetch = time.Now()
		err = nds.repository.SaveNewsSource(source)
		if err != nil {
			nds.logger.Error("更新新闻源失败: %s, %v", source.Name, err)
		}
	}

	return nil
}

// GetNewsSummary 获取新闻摘要
func (nds *NewsDataService) GetNewsSummary(stockCode string, days int) (map[string]interface{}, error) {
	stats, err := nds.GetNewsStats(stockCode, days)
	if err != nil {
		return nil, err
	}

	// 获取最新的几条新闻
	latestNews, err := nds.GetNewsByStock(stockCode, days, 5)
	if err != nil {
		return nil, err
	}

	summary := map[string]interface{}{
		"stats":       stats,
		"latest_news": latestNews,
		"summary":     nds.generateNewsSummary(stats, latestNews),
	}

	return summary, nil
}

// generateNewsSummary 生成新闻摘要
func (nds *NewsDataService) generateNewsSummary(stats map[string]interface{}, latestNews []*models.NewsItem) string {
	totalNews := stats["total_news"].(int)
	positiveNews := stats["positive_news"].(int)
	negativeNews := stats["negative_news"].(int)

	summary := fmt.Sprintf("共获取%d条新闻，其中正面%d条，负面%d条。",
		totalNews, positiveNews, negativeNews)

	if totalNews > 0 {
		sentimentRatio := float64(positiveNews) / float64(totalNews) * 100
		summary += fmt.Sprintf(" 市场情绪偏向%.0f%%积极。", sentimentRatio)
	}

	if len(latestNews) > 0 {
		summary += fmt.Sprintf(" 最新热点：%s。", latestNews[0].Title)
	}

	return summary
}