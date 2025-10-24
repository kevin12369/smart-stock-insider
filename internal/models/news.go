package models

import (
	"time"
)

// NewsItem 新闻条目
type NewsItem struct {
	ID          string    `json:"id"`
	Title       string    `json:"title"`
	Summary     string    `json:"summary"`
	Content     string    `json:"content"`
	Source      string    `json:"source"`
	Author      string    `json:"author"`
	URL         string    `json:"url"`
	PublishTime time.Time `json:"publish_time"`
	Category    string    `json:"category"`
	Tags        []string  `json:"tags"`
	Relevance   float64   `json:"relevance"`
	StockCodes  []string  `json:"stock_codes"`
	Sentiment   *SentimentResult `json:"sentiment"`
	CreatedAt   time.Time `json:"created_at"`
	UpdatedAt   time.Time `json:"updated_at"`
}

// SentimentResult 情感分析结果
type SentimentResult struct {
	Label      string             `json:"label"`       // positive, negative, neutral
	Score      float64            `json:"score"`       // -1 to 1
	Confidence float64            `json:"confidence"`  // 0 to 1
	Emotions   map[string]float64 `json:"emotions"`    // emotion scores
}

// NewsSource 新闻源配置
type NewsSource struct {
	ID          string `json:"id"`
	Name        string `json:"name"`
	BaseURL     string `json:"base_url"`
	APIKey      string `json:"api_key"`
	Enabled     bool   `json:"enabled"`
	RateLimit   int    `json:"rate_limit"`   // 每分钟请求限制
	LastFetch   time.Time `json:"last_fetch"`
	Description string `json:"description"`
}

// NewsAnalysisRequest 新闻分析请求
type NewsAnalysisRequest struct {
	StockCode     string   `json:"stock_code"`
	Days          int      `json:"days"`
	Sources       []string `json:"sources"`
	Categories    []string `json:"categories"`
	IncludeSocial bool     `json:"include_social"`
	Language      string   `json:"language"`
}

// NewsAnalysisResult 新闻分析结果
type NewsAnalysisResult struct {
	StockCode        string    `json:"stock_code"`
	AnalysisTime     time.Time `json:"analysis_time"`
	Days             int       `json:"days"`
	TotalNews        int       `json:"total_news"`
	PositiveNews     int       `json:"positive_news"`
	NegativeNews     int       `json:"negative_news"`
	NeutralNews      int       `json:"neutral_news"`
	OverallSentiment string    `json:"overall_sentiment"`
	SentimentScore   float64   `json:"sentiment_score"`
	SentimentTrend   string    `json:"sentiment_trend"`
	KeyTopics        []string  `json:"key_topics"`
	RiskEvents       []string  `json:"risk_events"`
	TopHeadlines     []NewsItem `json:"top_headlines"`
	NewsBySource     map[string]int `json:"news_by_source"`
	NewsByDay       []DailyNewsCount `json:"news_by_day"`
	Confidence      float64   `json:"confidence"`
}

// DailyNewsCount 每日新闻数量
type DailyNewsCount struct {
	Date        time.Time `json:"date"`
	TotalCount  int       `json:"total_count"`
	Positive    int       `json:"positive"`
	Negative    int       `json:"negative"`
	Neutral     int       `json:"neutral"`
}

// NewsFilter 新闻过滤器
type NewsFilter struct {
	StockCodes   []string  `json:"stock_codes"`
	Sources      []string  `json:"sources"`
	Categories   []string  `json:"categories"`
	Tags         []string  `json:"tags"`
	StartTime    *time.Time `json:"start_time"`
	EndTime      *time.Time `json:"end_time"`
	MinRelevance float64   `json:"min_relevance"`
	Sentiment    string    `json:"sentiment"`
}

// NewsAggregation 新闻聚合统计
type NewsAggregation struct {
	Source       string            `json:"source"`
	TotalCount   int               `json:"total_count"`
	SentimentDist map[string]int   `json:"sentiment_dist"`
	CategoryDist map[string]int    `json:"category_dist"`
	TopKeywords  []string          `json:"top_keywords"`
	LatestNews   time.Time         `json:"latest_news"`
}

// 东方财富新闻数据结构
type EastMoneyNewsItem struct {
	Id           string `json:"id"`
	Title        string `json:"title"`
	Digest       string `json:"digest"`
	Content      string `json:"content"`
	ShowTime     string `json:"showTime"`
	Author       string `json:"author"`
	Source       string `json:"source"`
	MediaCode    string `json:"mediaCode"`
	MediaName    string `json:"mediaName"`
	Video        bool   `json:"video"`
	ImageList    []string `json:"imageList"`
	RelatedStocks []EastMoneyRelatedStock `json:"relatedStocks"`
	Column        []EastMoneyColumn `json:"column"`
	ArtCreateTime int64  `json:"artCreateTime"`
}

type EastMoneyRelatedStock struct {
	StockCode string `json:"stockCode"`
	StockName string `json:"stockName"`
	Market    string `json:"market"`
}

type EastMoneyColumn struct {
	ColumnId   string `json:"columnId"`
	ColumnName string `json:"columnName"`
	ColumnCode string `json:"columnCode"`
}

// 同花顺新闻数据结构
type TongHuaShunNewsItem struct {
	Id          string `json:"id"`
	Title       string `json:"title"`
	Digest      string `json:"digest"`
	Content     string `json:"content"`
	ShowTime    string `json:"showTime"`
	Author      string `json:"author"`
	Source      string `json:"source"`
	CateCode    string `json:"cateCode"`
	CateName    string `json:"cateName"`
	Seq         string `json:"seq"`
	MediaCode   string `json:"mediaCode"`
	MediaName   string `json:"mediaName"`
	Tags        []string `json:"tags"`
	StockCodes  []string `json:"stockCodes"`
	IsImportant bool     `json:"isImportant"`
	ReadCount   int      `json:"readCount"`
	CreateTime  int64    `json:"createTime"`
}