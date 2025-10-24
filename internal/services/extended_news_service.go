package services

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"sort"
	"strconv"
	"strings"
	"sync"
	"time"

	"smart-stock-insider/internal/models"
)

// ExtendedNewsService 扩展新闻服务
type ExtendedNewsService struct {
	*NewsService                            // 继承基础新闻服务
	additionalSources map[string]*models.AdditionalNewsSource
	sourceStatus     map[string]*models.NewsSourceStatus
	sourceMetrics    map[string]*models.NewsSourceMetrics
	aggregationRules map[string]*models.NewsAggregationRule
	aggregator      *NewsAggregator                     // 新闻聚合器
	mutex           sync.RWMutex
	logger          *Logger
	httpClient      *http.Client
}

// NewExtendedNewsService 创建扩展新闻服务
func NewExtendedNewsService(baseService *NewsService) *ExtendedNewsService {
	ens := &ExtendedNewsService{
		NewsService:      baseService,
		additionalSources: make(map[string]*models.AdditionalNewsSource),
		sourceStatus:     make(map[string]*models.NewsSourceStatus),
		sourceMetrics:    make(map[string]*models.NewsSourceMetrics),
		aggregationRules:  make(map[string]*models.NewsAggregationRule),
		aggregator:       NewNewsAggregator(),
		httpClient: &http.Client{
			Timeout: 30 * time.Second,
		},
		logger: AppLogger,
	}

	// 初始化扩展新闻源
	ens.initAdditionalSources()
	ens.initAggregationRules()

	// 加载聚合规则到聚合器
	ens.aggregator.LoadAggregationRules(ens.aggregationRules)

	return ens
}

// initAdditionalSources 初始化扩展新闻源
func (ens *ExtendedNewsService) initAdditionalSources() {
	sources := []*models.AdditionalNewsSource{
		{
			ID:        "sina",
			Name:      "新浪财经",
			BaseURL:   "https://finance.sina.com.cn",
			APIKey:    "",
			Enabled:   true,
			RateLimit: 120,
			Priority:  1,
			Category:  "news",
			Description: "新浪财经新闻API",
			Headers: map[string]string{
				"User-Agent":   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
				"Referer":      "https://finance.sina.com.cn/",
				"Accept":       "application/json, text/plain, */*",
			},
		},
		{
			ID:        "tencent",
			Name:      "腾讯财经",
			BaseURL:   "https://finance.qq.com",
			APIKey:    "",
			Enabled:   true,
			RateLimit: 100,
			Priority:  2,
			Category:  "news",
			Description: "腾讯财经新闻API",
			Headers: map[string]string{
				"User-Agent":   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
				"Referer":      "https://finance.qq.com/",
				"Accept":       "application/json",
			},
		},
		{
			ID:        "xueqiu",
			Name:      "雪球",
			BaseURL:   "https://xueqiu.com",
			APIKey:    "",
			Enabled:   true,
			RateLimit: 60,
			Priority:  3,
			Category:  "social",
			Description: "雪球社区动态",
			Headers: map[string]string{
				"User-Agent":   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
				"Referer":      "https://xueqiu.com/",
				"Accept":       "application/json, text/plain, */*",
			},
		},
		{
			ID:        "hexun",
			Name:      "和讯网",
			BaseURL:   "https://news.hexun.com",
			APIKey:    "",
			Enabled:   true,
			RateLimit: 80,
			Priority:  4,
			Category:  "professional",
			Description: "和讯网专业财经新闻",
			Headers: map[string]string{
				"User-Agent":   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
				"Referer":      "https://www.hexun.com/",
				"Accept":       "application/json",
			},
		},
		{
			ID:        "caixin",
			Name:      "财新网",
			BaseURL:   "https://www.caixin.com",
			APIKey:    "",
			Enabled:   false, // 需要授权
			RateLimit: 40,
			Priority:  1,
			Category:  "professional",
			Description: "财新网深度财经报道",
			Headers: map[string]string{
				"User-Agent":   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
				"Referer":      "https://www.caixin.com/",
				"Accept":       "application/json",
			},
		},
		{
			ID:        "wallstreetcn",
			Name:      "华尔街见闻",
			BaseURL:   "https://wallstreetcn.com",
			APIKey:    "",
			Enabled:   false, // 需要授权
			RateLimit: 60,
			Priority:  2,
			Category:  "professional",
			Description: "华尔街见闻实时资讯",
			Headers: map[string]string{
				"User-Agent":   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
				"Referer":      "https://wallstreetcn.com/",
				"Accept":       "application/json",
			},
		},
	}

	for _, source := range sources {
		ens.additionalSources[source.ID] = source
		ens.sourceStatus[source.ID] = &models.NewsSourceStatus{
			SourceID:    source.ID,
			Name:        source.Name,
			Status:      "active",
			LastCheck:   time.Now(),
			ErrorCount:  0,
			SuccessRate: 1.0,
			ResponseTime: 1000,
			UpdatedAt:   time.Now(),
		}
		ens.sourceMetrics[source.ID] = &models.NewsSourceMetrics{
			SourceID:  source.ID,
			Date:      time.Now(),
			LastReset: time.Now(),
		}
	}
}

// initAggregationRules 初始化新闻聚合规则
func (ens *ExtendedNewsService) initAggregationRules() {
	rules := []*models.NewsAggregationRule{
		{
			ID:          "duplicate_title",
			Name:        "标题去重",
			Description: "去除相同标题的新闻",
			RuleType:    "duplicate",
			Conditions: map[string]string{
				"similarity_threshold": "0.9",
				"field":              "title",
			},
			Actions: map[string]string{
				"action":       "deduplicate",
				"keep_source":  "highest_priority",
				"merge_tags":   "true",
			},
			Enabled:  true,
			Priority: 1,
		},
		{
			ID:          "similar_content",
			Name:        "内容相似聚类",
			Description: "对相似内容的新闻进行聚类",
			RuleType:    "similar",
			Conditions: map[string]string{
				"similarity_threshold": "0.7",
				"field":              "content",
				"time_window":         "1h",
			},
			Actions: map[string]string{
				"action":       "cluster",
				"cluster_size": "5",
			},
			Enabled:  true,
			Priority: 2,
		},
		{
			ID:          "trending_topics",
			Name:        "热门话题聚合",
			Description: "识别热门话题并聚合相关新闻",
			RuleType:    "trending",
			Conditions: map[string]string{
				"min_articles":   "3",
				"time_window":    "2h",
				"keyword_match": "true",
			},
			Actions: map[string]string{
				"action":       "create_cluster",
				"auto_summarize": "true",
			},
			Enabled:  true,
			Priority: 3,
		},
	}

	for _, rule := range rules {
		rule.CreatedAt = time.Now()
		rule.UpdatedAt = time.Now()
		ens.aggregationRules[rule.ID] = rule
	}
}

// FetchExtendedNews 获取扩展新闻
func (ens *ExtendedNewsService) FetchExtendedNews(ctx context.Context, req *models.NewsAnalysisRequest) (*models.NewsAnalysisResult, error) {
	ens.logger.Info("开始获取扩展新闻: %s, 天数: %d", req.StockCode, req.Days)

	// 获取基础新闻（东方财富、同花顺）
	baseResult, err := ens.NewsService.FetchNews(ctx, req)
	if err != nil {
		ens.logger.Info("获取基础新闻失败: %v", err)
		baseResult = &models.NewsAnalysisResult{
			TotalNews: 0,
		}
	}

	// 获取扩展新闻
	extendedNews, err := ens.fetchFromAdditionalSources(ctx, req)
	if err != nil {
		ens.logger.Info("获取扩展新闻失败: %v", err)
		extendedNews = []*models.NewsItem{}
	}

	// 合并所有新闻
	allNews := make([]models.NewsItem, 0, len(baseResult.TopHeadlines)+len(extendedNews))
	allNews = append(allNews, baseResult.TopHeadlines...)
	for _, item := range extendedNews {
		if item != nil {
			allNews = append(allNews, *item)
		}
	}

	// 应用聚合规则
	allNewsPtrs := make([]*models.NewsItem, len(allNews))
	for i := range allNews {
		allNewsPtrs[i] = &allNews[i]
	}
	processedNews := ens.applyAggregationRules(allNewsPtrs)

	// 去重和排序
	finalNews := ens.deduplicateAndSort(processedNews)

	// 分析处理后的新闻
	result := ens.analyzeNews(req.StockCode, finalNews, req.Days)

	// 添加新闻源统计
	result.NewsBySource = ens.getNewsSourceStats(finalNews)

	ens.logger.Info("扩展新闻分析完成: %s, 总数: %d", req.StockCode, result.TotalNews)
	return result, nil
}

// fetchFromAdditionalSources 从扩展源获取新闻
func (ens *ExtendedNewsService) fetchFromAdditionalSources(ctx context.Context, req *models.NewsAnalysisRequest) ([]*models.NewsItem, error) {
	var allNews []*models.NewsItem
	var wg sync.WaitGroup
	newsChan := make(chan []*models.NewsItem, len(ens.additionalSources))
	errorChan := make(chan error, len(ens.additionalSources))

	// 获取启用的新闻源
	enabledSources := ens.getEnabledSources(req.Sources)

	for sourceID, source := range enabledSources {
		wg.Add(1)
		go func(sid string, src *models.AdditionalNewsSource) {
			defer wg.Done()

			// 检查速率限制
			if !ens.checkRateLimit(sid) {
				errorChan <- fmt.Errorf("新闻源 %s 已达到速率限制", src.Name)
				return
			}

			news, err := ens.fetchFromExtendedSource(ctx, sid, src, req)
			if err != nil {
				ens.updateSourceStatus(sid, "error", err)
				ens.logger.Error("从 %s 获取新闻失败: %v", src.Name, err)
				errorChan <- err
				return
			}

			ens.updateSourceStatus(sid, "success", nil)
			ens.updateSourceMetrics(sid, len(news))
			newsChan <- news
		}(sourceID, source)
	}

	// 等待所有goroutine完成
	go func() {
		wg.Wait()
		close(newsChan)
		close(errorChan)
	}()

	// 收集结果
	var errors []error
	for news := range newsChan {
		allNews = append(allNews, news...)
	}

	for err := range errorChan {
		errors = append(errors, err)
	}

	if len(allNews) == 0 && len(errors) > 0 {
		return nil, fmt.Errorf("所有扩展新闻源获取失败: %v", errors)
	}

	return allNews, nil
}

// fetchFromExtendedSource 从指定扩展源获取新闻
func (ens *ExtendedNewsService) fetchFromExtendedSource(ctx context.Context, sourceID string, source *models.AdditionalNewsSource, req *models.NewsAnalysisRequest) ([]*models.NewsItem, error) {
	switch sourceID {
	case "sina":
		return ens.fetchSinaNews(ctx, source, req)
	case "tencent":
		return ens.fetchTencentNews(ctx, source, req)
	case "xueqiu":
		return ens.fetchXueqiuNews(ctx, source, req)
	case "hexun":
		return ens.fetchHexunNews(ctx, source, req)
	default:
		return nil, fmt.Errorf("不支持的扩展新闻源: %s", sourceID)
	}
}

// fetchSinaNews 获取新浪财经新闻
func (ens *ExtendedNewsService) fetchSinaNews(ctx context.Context, source *models.AdditionalNewsSource, req *models.NewsAnalysisRequest) ([]*models.NewsItem, error) {
	ens.logger.Info("从新浪财经获取新闻: %s", req.StockCode)

	// 新浪财经API
	baseURL := "https://finance.sina.com.cn/7x24/scroll_data.php"

	// 构建查询参数
	params := url.Values{}
	params.Add("page", "1")
	params.Add("num", "50")
	params.Add("_", strconv.FormatInt(time.Now().UnixNano()/1000000, 10))

	// 如果指定了股票代码，添加股票过滤
	if req.StockCode != "" {
		params.Add("symbol", req.StockCode)
	}

	// 构建完整URL
	fullURL := baseURL + "?" + params.Encode()

	// 创建请求
	httpReq, err := http.NewRequestWithContext(ctx, "GET", fullURL, nil)
	if err != nil {
		return nil, fmt.Errorf("创建请求失败: %v", err)
	}

	// 设置自定义请求头
	for key, value := range source.Headers {
		httpReq.Header.Set(key, value)
	}

	// 发送请求
	resp, err := ens.httpClient.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("请求失败: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("HTTP错误: %d", resp.StatusCode)
	}

	// 读取响应
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("读取响应失败: %v", err)
	}

	// 解析响应
	return ens.parseSinaResponse(body, req.StockCode)
}

// parseSinaResponse 解析新浪响应
func (ens *ExtendedNewsService) parseSinaResponse(responseBody []byte, stockCode string) ([]*models.NewsItem, error) {
	var data struct {
		Counts   int `json:"counts"`
		CurrTime int `json:"curr_time"`
		List     []struct {
			ID        string `json:"id"`
			Title     string `json:"title"`
			URL       string `json:"url"`
			Time      string `json:"time"`
			Abstract  string `json:"abstract"`
			MediaName string `json:"media_name"`
			Tags      string `json:"tags"`
		} `json:"list"`
	}

	if err := json.Unmarshal(responseBody, &data); err != nil {
		return nil, fmt.Errorf("解析JSON失败: %v", err)
	}

	var news []*models.NewsItem
	for _, item := range data.List {
		// 解析时间
		publishTime, err := time.Parse("2006-01-02 15:04:05", item.Time)
		if err != nil {
			publishTime = time.Now().Add(-time.Minute)
		}

		// 提取标签
		tags := strings.Split(item.Tags, ",")
		if len(tags) == 1 && tags[0] == "" {
			tags = []string{}
		}

		// 检查是否相关股票
		relevant := stockCode == "" || strings.Contains(item.Title, stockCode) || strings.Contains(item.Abstract, stockCode)

		if relevant {
			newsItem := &models.NewsItem{
				ID:          fmt.Sprintf("sina_%s", item.ID),
				Title:       item.Title,
				Summary:     item.Abstract,
				Content:     item.Abstract, // 新浪通常只有摘要
				Source:      "新浪财经",
				Author:      item.MediaName,
				URL:         item.URL,
				PublishTime: publishTime,
				Category:    "财经快讯",
				Tags:        tags,
				Relevance:   0.8,
				StockCodes:  []string{stockCode},
				Sentiment: &models.SentimentResult{
					Label:      "neutral",
					Score:      0.0,
					Confidence: 0.6,
					Emotions:   make(map[string]float64),
				},
				CreatedAt: time.Now(),
				UpdatedAt: time.Now(),
			}
			news = append(news, newsItem)
		}
	}

	return news, nil
}

// fetchTencentNews 获取腾讯财经新闻
func (ens *ExtendedNewsService) fetchTencentNews(ctx context.Context, source *models.AdditionalNewsSource, req *models.NewsAnalysisRequest) ([]*models.NewsItem, error) {
	ens.logger.Info("从腾讯财经获取新闻: %s", req.StockCode)

	// 腾讯财经API (这里使用模拟方式，实际应该调用真实API)
	baseURL := "https://finance.qq.com/api/a/search"

	// 构建查询参数
	params := url.Values{}
	params.Add("page", "1")
	params.Add("pagesize", "50")
	params.Add("q", req.StockCode)

	// 构建完整URL
	fullURL := baseURL + "?" + params.Encode()

	// 创建请求
	httpReq, err := http.NewRequestWithContext(ctx, "GET", fullURL, nil)
	if err != nil {
		return nil, fmt.Errorf("创建请求失败: %v", err)
	}

	// 设置自定义请求头
	for key, value := range source.Headers {
		httpReq.Header.Set(key, value)
	}

	// 发送请求
	resp, err := ens.httpClient.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("请求失败: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("HTTP错误: %d", resp.StatusCode)
	}

	// 读取响应
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("读取响应失败: %v", err)
	}

	// 解析响应
	return ens.parseTencentResponse(body, req.StockCode)
}

// parseTencentResponse 解析腾讯响应
func (ens *ExtendedNewsService) parseTencentResponse(responseBody []byte, stockCode string) ([]*models.NewsItem, error) {
	var response models.TencentNewsResponse
	if err := json.Unmarshal(responseBody, &response); err != nil {
		return nil, fmt.Errorf("解析JSON失败: %v", err)
	}

	var news []*models.NewsItem
	for _, item := range response.Data.List {
		newsItem := &models.NewsItem{
			ID:          fmt.Sprintf("tencent_%s", item.ID),
			Title:       item.Title,
			Summary:     item.Summary,
			Content:     item.Content,
			Source:      "腾讯财经",
			Author:      item.Author,
			URL:         item.URL,
			PublishTime: item.PublishTime,
			Category:    item.Category,
			Tags:        append(item.Tags, item.Column),
			Relevance:   0.8,
			StockCodes:  append(item.StockCodes, stockCode),
			Sentiment:   item.Sentiment,
			CreatedAt:   time.Now(),
			UpdatedAt:   time.Now(),
		}
		news = append(news, newsItem)
	}

	return news, nil
}

// fetchXueqiuNews 获取雪球新闻
func (ens *ExtendedNewsService) fetchXueqiuNews(ctx context.Context, source *models.AdditionalNewsSource, req *models.NewsAnalysisRequest) ([]*models.NewsItem, error) {
	ens.logger.Info("从雪球获取新闻: %s", req.StockCode)

	// 雪球API (这里使用模拟方式，实际应该调用真实API)
	baseURL := "https://xueqiu.com/statuses/hot_timeline_v2.json"

	// 构建查询参数
	params := url.Values{}
	params.Add("page", "1")
	params.Add("count", "50")
	if req.StockCode != "" {
		params.Add("symbol_id", req.StockCode)
	}

	// 构建完整URL
	fullURL := baseURL + "?" + params.Encode()

	// 创建请求
	httpReq, err := http.NewRequestWithContext(ctx, "GET", fullURL, nil)
	if err != nil {
		return nil, fmt.Errorf("创建请求失败: %v", err)
	}

	// 设置自定义请求头
	for key, value := range source.Headers {
		httpReq.Header.Set(key, value)
	}

	// 发送请求
	resp, err := ens.httpClient.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("请求失败: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("HTTP错误: %d", resp.StatusCode)
	}

	// 读取响应
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("读取响应失败: %v", err)
	}

	// 解析响应
	return ens.parseXueqiuResponse(body, req.StockCode)
}

// parseXueqiuResponse 解析雪球响应
func (ens *ExtendedNewsService) parseXueqiuResponse(responseBody []byte, stockCode string) ([]*models.NewsItem, error) {
	var response models.XueqiuNewsResponse
	if err := json.Unmarshal(responseBody, &response); err != nil {
		return nil, fmt.Errorf("解析JSON失败: %v", err)
	}

	var news []*models.NewsItem
	for _, item := range response.Data.List {
		// 转换雪球特有格式为通用新闻格式
		newsItem := &models.NewsItem{
			ID:          fmt.Sprintf("xueqiu_%s", item.ID),
			Title:       item.Text[:min(50, len(item.Text))], // 截取前50字符作为标题
			Summary:     item.Text,
			Content:     item.Text,
			Source:      "雪球",
			Author:      item.User.ScreenName,
			URL:         item.URL,
			PublishTime: item.CreatedAt,
			Category:    "社区动态",
			Tags:        append(item.Tags, item.Symbols...),
			Relevance:   0.7,
			StockCodes:  append(item.Symbols, stockCode),
			Sentiment:   item.Sentiment,
			CreatedAt:   time.Now(),
			UpdatedAt:   time.Now(),
		}
		news = append(news, newsItem)
	}

	return news, nil
}

// fetchHexunNews 获取和讯网新闻
func (ens *ExtendedNewsService) fetchHexunNews(ctx context.Context, source *models.AdditionalNewsSource, req *models.NewsAnalysisRequest) ([]*models.NewsItem, error) {
	ens.logger.Info("从和讯网获取新闻: %s", req.StockCode)

	// 和讯网API (这里使用模拟方式，实际应该调用真实API)
	baseURL := "https://news.hexun.com/api/news/list"

	// 构建查询参数
	params := url.Values{}
	params.Add("page", "1")
	params.Add("size", "50")
	params.Add("keyword", req.StockCode)

	// 构建完整URL
	fullURL := baseURL + "?" + params.Encode()

	// 创建请求
	httpReq, err := http.NewRequestWithContext(ctx, "GET", fullURL, nil)
	if err != nil {
		return nil, fmt.Errorf("创建请求失败: %v", err)
	}

	// 设置自定义请求头
	for key, value := range source.Headers {
		httpReq.Header.Set(key, value)
	}

	// 发送请求
	resp, err := ens.httpClient.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("请求失败: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("HTTP错误: %d", resp.StatusCode)
	}

	// 读取响应
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("读取响应失败: %v", err)
	}

	// 解析响应
	return ens.parseHexunResponse(body, req.StockCode)
}

// parseHexunResponse 解析和讯网响应
func (ens *ExtendedNewsService) parseHexunResponse(responseBody []byte, stockCode string) ([]*models.NewsItem, error) {
	var response models.HexunNewsResponse
	if err := json.Unmarshal(responseBody, &response); err != nil {
		return nil, fmt.Errorf("解析JSON失败: %v", err)
	}

	var news []*models.NewsItem
	for _, item := range response.Data.List {
		newsItem := &models.NewsItem{
			ID:          fmt.Sprintf("hexun_%s", item.ID),
			Title:       item.Title,
			Summary:     item.Summary,
			Content:     item.Content,
			Source:      "和讯网",
			Author:      item.Author,
			URL:         item.URL,
			PublishTime: item.PublishTime,
			Category:    item.Category,
			Tags:        append(item.Tags, item.Column),
			Relevance:   0.8,
			StockCodes:  append(item.StockCodes, stockCode),
			Sentiment:   item.Sentiment,
			CreatedAt:   time.Now(),
			UpdatedAt:   time.Now(),
		}
		news = append(news, newsItem)
	}

	return news, nil
}

// 辅助函数
func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

// getEnabledSources 获取启用的新闻源
func (ens *ExtendedNewsService) getEnabledSources(requestedSources []string) map[string]*models.AdditionalNewsSource {
	enabled := make(map[string]*models.AdditionalNewsSource)

	for sourceID, source := range ens.additionalSources {
		if !source.Enabled {
			continue
		}

		// 如果指定了源，则只获取指定源
		if len(requestedSources) > 0 {
			found := false
			for _, s := range requestedSources {
				if s == sourceID {
					found = true
					break
				}
			}
			if !found {
				continue
			}
		}

		enabled[sourceID] = source
	}

	return enabled
}

// checkRateLimit 检查速率限制
func (ens *ExtendedNewsService) checkRateLimit(sourceID string) bool {
	status, exists := ens.sourceStatus[sourceID]
	if !exists {
		return false
	}

	// 简单的速率限制检查
	if status.Status == "rate_limited" && time.Since(status.UpdatedAt) < time.Minute {
		return false
	}

	return true
}

// updateSourceStatus 更新新闻源状态
func (ens *ExtendedNewsService) updateSourceStatus(sourceID, status string, err error) {
	ens.mutex.Lock()
	defer ens.mutex.Unlock()

	if sourceStatus, exists := ens.sourceStatus[sourceID]; exists {
		sourceStatus.Status = status
		sourceStatus.LastCheck = time.Now()
		sourceStatus.UpdatedAt = time.Now()

		if status == "error" && err != nil {
			sourceStatus.ErrorCount++
			sourceStatus.ErrorMessage = err.Error()
		} else if status == "success" {
			sourceStatus.ErrorMessage = ""
		}

		// 计算成功率
		metrics := ens.sourceMetrics[sourceID]
		if metrics != nil && metrics.RequestCount > 0 {
			sourceStatus.SuccessRate = float64(metrics.SuccessCount) / float64(metrics.RequestCount)
		}
	}
}

// updateSourceMetrics 更新新闻源指标
func (ens *ExtendedNewsService) updateSourceMetrics(sourceID string, newsCount int) {
	ens.mutex.Lock()
	defer ens.mutex.Unlock()

	if metrics, exists := ens.sourceMetrics[sourceID]; exists {
		metrics.RequestCount++
		metrics.SuccessCount++
		metrics.ArticlesFetched += newsCount

		// 每日重置指标
		if time.Since(metrics.LastReset) > 24*time.Hour {
			metrics.RequestCount = 0
			metrics.SuccessCount = 0
			metrics.ErrorCount = 0
			metrics.ArticlesFetched = 0
			metrics.LastReset = time.Now()
		}
	}
}

// applyAggregationRules 应用聚合规则
func (ens *ExtendedNewsService) applyAggregationRules(news []*models.NewsItem) []*models.NewsItem {
	// 使用新闻聚合器进行高级聚合处理
	return ens.aggregator.ProcessNews(news)
}

// deduplicateAndSort 去重和排序
func (ens *ExtendedNewsService) deduplicateAndSort(news []*models.NewsItem) []*models.NewsItem {
	// 按时间和相关性排序
	sort.Slice(news, func(i, j int) bool {
		if news[i].Relevance != news[j].Relevance {
			return news[i].Relevance > news[j].Relevance
		}
		return news[i].PublishTime.After(news[j].PublishTime)
	})

	return news
}

// getNewsSourceStats 获取新闻源统计
func (ens *ExtendedNewsService) getNewsSourceStats(news []*models.NewsItem) map[string]int {
	stats := make(map[string]int)
	for _, item := range news {
		stats[item.Source]++
	}
	return stats
}

// GetExtendedNewsSources 获取扩展新闻源列表
func (ens *ExtendedNewsService) GetExtendedNewsSources() map[string]*models.AdditionalNewsSource {
	ens.mutex.RLock()
	defer ens.mutex.RUnlock()

	result := make(map[string]*models.AdditionalNewsSource)
	for k, v := range ens.additionalSources {
		result[k] = v
	}
	return result
}

// GetNewsSourceStatus 获取新闻源状态
func (ens *ExtendedNewsService) GetNewsSourceStatus() map[string]*models.NewsSourceStatus {
	ens.mutex.RLock()
	defer ens.mutex.RUnlock()

	result := make(map[string]*models.NewsSourceStatus)
	for k, v := range ens.sourceStatus {
		result[k] = v
	}
	return result
}

// GetNewsSourceMetrics 获取新闻源指标
func (ens *ExtendedNewsService) GetNewsSourceMetrics() map[string]*models.NewsSourceMetrics {
	ens.mutex.RLock()
	defer ens.mutex.RUnlock()

	result := make(map[string]*models.NewsSourceMetrics)
	for k, v := range ens.sourceMetrics {
		result[k] = v
	}
	return result
}

// GetNewsClusters 获取新闻聚类信息
func (ens *ExtendedNewsService) GetNewsClusters() map[string]*models.NewsCluster {
	return ens.aggregator.GetClusters()
}

// GetNewsDuplicates 获取重复新闻信息
func (ens *ExtendedNewsService) GetNewsDuplicates() map[string][]string {
	return ens.aggregator.GetDuplicates()
}