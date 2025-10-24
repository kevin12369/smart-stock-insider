package models

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
)

// CreateExtendedNewsTables 创建扩展新闻相关数据库表
func CreateExtendedNewsTables(db *sql.DB) error {
	logger := log.Default()

	// 创建扩展新闻源表
	sourceQuery := `
	CREATE TABLE IF NOT EXISTS extended_news_sources (
		id TEXT PRIMARY KEY,
		name TEXT NOT NULL,
		base_url TEXT NOT NULL,
		api_key TEXT,
		enabled BOOLEAN NOT NULL DEFAULT 1,
		rate_limit INTEGER NOT NULL DEFAULT 60,
		priority INTEGER NOT NULL DEFAULT 1,
		category TEXT NOT NULL DEFAULT 'news',
		description TEXT,
		headers TEXT, -- JSON格式存储请求头
		params TEXT, -- JSON格式存储默认参数
		updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
	);`

	if _, err := db.Exec(sourceQuery); err != nil {
		return fmt.Errorf("创建扩展新闻源表失败: %v", err)
	}

	// 创建新闻源状态表
	statusQuery := `
	CREATE TABLE IF NOT EXISTS news_source_status (
		source_id TEXT PRIMARY KEY,
		name TEXT NOT NULL,
		status TEXT NOT NULL DEFAULT 'active',
		last_check DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
		error_count INTEGER NOT NULL DEFAULT 0,
		success_rate REAL NOT NULL DEFAULT 1.0,
		response_time INTEGER NOT NULL DEFAULT 1000,
		error_message TEXT,
		updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
		FOREIGN KEY (source_id) REFERENCES extended_news_sources(id) ON DELETE CASCADE
	);`

	if _, err := db.Exec(statusQuery); err != nil {
		return fmt.Errorf("创建新闻源状态表失败: %v", err)
	}

	// 创建新闻源指标表
	metricsQuery := `
	CREATE TABLE IF NOT EXISTS news_source_metrics (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		source_id TEXT NOT NULL,
		date DATE NOT NULL,
		request_count INTEGER NOT NULL DEFAULT 0,
		success_count INTEGER NOT NULL DEFAULT 0,
		error_count INTEGER NOT NULL DEFAULT 0,
		articles_fetched INTEGER NOT NULL DEFAULT 0,
		avg_response_time REAL NOT NULL DEFAULT 0.0,
		data_quality REAL NOT NULL DEFAULT 0.0,
		coverage TEXT, -- JSON格式存储覆盖的股票板块
		last_reset DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
		updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
		FOREIGN KEY (source_id) REFERENCES extended_news_sources(id) ON DELETE CASCADE,
		UNIQUE(source_id, date)
	);`

	if _, err := db.Exec(metricsQuery); err != nil {
		return fmt.Errorf("创建新闻源指标表失败: %v", err)
	}

	// 创建新闻聚合规则表
	rulesQuery := `
	CREATE TABLE IF NOT EXISTS news_aggregation_rules (
		id TEXT PRIMARY KEY,
		name TEXT NOT NULL,
		description TEXT,
		rule_type TEXT NOT NULL DEFAULT 'duplicate',
		conditions TEXT, -- JSON格式存储规则条件
		actions TEXT, -- JSON格式存储处理动作
		enabled BOOLEAN NOT NULL DEFAULT 1,
		priority INTEGER NOT NULL DEFAULT 1,
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
		updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
	);`

	if _, err := db.Exec(rulesQuery); err != nil {
		return fmt.Errorf("创建新闻聚合规则表失败: %v", err)
	}

	// 创建新闻聚类表
	clusterQuery := `
	CREATE TABLE IF NOT EXISTS news_clusters (
		id TEXT PRIMARY KEY,
		title TEXT NOT NULL,
		summary TEXT,
		category TEXT NOT NULL DEFAULT 'general',
		news_ids TEXT, -- JSON格式存储新闻ID列表
		stock_codes TEXT, -- JSON格式存储股票代码
		centroid TEXT, -- 中心新闻ID
		similarity REAL NOT NULL DEFAULT 0.0,
		impact_score REAL NOT NULL DEFAULT 0.0,
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
		updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
	);`

	if _, err := db.Exec(clusterQuery); err != nil {
		return fmt.Errorf("创建新闻聚类表失败: %v", err)
	}

	// 创建新闻聚类关联表
	clusterNewsQuery := `
	CREATE TABLE IF NOT EXISTS cluster_news_relations (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		cluster_id TEXT NOT NULL,
		news_id TEXT NOT NULL,
		similarity_score REAL NOT NULL DEFAULT 0.0,
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
		FOREIGN KEY (cluster_id) REFERENCES news_clusters(id) ON DELETE CASCADE,
		FOREIGN KEY (news_id) REFERENCES news_items(id) ON DELETE CASCADE,
		UNIQUE(cluster_id, news_id)
	);`

	if _, err := db.Exec(clusterNewsQuery); err != nil {
		return fmt.Errorf("创建新闻聚类关联表失败: %v", err)
	}

	// 创建新闻源配置表
	configQuery := `
	CREATE TABLE IF NOT EXISTS news_source_config (
		id INTEGER PRIMARY KEY CHECK (id = 1),
		config_version TEXT NOT NULL DEFAULT '1.0',
		sources TEXT NOT NULL, -- JSON格式存储所有新闻源配置
		updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
	);`

	if _, err := db.Exec(configQuery); err != nil {
		return fmt.Errorf("创建新闻源配置表失败: %v", err)
	}

	// 创建索引
	indexes := []string{
		"CREATE INDEX IF NOT EXISTS idx_news_sources_category ON extended_news_sources(category)",
		"CREATE INDEX IF NOT EXISTS idx_news_sources_enabled ON extended_news_sources(enabled)",
		"CREATE INDEX IF NOT EXISTS idx_news_sources_priority ON extended_news_sources(priority)",
		"CREATE INDEX IF NOT EXISTS idx_news_source_status ON news_source_status(status)",
		"CREATE INDEX IF NOT EXISTS idx_news_source_last_check ON news_source_status(last_check)",
		"CREATE INDEX IF NOT EXISTS idx_news_metrics_source_date ON news_source_metrics(source_id, date)",
		"CREATE INDEX IF NOT EXISTS idx_news_rules_enabled ON news_aggregation_rules(enabled)",
		"CREATE INDEX IF NOT EXISTS idx_news_rules_priority ON news_aggregation_rules(priority)",
		"CREATE INDEX IF NOT EXISTS idx_news_clusters_category ON news_clusters(category)",
		"CREATE INDEX IF NOT EXISTS idx_news_clusters_impact ON news_clusters(impact_score)",
		"CREATE INDEX IF NOT EXISTS idx_cluster_news_cluster ON cluster_news_relations(cluster_id)",
		"CREATE INDEX IF NOT EXISTS idx_cluster_news_news ON cluster_news_relations(news_id)",
	}

	for _, indexQuery := range indexes {
		if _, err := db.Exec(indexQuery); err != nil {
			logger.Printf("创建索引失败: %s, 错误: %v", indexQuery, err)
		}
	}

	// 初始化默认配置
	if err := initDefaultExtendedNewsConfig(db); err != nil {
		logger.Printf("初始化默认扩展新闻配置失败: %v", err)
	}

	logger.Println("扩展新闻数据库表创建成功")
	return nil
}

// initDefaultExtendedNewsConfig 初始化默认扩展新闻配置
func initDefaultExtendedNewsConfig(db *sql.DB) error {
	// 检查是否已有配置
	var count int
	err := db.QueryRow("SELECT COUNT(*) FROM news_source_config").Scan(&count)
	if err != nil {
		return err
	}

	if count > 0 {
		return nil // 配置已存在
	}

	// 插入默认配置
	_, err = db.Exec(`
		INSERT INTO news_source_config (id, config_version, sources)
		VALUES (1, '1.0', '{"auto_refresh": true, "refresh_interval": 300, "max_sources": 10}')
	`)

	return err
}

// ExtendedNewsSourceRepository 扩展新闻源数据访问层
type ExtendedNewsSourceRepository struct {
	db     *sql.DB
	logger *log.Logger
}

// NewExtendedNewsSourceRepository 创建扩展新闻源数据访问层
func NewExtendedNewsSourceRepository(db *sql.DB) *ExtendedNewsSourceRepository {
	return &ExtendedNewsSourceRepository{
		db:     db,
		logger: log.Default(),
	}
}

// SaveExtendedNewsSource 保存扩展新闻源
func (repo *ExtendedNewsSourceRepository) SaveExtendedNewsSource(source *AdditionalNewsSource) error {
	query := `
	INSERT OR REPLACE INTO extended_news_sources
	(id, name, base_url, api_key, enabled, rate_limit, priority, category, description, headers, params, updated_at)
	VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
	`

	headersJSON, _ := json.Marshal(source.Headers)
	paramsJSON, _ := json.Marshal(source.Params)

	_, err := repo.db.Exec(query, source.ID, source.Name, source.BaseURL, source.APIKey,
		source.Enabled, source.RateLimit, source.Priority, source.Category,
		source.Description, string(headersJSON), string(paramsJSON))

	return err
}

// GetExtendedNewsSources 获取所有扩展新闻源
func (repo *ExtendedNewsSourceRepository) GetExtendedNewsSources() ([]*AdditionalNewsSource, error) {
	query := `
		SELECT id, name, base_url, api_key, enabled, rate_limit, priority, category,
			   description, headers, params, updated_at
		FROM extended_news_sources
		ORDER BY priority ASC, name ASC
	`

	rows, err := repo.db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var sources []*AdditionalNewsSource
	for rows.Next() {
		source := &AdditionalNewsSource{}
		var headersJSON, paramsJSON string

		err := rows.Scan(&source.ID, &source.Name, &source.BaseURL, &source.APIKey,
			&source.Enabled, &source.RateLimit, &source.Priority, &source.Category,
			&source.Description, &headersJSON, &paramsJSON, &source.UpdatedAt)
		if err != nil {
			continue
		}

		// 解析JSON字段
		if headersJSON != "" {
			json.Unmarshal([]byte(headersJSON), &source.Headers)
		}
		if paramsJSON != "" {
			json.Unmarshal([]byte(paramsJSON), &source.Params)
		}

		sources = append(sources, source)
	}

	return sources, nil
}

// SaveNewsSourceStatus 保存新闻源状态
func (repo *ExtendedNewsSourceRepository) SaveNewsSourceStatus(status *NewsSourceStatus) error {
	query := `
	INSERT OR REPLACE INTO news_source_status
	(source_id, name, status, last_check, error_count, success_rate, response_time, error_message, updated_at)
	VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
	`

	_, err := repo.db.Exec(query, status.SourceID, status.Name, status.Status,
		status.LastCheck, status.ErrorCount, status.SuccessRate,
		status.ResponseTime, status.ErrorMessage)

	return err
}

// GetNewsSourceStatus 获取新闻源状态
func (repo *ExtendedNewsSourceRepository) GetNewsSourceStatus(sourceID string) (*NewsSourceStatus, error) {
	query := `
		SELECT source_id, name, status, last_check, error_count, success_rate, response_time, error_message, updated_at
		FROM news_source_status
		WHERE source_id = ?
	`

	row := repo.db.QueryRow(query, sourceID)
	status := &NewsSourceStatus{}

	err := row.Scan(&status.SourceID, &status.Name, &status.Status,
		&status.LastCheck, &status.ErrorCount, &status.SuccessRate,
		&status.ResponseTime, &status.ErrorMessage, &status.UpdatedAt)

	if err != nil {
		return nil, err
	}

	return status, nil
}

// SaveNewsSourceMetrics 保存新闻源指标
func (repo *ExtendedNewsSourceRepository) SaveNewsSourceMetrics(metrics *NewsSourceMetrics) error {
	query := `
	INSERT OR REPLACE INTO news_source_metrics
	(source_id, date, request_count, success_count, error_count, articles_fetched,
	 avg_response_time, data_quality, coverage, last_reset, updated_at)
	VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
	`

	coverageJSON, _ := json.Marshal(metrics.Coverage)

	_, err := repo.db.Exec(query, metrics.SourceID, metrics.Date.Format("2006-01-02"),
		metrics.RequestCount, metrics.SuccessCount, metrics.ErrorCount,
		metrics.ArticlesFetched, metrics.AvgResponseTime, metrics.DataQuality,
		string(coverageJSON), metrics.LastReset)

	return err
}

// GetNewsSourceMetrics 获取新闻源指标
func (repo *ExtendedNewsSourceRepository) GetNewsSourceMetrics(sourceID string, days int) ([]*NewsSourceMetrics, error) {
	query := `
		SELECT source_id, date, request_count, success_count, error_count, articles_fetched,
			   avg_response_time, data_quality, coverage, last_reset, created_at, updated_at
		FROM news_source_metrics
		WHERE source_id = ? AND date >= date('now', '-' || ? || ' days')
		ORDER BY date DESC
	`

	rows, err := repo.db.Query(query, sourceID, days)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var metricsList []*NewsSourceMetrics
	for rows.Next() {
		metrics := &NewsSourceMetrics{}
		var coverageJSON string

		err := rows.Scan(&metrics.SourceID, &metrics.Date, &metrics.RequestCount,
			&metrics.SuccessCount, &metrics.ErrorCount, &metrics.ArticlesFetched,
			&metrics.AvgResponseTime, &metrics.DataQuality, &coverageJSON,
			&metrics.LastReset, &metrics.CreatedAt, &metrics.UpdatedAt)
		if err != nil {
			continue
		}

		// 解析coverage字段
		if coverageJSON != "" {
			json.Unmarshal([]byte(coverageJSON), &metrics.Coverage)
		}

		metricsList = append(metricsList, metrics)
	}

	return metricsList, nil
}