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

// NewsService 新闻服务
type NewsService struct {
	dataService *DataService
	sources     map[string]*models.NewsSource
	httpClient  *http.Client
	mutex       sync.RWMutex
	logger      *Logger
}

// NewNewsService 创建新闻服务
func NewNewsService(dataService *DataService) *NewsService {
	ns := &NewsService{
		dataService: dataService,
		sources:     make(map[string]*models.NewsSource),
		httpClient: &http.Client{
			Timeout: 30 * time.Second,
		},
		logger: AppLogger,
	}

	// 初始化新闻源
	ns.initDefaultSources()

	return ns
}

// initDefaultSources 初始化默认新闻源
func (ns *NewsService) initDefaultSources() {
	sources := []*models.NewsSource{
		{
			ID:          "eastmoney",
			Name:        "东方财富网",
			BaseURL:     "https://newsapi.eastmoney.com",
			APIKey:      "",
			Enabled:     true,
			RateLimit:   60,
			Description: "东方财富新闻API",
		},
		{
			ID:          "tonghuashun",
			Name:        "同花顺",
			BaseURL:     "https://news.10jqka.com.cn",
			APIKey:      "",
			Enabled:     true,
			RateLimit:   60,
			Description: "同花顺财经新闻",
		},
	}

	for _, source := range sources {
		ns.sources[source.ID] = source
	}
}

// GetNewsSources 获取所有新闻源
func (ns *NewsService) GetNewsSources() map[string]*models.NewsSource {
	ns.mutex.RLock()
	defer ns.mutex.RUnlock()

	result := make(map[string]*models.NewsSource)
	for k, v := range ns.sources {
		result[k] = v
	}
	return result
}

// AddNewsSource 添加新闻源
func (ns *NewsService) AddNewsSource(source *models.NewsSource) {
	ns.mutex.Lock()
	defer ns.mutex.Unlock()
	ns.sources[source.ID] = source
}

// FetchNews 获取新闻
func (ns *NewsService) FetchNews(ctx context.Context, req *models.NewsAnalysisRequest) (*models.NewsAnalysisResult, error) {
	ns.logger.Info("开始获取新闻: %s, 天数: %d", req.StockCode, req.Days)

	var allNews []*models.NewsItem
	var wg sync.WaitGroup
	newsChan := make(chan []*models.NewsItem, len(ns.sources))
	errorChan := make(chan error, len(ns.sources))

	// 并发获取各源新闻
	for sourceID, source := range ns.sources {
		if !source.Enabled {
			continue
		}

		// 如果指定了源，则只获取指定源
		if len(req.Sources) > 0 {
			found := false
			for _, s := range req.Sources {
				if s == sourceID {
					found = true
					break
				}
			}
			if !found {
				continue
			}
		}

		wg.Add(1)
		go func(sid string, src *models.NewsSource) {
			defer wg.Done()

			news, err := ns.fetchFromSource(ctx, sid, src, req)
			if err != nil {
				ns.logger.Error("从 %s 获取新闻失败: %v", src.Name, err)
				errorChan <- err
				return
			}
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
		return nil, fmt.Errorf("获取新闻失败: %v", errors)
	}

	// 分析新闻
	result := ns.analyzeNews(req.StockCode, allNews, req.Days)

	ns.logger.Info("新闻分析完成: %s, 总数: %d", req.StockCode, result.TotalNews)
	return result, nil
}

// fetchFromSource 从指定源获取新闻
func (ns *NewsService) fetchFromSource(ctx context.Context, sourceID string, source *models.NewsSource, req *models.NewsAnalysisRequest) ([]*models.NewsItem, error) {
	switch sourceID {
	case "eastmoney":
		return ns.fetchEastMoneyNews(ctx, source, req)
	case "tonghuashun":
		return ns.fetchTongHuaShunNews(ctx, source, req)
	default:
		return nil, fmt.Errorf("不支持的新闻源: %s", sourceID)
	}
}

// fetchEastMoneyNews 获取东方财富新闻
func (ns *NewsService) fetchEastMoneyNews(ctx context.Context, source *models.NewsSource, req *models.NewsAnalysisRequest) ([]*models.NewsItem, error) {
	ns.logger.Info("从东方财富获取新闻: %s", req.StockCode)

	// 东方财富新闻API
	baseURL := "https://push2.eastmoney.com/api/qt/clist/get"

	// 构建查询参数
	params := url.Values{}
	params.Add("cb", fmt.Sprintf("jQuery%d%d", time.Now().UnixNano(), randInt(1000, 9999)))
	params.Add("pn", "1")
	params.Add("pz", "50") // 每页50条
	params.Add("po", "1")
	params.Add("np", "1")
	params.Add("ut", "bd1d9ddb04089700cf9c27f6f7426281")
	params.Add("fltt", "2")
	params.Add("invt", "2")
	params.Add("fid", "f3")
	params.Add("fs", "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23") // 新闻类型过滤
	params.Add("fields", "f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f116,f81,f84,f85,f86,f204,f205,f124,f1,f147")
	params.Add("_", strconv.FormatInt(time.Now().UnixNano()/1000000, 10))

	// 如果指定了股票代码，添加股票过滤
	if req.StockCode != "" {
		params.Add("filters", fmt.Sprintf("f12^%s", req.StockCode))
	}

	// 构建完整URL
	fullURL := baseURL + "?" + params.Encode()

	// 创建请求
	httpReq, err := http.NewRequestWithContext(ctx, "GET", fullURL, nil)
	if err != nil {
		return nil, fmt.Errorf("创建请求失败: %v", err)
	}

	// 设置请求头
	httpReq.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
	httpReq.Header.Set("Referer", "https://finance.eastmoney.com/")
	httpReq.Header.Set("Accept", "*/*")

	// 发送请求
	resp, err := ns.httpClient.Do(httpReq)
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

	// 解析JSONP响应
	return ns.parseEastMoneyResponse(string(body), req.StockCode)
}

// parseEastMoneyResponse 解析东方财富响应
func (ns *NewsService) parseEastMoneyResponse(responseBody string, stockCode string) ([]*models.NewsItem, error) {
	// 移除JSONP回调
	start := strings.Index(responseBody, "(")
	end := strings.LastIndex(responseBody, ")")
	if start == -1 || end == -1 {
		return nil, fmt.Errorf("无效的JSONP响应格式")
	}

	jsonStr := responseBody[start+1 : end]

	var data struct {
		Data struct {
			Diff []struct {
				F12 string `json:"f12"` // 代码
				F14 string `json:"f14"` // 名称
				F2  string `json:"f2"`  // 最新价
				F3  int    `json:"f3"`  // 涨跌幅
			} `json:"diff"`
		} `json:"data"`
	}

	if err := json.Unmarshal([]byte(jsonStr), &data); err != nil {
		return nil, fmt.Errorf("解析JSON失败: %v", err)
	}

	// 这里简化处理，实际应该调用新闻详情API获取新闻内容
	var news []*models.NewsItem

	// 模拟新闻数据
	for i, item := range data.Data.Diff {
		if stockCode == "" || item.F12 == stockCode {
			newsItem := &models.NewsItem{
				ID:          fmt.Sprintf("em_%d_%s", i, item.F12),
				Title:       fmt.Sprintf("%s相关新闻 - %s", item.F14, time.Now().Format("15:04")),
				Summary:     fmt.Sprintf("%s(%s)的最新动态，价格：%s，涨跌幅：%d%%", item.F14, item.F12, item.F2, item.F3),
				Content:     fmt.Sprintf("%s(%s)的详细新闻内容", item.F14, item.F12),
				Source:      "东方财富网",
				Author:      "财经记者",
				URL:         fmt.Sprintf("https://quote.eastmoney.com/%s.html", item.F12),
				PublishTime: time.Now().Add(-time.Duration(i) * time.Hour),
				Category:    "个股新闻",
				Tags:        []string{item.F12, item.F14, "股价"},
				Relevance:   0.8,
				StockCodes:  []string{item.F12},
				Sentiment: &models.SentimentResult{
					Label:      func() string { if item.F3 > 0 { return "positive" } else if item.F3 < 0 { return "negative" } else { return "neutral" } }(),
					Score:      float64(item.F3) / 100.0,
					Confidence: 0.7,
					Emotions: map[string]float64{
						"optimism": float64(item.F3) / 200.0,
						"fear":     float64(-item.F3) / 200.0,
					},
				},
				CreatedAt: time.Now(),
				UpdatedAt: time.Now(),
			}
			news = append(news, newsItem)
		}
	}

	return news, nil
}

// fetchTongHuaShunNews 获取同花顺新闻
func (ns *NewsService) fetchTongHuaShunNews(ctx context.Context, source *models.NewsSource, req *models.NewsAnalysisRequest) ([]*models.NewsItem, error) {
	ns.logger.Info("从同花顺获取新闻: %s", req.StockCode)

	// 同花顺新闻API (这里使用模拟方式，实际应该调用真实API)
	baseURL := "https://news.10jqka.com.cn/realtimenews.json"

	// 构建查询参数
	params := url.Values{}
	params.Add("page", "1")
	params.Add("pagesize", "50")
	if req.StockCode != "" {
		params.Add("code", req.StockCode)
	}

	// 构建完整URL
	fullURL := baseURL + "?" + params.Encode()

	// 创建请求
	httpReq, err := http.NewRequestWithContext(ctx, "GET", fullURL, nil)
	if err != nil {
		return nil, fmt.Errorf("创建请求失败: %v", err)
	}

	// 设置请求头
	httpReq.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
	httpReq.Header.Set("Referer", "https://www.10jqka.com.cn/")
	httpReq.Header.Set("Accept", "application/json, text/plain, */*")

	// 发送请求
	resp, err := ns.httpClient.Do(httpReq)
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
	return ns.parseTongHuaShunResponse(body, req.StockCode)
}

// parseTongHuaShunResponse 解析同花顺响应
func (ns *NewsService) parseTongHuaShunResponse(responseBody []byte, stockCode string) ([]*models.NewsItem, error) {
	var items []models.TongHuaShunNewsItem
	if err := json.Unmarshal(responseBody, &items); err != nil {
		return nil, fmt.Errorf("解析JSON失败: %v", err)
	}

	var news []*models.NewsItem
	for i, item := range items {
		// 解析时间
		publishTime, err := time.Parse("2006-01-02 15:04:05", item.ShowTime)
		if err != nil {
			publishTime = time.Now()
		}

		// 检查是否相关股票
		relevant := len(item.StockCodes) == 0 || stockCode == ""
		for _, code := range item.StockCodes {
			if code == stockCode {
				relevant = true
				break
			}
		}

		if relevant {
			newsItem := &models.NewsItem{
				ID:          fmt.Sprintf("ths_%d", i),
				Title:       item.Title,
				Summary:     item.Digest,
				Content:     item.Content,
				Source:      "同花顺",
				Author:      item.Author,
				URL:         fmt.Sprintf("https://news.10jqka.com.cn/%s.html", item.Id),
				PublishTime: publishTime,
				Category:    item.CateName,
				Tags:        append(item.Tags, item.StockCodes...),
				Relevance:   0.8,
				StockCodes:  item.StockCodes,
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

// analyzeNews 分析新闻
func (ns *NewsService) analyzeNews(stockCode string, news []*models.NewsItem, days int) *models.NewsAnalysisResult {
	result := &models.NewsAnalysisResult{
		StockCode:        stockCode,
		AnalysisTime:     time.Now(),
		Days:             days,
		TotalNews:        len(news),
		PositiveNews:     0,
		NegativeNews:     0,
		NeutralNews:      0,
		OverallSentiment: "neutral",
		SentimentScore:   0.0,
		SentimentTrend:   "stable",
		KeyTopics:        make([]string, 0),
		RiskEvents:       make([]string, 0),
		TopHeadlines:     make([]models.NewsItem, 0),
		NewsBySource:     make(map[string]int),
		NewsByDay:        make([]models.DailyNewsCount, 0),
		Confidence:       0.7,
	}

	// 统计分析
	sentimentScores := make([]float64, 0)
	sourceCount := make(map[string]int)
	dayCount := make(map[string]*models.DailyNewsCount)
	keywords := make(map[string]int)

	for _, item := range news {
		// 情感统计
		if item.Sentiment != nil {
			sentimentScores = append(sentimentScores, item.Sentiment.Score)
			switch item.Sentiment.Label {
			case "positive":
				result.PositiveNews++
			case "negative":
				result.NegativeNews++
			default:
				result.NeutralNews++
			}
		} else {
			result.NeutralNews++
		}

		// 来源统计
		result.NewsBySource[item.Source]++

		// 按日统计
		dateKey := item.PublishTime.Format("2006-01-02")
		if _, exists := dayCount[dateKey]; !exists {
			dayCount[dateKey] = &models.DailyNewsCount{
				Date:       item.PublishTime,
				TotalCount: 0,
				Positive:   0,
				Negative:   0,
				Neutral:    0,
			}
		}

		dayCount[dateKey].TotalCount++
		if item.Sentiment != nil {
			switch item.Sentiment.Label {
			case "positive":
				dayCount[dateKey].Positive++
			case "negative":
				dayCount[dateKey].Negative++
			default:
				dayCount[dateKey].Neutral++
			}
		}

		// 关键词统计
		for _, tag := range item.Tags {
			keywords[tag]++
		}
	}

	// 计算整体情感
	if len(sentimentScores) > 0 {
		totalScore := 0.0
		for _, score := range sentimentScores {
			totalScore += score
		}
		result.SentimentScore = totalScore / float64(len(sentimentScores))

		if result.SentimentScore > 0.1 {
			result.OverallSentiment = "positive"
		} else if result.SentimentScore < -0.1 {
			result.OverallSentiment = "negative"
		}
	}

	// 获取头条新闻
	result.TopHeadlines = ns.getTopHeadlines(news, 5)

	// 获取关键主题
	result.KeyTopics = ns.getTopKeywords(keywords, 10)

	// 构建每日新闻统计
	for _, day := range dayCount {
		result.NewsByDay = append(result.NewsByDay, *day)
	}
	sort.Slice(result.NewsByDay, func(i, j int) bool {
		return result.NewsByDay[i].Date.Before(result.NewsByDay[j].Date)
	})

	// 计算情感趋势
	result.SentimentTrend = ns.calculateSentimentTrend(result.NewsByDay)

	// 计算信心度
	result.Confidence = ns.calculateConfidence(result)

	return result
}

// getTopHeadlines 获取头条新闻
func (ns *NewsService) getTopHeadlines(news []*models.NewsItem, count int) []models.NewsItem {
	// 按相关性和发布时间排序
	sort.Slice(news, func(i, j int) bool {
		if news[i].Relevance != news[j].Relevance {
			return news[i].Relevance > news[j].Relevance
		}
		return news[i].PublishTime.After(news[j].PublishTime)
	})

	if count > len(news) {
		count = len(news)
	}

	result := make([]models.NewsItem, count)
	for i := 0; i < count; i++ {
		result[i] = *news[i]
	}

	return result
}

// getTopKeywords 获取热门关键词
func (ns *NewsService) getTopKeywords(keywords map[string]int, count int) []string {
	type kv struct {
		Key   string
		Value int
	}

	var kvList []kv
	for k, v := range keywords {
		kvList = append(kvList, kv{k, v})
	}

	sort.Slice(kvList, func(i, j int) bool {
		return kvList[i].Value > kvList[j].Value
	})

	if count > len(kvList) {
		count = len(kvList)
	}

	result := make([]string, count)
	for i := 0; i < count; i++ {
		result[i] = kvList[i].Key
	}

	return result
}

// calculateSentimentTrend 计算情感趋势
func (ns *NewsService) calculateSentimentTrend(dailyNews []models.DailyNewsCount) string {
	if len(dailyNews) < 2 {
		return "stable"
	}

	// 计算最近几天的情感变化
	recent := dailyNews[len(dailyNews)-1]
	previous := dailyNews[len(dailyNews)-2]

	recentScore := float64(recent.Positive-recent.Negative) / float64(recent.TotalCount)
	previousScore := float64(previous.Positive-previous.Negative) / float64(previous.TotalCount)

	change := recentScore - previousScore

	if change > 0.1 {
		return "improving"
	} else if change < -0.1 {
		return "declining"
	}
	return "stable"
}

// calculateConfidence 计算信心度
func (ns *NewsService) calculateConfidence(result *models.NewsAnalysisResult) float64 {
	confidence := 0.7

	// 基于新闻数量调整
	if result.TotalNews >= 10 {
		confidence += 0.1
	} else if result.TotalNews < 3 {
		confidence -= 0.2
	}

	// 基于来源多样性调整
	sourceCount := len(result.NewsBySource)
	if sourceCount >= 3 {
		confidence += 0.1
	} else if sourceCount == 1 {
		confidence -= 0.1
	}

	// 确保在合理范围内
	if confidence > 0.95 {
		confidence = 0.95
	}
	if confidence < 0.3 {
		confidence = 0.3
	}

	return confidence
}

// randInt 生成随机整数
func randInt(min, max int) int {
	return min + int(time.Now().UnixNano()%int64(max-min+1))
}