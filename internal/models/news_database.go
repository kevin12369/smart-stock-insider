package models

import (
	"database/sql"
	"encoding/json"
	"strings"
	"time"

	_ "modernc.org/sqlite"
)

// CreateNewsTables 创建新闻相关数据表
func CreateNewsTables(db *sql.DB) error {
	queries := []string{
		`CREATE TABLE IF NOT EXISTS news_items (
			id TEXT PRIMARY KEY,
			title TEXT NOT NULL,
			summary TEXT,
			content TEXT,
			source TEXT NOT NULL,
			author TEXT,
			url TEXT,
			publish_time DATETIME NOT NULL,
			category TEXT,
			tags TEXT,
			relevance REAL DEFAULT 0.0,
			stock_codes TEXT,
			sentiment_label TEXT,
			sentiment_score REAL DEFAULT 0.0,
			sentiment_confidence REAL DEFAULT 0.0,
			emotions TEXT,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
		) WITHOUT ROWID`,
		`CREATE INDEX IF NOT EXISTS idx_news_items_source ON news_items(source)`,
		`CREATE INDEX IF NOT EXISTS idx_news_items_publish_time ON news_items(publish_time)`,
		`CREATE INDEX IF NOT EXISTS idx_news_items_category ON news_items(category)`,
		`CREATE INDEX IF NOT EXISTS idx_news_items_sentiment ON news_items(sentiment_label)`,
		`CREATE INDEX IF NOT EXISTS idx_news_items_relevance ON news_items(relevance)`,
		`CREATE INDEX IF NOT EXISTS idx_news_items_stock_codes ON news_items(stock_codes)`,
		`CREATE TABLE IF NOT EXISTS news_sources (
			id TEXT PRIMARY KEY,
			name TEXT NOT NULL,
			base_url TEXT NOT NULL,
			api_key TEXT,
			enabled BOOLEAN DEFAULT 1,
			rate_limit INTEGER DEFAULT 60,
			last_fetch DATETIME,
			description TEXT,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
		) WITHOUT ROWID`,
		`CREATE TABLE IF NOT EXISTS news_analysis_cache (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			stock_code TEXT NOT NULL,
			analysis_days INTEGER NOT NULL,
			sources TEXT,
			total_news INTEGER DEFAULT 0,
			positive_news INTEGER DEFAULT 0,
			negative_news INTEGER DEFAULT 0,
			neutral_news INTEGER DEFAULT 0,
			overall_sentiment TEXT DEFAULT 'neutral',
			sentiment_score REAL DEFAULT 0.0,
			sentiment_trend TEXT DEFAULT 'stable',
			key_topics TEXT,
			risk_events TEXT,
			confidence REAL DEFAULT 0.7,
			analysis_result TEXT,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			UNIQUE(stock_code, analysis_days, sources)
		)`,
		`CREATE INDEX IF NOT EXISTS idx_news_analysis_cache_stock ON news_analysis_cache(stock_code)`,
		`CREATE INDEX IF NOT EXISTS idx_news_analysis_cache_created ON news_analysis_cache(created_at)`,
	}

	for _, query := range queries {
		if _, err := db.Exec(query); err != nil {
			return err
		}
	}

	return nil
}

// NewsRepository 新闻数据仓库
type NewsRepository struct {
	db *sql.DB
}

// NewNewsRepository 创建新闻仓库
func NewNewsRepository(db *sql.DB) *NewsRepository {
	return &NewsRepository{db: db}
}

// SaveNewsItem 保存新闻条目
func (r *NewsRepository) SaveNewsItem(item *NewsItem) error {
	tagsJSON, _ := json.Marshal(item.Tags)
	stockCodesJSON, _ := json.Marshal(item.StockCodes)
	var emotionsJSON []byte
	if item.Sentiment != nil {
		emotionsJSON, _ = json.Marshal(item.Sentiment.Emotions)
	}

	query := `INSERT OR REPLACE INTO news_items
		(id, title, summary, content, source, author, url, publish_time, category, tags,
		 relevance, stock_codes, sentiment_label, sentiment_score, sentiment_confidence, emotions,
		 created_at, updated_at)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`

	var sentimentLabel string
	var sentimentScore, sentimentConfidence float64
	if item.Sentiment != nil {
		sentimentLabel = item.Sentiment.Label
		sentimentScore = item.Sentiment.Score
		sentimentConfidence = item.Sentiment.Confidence
	}

	_, err := r.db.Exec(query,
		item.ID, item.Title, item.Summary, item.Content, item.Source, item.Author, item.URL,
		item.PublishTime, item.Category, string(tagsJSON), item.Relevance, string(stockCodesJSON),
		sentimentLabel, sentimentScore, sentimentConfidence, string(emotionsJSON),
		item.CreatedAt, item.UpdatedAt)

	return err
}

// GetNewsItems 获取新闻列表
func (r *NewsRepository) GetNewsItems(filter *NewsFilter, limit, offset int) ([]*NewsItem, error) {
	query := `SELECT id, title, summary, content, source, author, url, publish_time,
		category, tags, relevance, stock_codes, sentiment_label, sentiment_score,
		sentiment_confidence, emotions, created_at, updated_at
		FROM news_items WHERE 1=1`

	args := make([]interface{}, 0)

	// 构建WHERE条件
	if filter != nil {
		if len(filter.Sources) > 0 {
			placeholders := make([]string, len(filter.Sources))
			for i, source := range filter.Sources {
				placeholders[i] = "?"
				args = append(args, source)
			}
			query += " AND source IN (" + strings.Join(placeholders, ",") + ")"
		}

		if len(filter.Categories) > 0 {
			placeholders := make([]string, len(filter.Categories))
			for i, category := range filter.Categories {
				placeholders[i] = "?"
				args = append(args, category)
			}
			query += " AND category IN (" + strings.Join(placeholders, ",") + ")"
		}

		if filter.Sentiment != "" {
			query += " AND sentiment_label = ?"
			args = append(args, filter.Sentiment)
		}

		if filter.MinRelevance > 0 {
			query += " AND relevance >= ?"
			args = append(args, filter.MinRelevance)
		}

		if filter.StartTime != nil {
			query += " AND publish_time >= ?"
			args = append(args, filter.StartTime)
		}

		if filter.EndTime != nil {
			query += " AND publish_time <= ?"
			args = append(args, filter.EndTime)
		}
	}

	query += " ORDER BY publish_time DESC, relevance DESC LIMIT ? OFFSET ?"
	args = append(args, limit, offset)

	rows, err := r.db.Query(query, args...)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var items []*NewsItem
	for rows.Next() {
		item := &NewsItem{}
		var tagsJSON, stockCodesJSON, emotionsJSON []byte
		var sentimentLabel sql.NullString
		var sentimentScore, sentimentConfidence sql.NullFloat64

		err := rows.Scan(
			&item.ID, &item.Title, &item.Summary, &item.Content, &item.Source,
			&item.Author, &item.URL, &item.PublishTime, &item.Category,
			&tagsJSON, &item.Relevance, &stockCodesJSON, &sentimentLabel,
			&sentimentScore, &sentimentConfidence, &emotionsJSON,
			&item.CreatedAt, &item.UpdatedAt,
		)
		if err != nil {
			return nil, err
		}

		// 解析JSON字段
		json.Unmarshal(tagsJSON, &item.Tags)
		json.Unmarshal(stockCodesJSON, &item.StockCodes)

		if sentimentLabel.Valid {
			item.Sentiment = &SentimentResult{
				Label:      sentimentLabel.String,
				Score:      sentimentScore.Float64,
				Confidence: sentimentConfidence.Float64,
				Emotions:   make(map[string]float64),
			}
			json.Unmarshal(emotionsJSON, &item.Sentiment.Emotions)
		}

		items = append(items, item)
	}

	return items, nil
}

// SaveNewsSource 保存新闻源
func (r *NewsRepository) SaveNewsSource(source *NewsSource) error {
	query := `INSERT OR REPLACE INTO news_sources
		(id, name, base_url, api_key, enabled, rate_limit, last_fetch,
		 description, created_at, updated_at)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`

	_, err := r.db.Exec(query,
		source.ID, source.Name, source.BaseURL, source.APIKey, source.Enabled,
		source.RateLimit, source.LastFetch, source.Description,
		time.Now(), time.Now())

	return err
}

// GetNewsSources 获取新闻源列表
func (r *NewsRepository) GetNewsSources() ([]*NewsSource, error) {
	query := `SELECT id, name, base_url, api_key, enabled, rate_limit,
		last_fetch, description FROM news_sources ORDER BY name`

	rows, err := r.db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var sources []*NewsSource
	for rows.Next() {
		source := &NewsSource{}
		err := rows.Scan(&source.ID, &source.Name, &source.BaseURL, &source.APIKey,
			&source.Enabled, &source.RateLimit, &source.LastFetch, &source.Description)
		if err != nil {
			return nil, err
		}
		sources = append(sources, source)
	}

	return sources, nil
}

// SaveAnalysisCache 保存分析缓存
func (r *NewsRepository) SaveAnalysisCache(result *NewsAnalysisResult) error {
	keyTopicsJSON, _ := json.Marshal(result.KeyTopics)
	riskEventsJSON, _ := json.Marshal(result.RiskEvents)
	resultJSON, _ := json.Marshal(result)

	query := `INSERT OR REPLACE INTO news_analysis_cache
		(stock_code, analysis_days, sources, total_news, positive_news, negative_news,
		 neutral_news, overall_sentiment, sentiment_score, sentiment_trend,
		 key_topics, risk_events, confidence, analysis_result, created_at)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`

	sourcesJSON, _ := json.Marshal(result.TopHeadlines) // 使用TopHeadlines作为源信息
	_, err := r.db.Exec(query,
		result.StockCode, result.Days, string(sourcesJSON), result.TotalNews,
		result.PositiveNews, result.NegativeNews, result.NeutralNews,
		result.OverallSentiment, result.SentimentScore, result.SentimentTrend,
		string(keyTopicsJSON), string(riskEventsJSON), result.Confidence,
		string(resultJSON), result.AnalysisTime)

	return err
}

// GetAnalysisCache 获取分析缓存
func (r *NewsRepository) GetAnalysisCache(stockCode string, days int) (*NewsAnalysisResult, error) {
	query := `SELECT analysis_result FROM news_analysis_cache
		WHERE stock_code = ? AND analysis_days = ?
		ORDER BY created_at DESC LIMIT 1`

	var resultJSON []byte
	err := r.db.QueryRow(query, stockCode, days).Scan(&resultJSON)
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, nil
		}
		return nil, err
	}

	var result NewsAnalysisResult
	err = json.Unmarshal(resultJSON, &result)
	if err != nil {
		return nil, err
	}

	return &result, nil
}

// GetNewsStats 获取新闻统计信息
func (r *NewsRepository) GetNewsStats(stockCode string, days int) (map[string]interface{}, error) {
	query := `SELECT
		COUNT(*) as total_news,
		COUNT(CASE WHEN sentiment_label = 'positive' THEN 1 END) as positive_news,
		COUNT(CASE WHEN sentiment_label = 'negative' THEN 1 END) as negative_news,
		COUNT(CASE WHEN sentiment_label = 'neutral' THEN 1 END) as neutral_news,
		AVG(sentiment_score) as avg_sentiment,
		COUNT(DISTINCT source) as source_count,
		MAX(publish_time) as latest_news
		FROM news_items
		WHERE publish_time >= datetime('now', '-' || ? || ' days')`

	args := []interface{}{days}
	if stockCode != "" {
		query += " AND stock_codes LIKE ?"
		args = append(args, "%"+stockCode+"%")
	}

	stats := make(map[string]interface{})
	var totalNews, positiveNews, negativeNews, neutralNews, sourceCount int
	var avgSentiment float64
	var latestNews time.Time

	err := r.db.QueryRow(query, args...).Scan(
		&totalNews, &positiveNews, &negativeNews, &neutralNews,
		&avgSentiment, &sourceCount, &latestNews)
	if err != nil {
		return nil, err
	}

	stats["total_news"] = totalNews
	stats["positive_news"] = positiveNews
	stats["negative_news"] = negativeNews
	stats["neutral_news"] = neutralNews
	stats["avg_sentiment"] = avgSentiment
	stats["source_count"] = sourceCount
	stats["latest_news"] = latestNews

	return stats, nil
}