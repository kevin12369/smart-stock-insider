package services

import (
	"crypto/md5"
	"fmt"
	"math"
	"sort"
	"strconv"
	"strings"
	"sync"
	"time"

	"smart-stock-insider/internal/models"
)

// NewsAggregator 新闻聚合器
type NewsAggregator struct {
	rules      map[string]*models.NewsAggregationRule
	clusters   map[string]*models.NewsCluster
	duplicates map[string][]string // MD5哈希 -> 原始新闻ID列表
	mutex      sync.RWMutex
	logger     *Logger
}

// NewNewsAggregator 创建新闻聚合器
func NewNewsAggregator() *NewsAggregator {
	return &NewsAggregator{
		rules:      make(map[string]*models.NewsAggregationRule),
		clusters:   make(map[string]*models.NewsCluster),
		duplicates: make(map[string][]string),
		logger:     AppLogger,
	}
}

// LoadAggregationRules 加载聚合规则
func (na *NewsAggregator) LoadAggregationRules(rules map[string]*models.NewsAggregationRule) {
	na.mutex.Lock()
	defer na.mutex.Unlock()

	na.rules = rules
	na.logger.Info("加载了 %d 条新闻聚合规则", len(rules))
}

// ProcessNews 处理新闻聚合
func (na *NewsAggregator) ProcessNews(news []*models.NewsItem) []*models.NewsItem {
	na.logger.Info("开始处理新闻聚合，原始新闻数量: %d", len(news))

	// 1. 去重处理
	deduplicatedNews := na.deduplicateNews(news)

	// 2. 相似内容聚类
	clusteredNews := na.clusterSimilarNews(deduplicatedNews)

	// 3. 热门话题识别
	trendingNews := na.identifyTrendingTopics(clusteredNews)

	// 4. 应用聚合规则
	finalNews := na.applyAggregationRules(trendingNews)

	na.logger.Info("新闻聚合处理完成，最终新闻数量: %d", len(finalNews))
	return finalNews
}

// deduplicateNews 去重新闻
func (na *NewsAggregator) deduplicateNews(news []*models.NewsItem) []*models.NewsItem {
	na.mutex.Lock()
	defer na.mutex.Unlock()

	seen := make(map[string]bool)
	var result []*models.NewsItem

	for _, item := range news {
		// 生成内容哈希
		hash := na.generateContentHash(item)

		// 检查是否已存在相似内容
		if !na.isDuplicate(hash, item) {
			seen[hash] = true
			result = append(result, item)
			na.duplicates[hash] = append(na.duplicates[hash], item.ID)
		}
	}

	na.logger.Info("去重完成，去除重复新闻 %d 条", len(news)-len(result))
	return result
}

// generateContentHash 生成内容哈希
func (na *NewsAggregator) generateContentHash(item *models.NewsItem) string {
	content := strings.ToLower(strings.TrimSpace(item.Title + item.Summary))

	// 简单的内容标准化
	content = strings.ReplaceAll(content, " ", "")
	content = strings.ReplaceAll(content, "\n", "")
	content = strings.ReplaceAll(content, "\t", "")

	hash := md5.Sum([]byte(content))
	return fmt.Sprintf("%x", hash)
}

// isDuplicate 检查是否为重复内容
func (na *NewsAggregator) isDuplicate(hash string, item *models.NewsItem) bool {
	// 检查是否已存在相同哈希
	if _, exists := na.duplicates[hash]; exists {
		return true
	}

	// 检查去重规则
	for _, rule := range na.rules {
		if rule.RuleType == "duplicate" && rule.Enabled {
			if na.matchesDuplicateRule(rule, item) {
				return true
			}
		}
	}

	return false
}

// matchesDuplicateRule 检查是否匹配去重规则
func (na *NewsAggregator) matchesDuplicateRule(rule *models.NewsAggregationRule, item *models.NewsItem) bool {
	threshold := 0.9 // 默认相似度阈值

	// 从规则条件中获取阈值
	if val, exists := rule.Conditions["similarity_threshold"]; exists {
		if parsed, err := strconv.ParseFloat(val, 64); err == nil {
			threshold = parsed
		}
	}

	// 检查与已有新闻的相似度
	for hash, ids := range na.duplicates {
		if len(ids) > 0 {
			// 这里简化处理，实际应该实现内容相似度计算
			if hash == na.generateContentHash(item) {
				return threshold >= 0.9 // 完全相同
			}
		}
	}

	return false
}

// clusterSimilarNews 聚类相似新闻
func (na *NewsAggregator) clusterSimilarNews(news []*models.NewsItem) []*models.NewsItem {
	na.mutex.Lock()
	defer na.mutex.Unlock()

	// 清空之前的聚类
	na.clusters = make(map[string]*models.NewsCluster)

	// 按时间窗口分组
	timeWindows := na.groupByTimeWindow(news, 2*time.Hour) // 2小时窗口

	// 在每个时间窗口内进行聚类
	var clusteredNews []*models.NewsItem
	for windowKey, windowNews := range timeWindows {
		clusters := na.clusterBySimilarity(windowNews, 0.7)

		for _, cluster := range clusters {
			clusterID := fmt.Sprintf("cluster_%s_%d", windowKey, len(na.clusters))

			// 创建聚类对象
			clusterObj := &models.NewsCluster{
				ID:         clusterID,
				Title:      na.generateClusterTitle(cluster),
				Summary:    na.generateClusterSummary(cluster),
				Category:   na.getClusterCategory(cluster),
				NewsIDs:    na.extractNewsIDs(cluster),
				StockCodes: na.extractStockCodes(cluster),
				Centroid:   cluster[0].ID, // 第一个作为中心
				Similarity:  na.calculateClusterSimilarity(cluster),
				ImpactScore: na.calculateClusterImpact(cluster),
				CreatedAt:  time.Now(),
				UpdatedAt:  time.Now(),
			}

			na.clusters[clusterID] = clusterObj

			// 保留聚类中最有代表性的新闻
			representativeNews := na.selectRepresentativeNews(cluster)
			clusteredNews = append(clusteredNews, representativeNews...)
		}
	}

	na.logger.Info("新闻聚类完成，生成 %d 个聚类", len(na.clusters))
	return clusteredNews
}

// groupByTimeWindow 按时间窗口分组
func (na *NewsAggregator) groupByTimeWindow(news []*models.NewsItem, window time.Duration) map[string][]*models.NewsItem {
	groups := make(map[string][]*models.NewsItem)

	for _, item := range news {
		// 按小时分组
		windowKey := item.PublishTime.Truncate(window).Format("2006-01-02_15")
		groups[windowKey] = append(groups[windowKey], item)
	}

	return groups
}

// clusterBySimilarity 按相似度聚类
func (na *NewsAggregator) clusterBySimilarity(news []*models.NewsItem, threshold float64) [][]*models.NewsItem {
	var clusters [][]*models.NewsItem
	used := make(map[int]bool)

	for i, item := range news {
		if used[i] {
			continue
		}

		cluster := []*models.NewsItem{item}
		used[i] = true

		// 查找相似新闻
		for j := i + 1; j < len(news); j++ {
			if used[j] {
				continue
			}

			if na.calculateSimilarity(item, news[j]) >= threshold {
				cluster = append(cluster, news[j])
				used[j] = true
			}
		}

		clusters = append(clusters, cluster)
	}

	return clusters
}

// calculateSimilarity 计算新闻相似度
func (na *NewsAggregator) calculateSimilarity(item1, item2 *models.NewsItem) float64 {
	title1 := strings.ToLower(item1.Title)
	title2 := strings.ToLower(item2.Title)

	// 简单的标题相似度计算
	intersection := 0
	words1 := strings.Fields(title1)
	words2 := strings.Fields(title2)

	wordSet1 := make(map[string]bool)
	wordSet2 := make(map[string]bool)

	for _, word := range words1 {
		wordSet1[word] = true
	}

	for _, word := range words2 {
		wordSet2[word] = true
	}

	// 计算交集
	for word := range wordSet1 {
		if wordSet2[word] {
			intersection++
		}
	}

	// 计算并集大小
	union := len(wordSet1) + len(wordSet2) - intersection

	if union == 0 {
		return 0
	}

	// Jaccard相似度
	return float64(intersection) / float64(union)
}

// generateClusterTitle 生成聚类标题
func (na *NewsAggregator) generateClusterTitle(cluster []*models.NewsItem) string {
	if len(cluster) == 0 {
		return ""
	}

	if len(cluster) == 1 {
		return cluster[0].Title
	}

	// 选择最长标题作为聚类标题
	var longestTitle string
	for _, item := range cluster {
		if len(item.Title) > len(longestTitle) {
			longestTitle = item.Title
		}
	}

	return fmt.Sprintf("【%d条相关】%s", len(cluster), longestTitle)
}

// generateClusterSummary 生成聚类摘要
func (na *NewsAggregator) generateClusterSummary(cluster []*models.NewsItem) string {
	if len(cluster) == 0 {
		return ""
	}

	if len(cluster) == 1 {
		return cluster[0].Summary
	}

	// 合并摘要
	var combinedSummary strings.Builder
	combinedSummary.WriteString(fmt.Sprintf("共%d条相关新闻：", len(cluster)))

	for i, item := range cluster {
		if i >= 3 { // 最多显示3条摘要
			break
		}
		combinedSummary.WriteString(fmt.Sprintf("\n%d. %s", i+1, item.Title))
	}

	return combinedSummary.String()
}

// getClusterTitle 获取聚类类别
func (na *NewsAggregator) getClusterCategory(cluster []*models.NewsItem) string {
	if len(cluster) == 0 {
		return "general"
	}

	// 统计类别出现频率
	categoryCount := make(map[string]int)
	for _, item := range cluster {
		categoryCount[item.Category]++
	}

	// 返回最频繁的类别
	var maxCategory string
	var maxCount int
	for category, count := range categoryCount {
		if count > maxCount {
			maxCount = count
			maxCategory = category
		}
	}

	return maxCategory
}

// extractNewsIDs 提取新闻ID列表
func (na *NewsAggregator) extractNewsIDs(cluster []*models.NewsItem) []string {
	var ids []string
	for _, item := range cluster {
		ids = append(ids, item.ID)
	}
	return ids
}

// extractStockCodes 提取股票代码
func (na *NewsAggregator) extractStockCodes(cluster []*models.NewsItem) []string {
	codeSet := make(map[string]bool)
	var codes []string

	for _, item := range cluster {
		for _, code := range item.StockCodes {
			if !codeSet[code] {
				codeSet[code] = true
				codes = append(codes, code)
			}
		}
	}

	return codes
}

// calculateClusterSimilarity 计算聚类相似度
func (na *NewsAggregator) calculateClusterSimilarity(cluster []*models.NewsItem) float64 {
	if len(cluster) < 2 {
		return 1.0
	}

	totalSimilarity := 0.0
	comparisons := 0

	for i := 0; i < len(cluster); i++ {
		for j := i + 1; j < len(cluster); j++ {
			similarity := na.calculateSimilarity(cluster[i], cluster[j])
			totalSimilarity += similarity
			comparisons++
		}
	}

	if comparisons == 0 {
		return 0
	}

	return totalSimilarity / float64(comparisons)
}

// calculateClusterImpact 计算聚类影响力
func (na *NewsAggregator) calculateClusterImpact(cluster []*models.NewsItem) float64 {
	if len(cluster) == 0 {
		return 0
	}

	// 基于新闻数量、相关性和时间新鲜度计算影响力
	var totalRelevance float64
	var totalFreshness float64

	now := time.Now()
	for _, item := range cluster {
		totalRelevance += item.Relevance

		// 时间新鲜度（越新越有影响力）
		hoursAgo := now.Sub(item.PublishTime).Hours()
		freshness := math.Max(0, 1.0-hoursAgo/24.0) // 24小时内新闻新鲜度递减
		totalFreshness += freshness
	}

	avgRelevance := totalRelevance / float64(len(cluster))
	avgFreshness := totalFreshness / float64(len(cluster))

	// 综合影响力评分
	impact := math.Sqrt(float64(len(cluster))) * avgRelevance * avgFreshness

	// 归一化到0-1范围
	return math.Min(1.0, impact/10.0)
}

// selectRepresentativeNews 选择代表性新闻
func (na *NewsAggregator) selectRepresentativeNews(cluster []*models.NewsItem) []*models.NewsItem {
	if len(cluster) == 0 {
		return nil
	}

	if len(cluster) == 1 {
		return cluster
	}

	// 按影响力和相关性排序
	sort.Slice(cluster, func(i, j int) bool {
		scoreI := cluster[i].Relevance * na.calculateFreshness(cluster[i])
		scoreJ := cluster[j].Relevance * na.calculateFreshness(cluster[j])
		return scoreI > scoreJ
	})

	// 返回最代表性的1-2条新闻
	representativeCount := 1
	if len(cluster) >= 5 {
		representativeCount = 2
	}

	return cluster[:representativeCount]
}

// calculateFreshness 计算新闻新鲜度
func (na *NewsAggregator) calculateFreshness(item *models.NewsItem) float64 {
	hoursAgo := time.Since(item.PublishTime).Hours()
	return math.Max(0, 1.0-hoursAgo/24.0)
}

// identifyTrendingTopics 识别热门话题
func (na *NewsAggregator) identifyTrendingTopics(news []*models.NewsItem) []*models.NewsItem {
	na.mutex.Lock()
	defer na.mutex.Unlock()

	// 检查热门话题规则
	var trendingRule *models.NewsAggregationRule
	for _, rule := range na.rules {
		if rule.RuleType == "trending" && rule.Enabled {
			trendingRule = rule
			break
		}
	}

	if trendingRule == nil {
		return news
	}

	// 按时间窗口分组新闻
	timeWindows := na.groupByTimeWindow(news, 2*time.Hour)

	// 识别热门话题
	var trendingNews []*models.NewsItem
	for windowKey, windowNews := range timeWindows {
		topicClusters := na.identifyTopicsInWindow(windowNews, trendingRule)

		// 为每个热门话题创建聚合新闻
		for _, topic := range topicClusters {
			if len(topic) >= 3 { // 至少3条相关新闻才算热门
				trendingItem := na.createTrendingNewsItem(topic, windowKey)
				trendingNews = append(trendingNews, trendingItem)
			}
		}
	}

	na.logger.Info("识别到 %d 个热门话题", len(trendingNews))
	return append(news, trendingNews...)
}

// identifyTopicsInWindow 在时间窗口内识别话题
func (na *NewsAggregator) identifyTopicsInWindow(news []*models.NewsItem, rule *models.NewsAggregationRule) [][]*models.NewsItem {
	// 基于关键词聚类
	keywordClusters := make(map[string][]*models.NewsItem)

	for _, item := range news {
		keywords := na.extractKeywords(item)
		for _, keyword := range keywords {
			keywordClusters[keyword] = append(keywordClusters[keyword], item)
		}
	}

	// 筛选出达到最小文章数的聚类
	minArticles := 3
	if val, exists := rule.Conditions["min_articles"]; exists {
		if parsed, err := strconv.Atoi(val); err == nil {
			minArticles = parsed
		}
	}

	var topics [][]*models.NewsItem
	for _, cluster := range keywordClusters {
		if len(cluster) >= minArticles {
			topics = append(topics, cluster)
		}
	}

	return topics
}

// extractKeywords 提取关键词
func (na *NewsAggregator) extractKeywords(item *models.NewsItem) []string {
	var keywords []string

	// 从标题中提取关键词
	titleWords := strings.Fields(strings.ToLower(item.Title))
	for _, word := range titleWords {
		if len(word) > 2 && !na.isStopWord(word) {
			keywords = append(keywords, word)
		}
	}

	// 从标签中提取关键词
	for _, tag := range item.Tags {
		if len(tag) > 1 {
			keywords = append(keywords, strings.ToLower(tag))
		}
	}

	// 从股票代码中提取
	for _, code := range item.StockCodes {
		keywords = append(keywords, strings.ToLower(code))
	}

	return keywords
}

// isStopWord 判断是否为停用词
func (na *NewsAggregator) isStopWord(word string) bool {
	stopWords := map[string]bool{
		"的": true, "了": true, "在": true, "是": true, "我": true,
		"有": true, "和": true, "就": true, "不": true, "人": true,
		"都": true, "一": true, "个": true, "上": true, "也": true,
		"很": true, "到": true, "说": true, "要": true, "去": true,
		"你": true, "会": true, "着": true, "没有": true, "看": true,
		"好": true, "自己": true, "这": true, "那": true, "就是": true,
		"the": true, "a": true, "an": true, "and": true, "or": true,
		"but": true, "in": true, "on": true, "at": true, "to": true,
		"for": true, "of": true, "with": true, "by": true, "as": true,
	}

	return stopWords[strings.TrimSpace(word)]
}

// createTrendingNewsItem 创建热门话题新闻项
func (na *NewsAggregator) createTrendingNewsItem(cluster []*models.NewsItem, windowKey string) *models.NewsItem {
	// 聚合信息
	title := fmt.Sprintf("🔥 热门话题：%s", na.generateClusterTitle(cluster))
	summary := fmt.Sprintf("在%s期间，共发现%d条相关新闻：", windowKey, len(cluster))

	// 提取所有股票代码
	var allCodes []string
	codeSet := make(map[string]bool)
	for _, item := range cluster {
		for _, code := range item.StockCodes {
			if !codeSet[code] {
				codeSet[code] = true
				allCodes = append(allCodes, code)
			}
		}
	}

	// 创建热门话题新闻项
	trendingItem := &models.NewsItem{
		ID:        fmt.Sprintf("trending_%s_%d", windowKey, len(cluster)),
		Title:     title,
		Summary:   summary,
		Content:   na.generateTrendingContent(cluster),
		Source:    "智股通聚合",
		Author:    "系统自动聚合",
		URL:       "",
		PublishTime: time.Now(),
		Category:  "热门话题",
		Tags:      []string{"热门话题", "聚合", "趋势"},
		Relevance: 1.0,
		StockCodes: allCodes,
		Sentiment: &models.SentimentResult{
			Label:      "trending",
			Score:      0.0,
			Confidence: 0.8,
			Emotions:   make(map[string]float64),
		},
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	return trendingItem
}

// generateTrendingContent 生成热门话题内容
func (na *NewsAggregator) generateTrendingContent(cluster []*models.NewsItem) string {
	var content strings.Builder
	content.WriteString("热门话题详情：\n\n")

	for i, item := range cluster {
		if i >= 5 { // 最多显示5条
			break
		}
		content.WriteString(fmt.Sprintf("%d. %s\n", i+1, item.Title))
		content.WriteString(fmt.Sprintf("   来源：%s\n", item.Source))
		content.WriteString(fmt.Sprintf("   时间：%s\n", item.PublishTime.Format("15:04")))
		if item.Summary != "" {
			content.WriteString(fmt.Sprintf("   摘要：%s\n", item.Summary))
		}
		content.WriteString("\n")
	}

	if len(cluster) > 5 {
		content.WriteString(fmt.Sprintf("...还有%d条相关新闻\n", len(cluster)-5))
	}

	return content.String()
}

// applyAggregationRules 应用聚合规则
func (na *NewsAggregator) applyAggregationRules(news []*models.NewsItem) []*models.NewsItem {
	// 这里可以实现更多的聚合规则处理
	// 目前主要依赖前面的去重、聚类和热门话题识别

	// 按时间倒序排列
	sort.Slice(news, func(i, j int) bool {
		return news[i].PublishTime.After(news[j].PublishTime)
	})

	return news
}

// GetClusters 获取聚类信息
func (na *NewsAggregator) GetClusters() map[string]*models.NewsCluster {
	na.mutex.RLock()
	defer na.mutex.RUnlock()

	result := make(map[string]*models.NewsCluster)
	for k, v := range na.clusters {
		result[k] = v
	}
	return result
}

// GetDuplicates 获取重复新闻信息
func (na *NewsAggregator) GetDuplicates() map[string][]string {
	na.mutex.RLock()
	defer na.mutex.RUnlock()

	result := make(map[string][]string)
	for k, v := range na.duplicates {
		result[k] = append([]string{}, v...)
	}
	return result
}

// 辅助函数
func parseFloat(s string) float64 {
	var f float64
	fmt.Sscanf(s, "%f", &f)
	return f
}

func parseInt(s string) int {
	var i int
	fmt.Sscanf(s, "%d", &i)
	return i
}