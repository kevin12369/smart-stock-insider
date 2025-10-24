package models

import (
	"time"
)

// AdditionalNewsSource 扩展新闻源配置
type AdditionalNewsSource struct {
	ID          string            `json:"id"`
	Name        string            `json:"name"`
	BaseURL     string            `json:"base_url"`
	APIKey      string            `json:"api_key,omitempty"`
	Enabled     bool              `json:"enabled"`
	RateLimit   int               `json:"rate_limit"`   // 每分钟请求限制
	Priority    int               `json:"priority"`     // 优先级 1-5
	Category    string            `json:"category"`     // news, social, professional
	Description string            `json:"description"`
	Headers     map[string]string `json:"headers,omitempty"`   // 自定义请求头
	Params      map[string]string `json:"params,omitempty"`    // 默认参数
	UpdatedAt   time.Time         `json:"updated_at"`
}

// SinaNewsResponse 新浪财经新闻响应
type SinaNewsResponse struct {
	Code    int `json:"code"`
	Message string `json:"msg"`
	Data    struct {
		List []SinaNewsItem `json:"list"`
	} `json:"data"`
}

type SinaNewsItem struct {
	ID          string    `json:"id"`
	Title       string    `json:"title"`
	Summary     string    `json:"summary"`
	Content     string    `json:"content"`
	URL         string    `json:"url"`
	Author      string    `json:"author"`
	Source      string    `json:"source"`
	Category    string    `json:"category"`
	Tags        []string  `json:"tags"`
	PublishTime time.Time `json:"publish_time"`
	StockCodes  []string  `json:"stock_codes"`
	Sentiment   *SentimentResult `json:"sentiment,omitempty"`
}

// TencentNewsResponse 腾讯财经新闻响应
type TencentNewsResponse struct {
	TimeStamp int64  `json:"timestamp"`
	ErrorCode int    `json:"error_code"`
	ErrorMessage string `json:"error_message"`
	Data      struct {
		Total int               `json:"total"`
		List []TencentNewsItem  `json:"list"`
	} `json:"data"`
}

type TencentNewsItem struct {
	ID          string    `json:"id"`
	Title       string    `json:"title"`
	Summary     string    `json:"summary"`
	Content     string    `json:"content"`
	URL         string    `json:"url"`
	Author      string    `json:"author"`
	Column      string    `json:"column"`      // 栏目
	Category    string    `json:"category"`
	Tags        []string  `json:"tags"`
	PublishTime time.Time `json:"publish_time"`
	StockCodes  []string  `json:"stock_codes"`
	ViewCount   int       `json:"view_count"`
	Sentiment   *SentimentResult `json:"sentiment,omitempty"`
}

// XueqiuNewsResponse 雪球新闻响应
type XueqiuNewsResponse struct {
	ErrorDescription string `json:"error_description"`
	ErrorCode       int    `json:"error_code"`
	Data           struct {
		Count   int              `json:"count"`
		HasMore bool             `json:"has_more"`
		List    []XueqiuNewsItem `json:"list"`
	} `json:"data"`
}

type XueqiuNewsItem struct {
	ID          string    `json:"id"`
	Title       string    `json:"title"`
	Text        string    `json:"text"`        // 雪球特有的文本内容
	URL         string    `json:"url"`
	User        XueqiuUser `json:"user"`      // 发布用户信息
	Target      XueqiuTarget `json:"target"` // 相关股票
	CreatedAt   time.Time `json:"created_at"`
	CommentCount int       `json:"comment_count"`
	RepostCount  int       `json:"repost_count"`
	LikeCount    int       `json:"like_count"`
	ReplyCount   int       `json:"reply_count"`
	Symbols      []string  `json:"symbols"`    // 相关股票代码
	Tags        []string  `json:"tags"`
	Sentiment   *SentimentResult `json:"sentiment,omitempty"`
}

type XueqiuUser struct {
	ID          string `json:"id"`
	ScreenName  string `json:"screen_name"`
	Description string `json:"description"`
	Verified    bool   `json:"verified"`
	Followers   int    `json:"followers"`
}

type XueqiuTarget struct {
	Symbol string `json:"symbol"`
	Name   string `json:"name"`
	Type   string `json:"type"`
}

// HexunNewsResponse 和讯网新闻响应
type HexunNewsResponse struct {
	Success bool `json:"success"`
	Message string `json:"message"`
	Data    struct {
		Total int             `json:"total"`
		Page  int             `json:"page"`
		Size  int             `json:"size"`
		List  []HexunNewsItem `json:"list"`
	} `json:"data"`
}

type HexunNewsItem struct {
	ID          string    `json:"id"`
	Title       string    `json:"title"`
	Summary     string    `json:"summary"`
	Content     string    `json:"content"`
	URL         string    `json:"url"`
	Author      string    `json:"author"`
	Column      string    `json:"column"`
	Category    string    `json:"category"`
	Tags        []string  `json:"tags"`
	PublishTime time.Time `json:"publish_time"`
	StockCodes  []string  `json:"stock_codes"`
	Editor      string    `json:"editor"`
	Source      string    `json:"source"`
	Sentiment   *SentimentResult `json:"sentiment,omitempty"`
}

// NewsSourceConfig 新闻源配置管理
type NewsSourceConfig struct {
	Sources map[string]*AdditionalNewsSource `json:"sources"`
	UpdatedAt time.Time                     `json:"updated_at"`
}

// NewsSourceStatus 新闻源状态
type NewsSourceStatus struct {
	SourceID    string    `json:"source_id"`
	Name        string    `json:"name"`
	Status      string    `json:"status"`      // active, inactive, error, rate_limited
	LastCheck   time.Time `json:"last_check"`
	ErrorCount  int       `json:"error_count"`
	SuccessRate float64   `json:"success_rate"`
	ResponseTime int64    `json:"response_time"` // 毫秒
	ErrorMessage string   `json:"error_message,omitempty"`
	UpdatedAt   time.Time `json:"updated_at"`
}

// NewsSourceMetrics 新闻源指标
type NewsSourceMetrics struct {
	SourceID        string    `json:"source_id"`
	Date            time.Time `json:"date"`
	RequestCount    int       `json:"request_count"`
	SuccessCount    int       `json:"success_count"`
	ErrorCount      int       `json:"error_count"`
	ArticlesFetched int       `json:"articles_fetched"`
	AvgResponseTime float64   `json:"avg_response_time"`
	DataQuality     float64   `json:"data_quality"`     // 0-1 数据质量评分
	Coverage        []string  `json:"coverage"`         // 覆盖的股票板块
	LastReset       time.Time `json:"last_reset"`
	CreatedAt       time.Time `json:"created_at"`
	UpdatedAt       time.Time `json:"updated_at"`
}

// NewsAggregationRule 新闻聚合规则
type NewsAggregationRule struct {
	ID          string            `json:"id"`
	Name        string            `json:"name"`
	Description string            `json:"description"`
	RuleType    string            `json:"rule_type"`     // duplicate, similar, trending
	Conditions  map[string]string `json:"conditions"`    // 规则条件
	Actions     map[string]string `json:"actions"`       // 处理动作
	Enabled     bool              `json:"enabled"`
	Priority    int               `json:"priority"`
	CreatedAt   time.Time         `json:"created_at"`
	UpdatedAt   time.Time         `json:"updated_at"`
}

// NewsCluster 新闻聚类
type NewsCluster struct {
	ID          string      `json:"id"`
	Title       string      `json:"title"`
	Summary     string      `json:"summary"`
	Category    string      `json:"category"`
	NewsIDs     []string    `json:"news_ids"`     // 聚类的新闻ID列表
	StockCodes  []string    `json:"stock_codes"`
	Centroid    string      `json:"centroid"`     // 中心新闻ID
	Similarity  float64     `json:"similarity"`   // 相似度阈值
	ImpactScore float64     `json:"impact_score"` // 影响力评分
	CreatedAt  time.Time   `json:"created_at"`
	UpdatedAt  time.Time   `json:"updated_at"`
}