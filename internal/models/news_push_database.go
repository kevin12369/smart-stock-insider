package models

import (
	"database/sql"
	"fmt"
	"log"
)

// CreateNewsPushTables 创建新闻推送相关数据库表
func CreateNewsPushTables(db *sql.DB) error {
	logger := log.Default()

	// 创建推送服务表
	pushServiceQuery := `
	CREATE TABLE IF NOT EXISTS push_services (
		id TEXT PRIMARY KEY,
		name TEXT NOT NULL,
		type TEXT NOT NULL CHECK (type IN ('websocket', 'sse', 'push_notification')),
		config TEXT NOT NULL,
		enabled BOOLEAN NOT NULL DEFAULT 1,
		priority INTEGER NOT NULL DEFAULT 1,
		rate_limit INTEGER NOT NULL DEFAULT 0,
		success_rate REAL NOT NULL DEFAULT 0.0,
		error_rate REAL NOT NULL DEFAULT 0.0,
		connected_users INTEGER NOT NULL DEFAULT 0,
		message_count BIGINT NOT NULL DEFAULT 0,
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
		updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
	);`

	if _, err := db.Exec(pushServiceQuery); err != nil {
		return fmt.Errorf("创建推送服务表失败: %v", err)
	}

	// 创建推送消息表
	pushMessageQuery := `
	CREATE TABLE IF NOT EXISTS push_messages (
		id TEXT PRIMARY KEY,
		type TEXT NOT NULL CHECK (type IN ('news', 'alert', 'analysis', 'portfolio_update')),
		title TEXT NOT NULL,
		content TEXT NOT NULL,
		summary TEXT,
		url TEXT,
		image_url TEXT,
		category TEXT,
		priority TEXT NOT NULL CHECK (priority IN ('high', 'medium', 'low')),
		tags TEXT, -- JSON格式存储标签数组
		data TEXT, -- JSON格式存储额外数据
		target_id TEXT,
		target_data TEXT, -- JSON格式存储目标数据
		schedule_at DATETIME,
		expires_at DATETIME,
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
		updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
		delivered BOOLEAN NOT NULL DEFAULT 0,
		read BOOLEAN NOT NULL DEFAULT 0,
		clicked BOOLEAN NOT NULL DEFAULT 0,
		dismissed BOOLEAN NOT NULL DEFAULT 0
	);`

	if _, err := db.Exec(pushMessageQuery); err != nil {
		return fmt.Errorf("创建推送消息表失败: %v", err)
	}

	// 创建推送订阅表
	pushSubscriptionQuery := `
	CREATE TABLE IF NOT EXISTS push_subscriptions (
		id TEXT PRIMARY KEY,
		user_id TEXT NOT NULL,
		device_type TEXT NOT NULL,
		device_token TEXT NOT NULL,
		endpoint TEXT,
		keys TEXT, -- JSON格式存储密钥
		subscriptions TEXT, -- JSON格式存储订阅列表
		preferences TEXT, -- JSON格式存储偏好设置
		is_active BOOLEAN NOT NULL DEFAULT 1,
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
		updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
		last_activity_at DATETIME DEFAULT CURRENT_TIMESTAMP,
		FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
	);`

	if _, err := db.Exec(pushSubscriptionQuery); err != nil {
		return fmt.Errorf("创建推送订阅表失败: %v", err)
	}

	// 创建推送模板表
	pushTemplateQuery := `
	CREATE TABLE IF NOT EXISTS push_templates (
		id TEXT PRIMARY KEY,
		name TEXT NOT NULL,
		type TEXT NOT NULL CHECK (type IN ('news', 'alert', 'analysis', 'portfolio')),
		category TEXT NOT NULL,
		title TEXT NOT NULL,
		content TEXT NOT NULL,
		summary TEXT,
		image_url TEXT,
		deep_link TEXT,
		variables TEXT, -- JSON格式存储模板变量
		is_active BOOLEAN NOT NULL DEFAULT 1,
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
		updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
	);`

	if _, err := db.Exec(pushTemplateQuery); err != nil {
		return fmt.Errorf("创建推送模板表失败: %v", err)
	}

	// 创建推送规则表
	pushRuleQuery := `
	CREATE TABLE IF NOT EXISTS push_rules (
		id TEXT PRIMARY KEY,
		name TEXT NOT NULL,
		description TEXT,
		trigger_data TEXT NOT NULL, -- JSON格式存储触发器数据
		condition_data TEXT NOT NULL, -- JSON格式存储条件数据
		action_data TEXT NOT NULL, -- JSON格式存储动作数据
		is_active BOOLEAN NOT NULL DEFAULT 1,
		priority INTEGER NOT NULL DEFAULT 1,
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
		updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
	);`

	if _, err := db.Exec(pushRuleQuery); err != nil {
		return fmt.Errorf("创建推送规则表失败: %v", err)
	}

	// 创建推送活动表
	pushCampaignQuery := `
	CREATE TABLE IF NOT EXISTS push_campaigns (
		id TEXT PRIMARY KEY,
		name TEXT NOT NULL,
		description TEXT,
		type TEXT NOT NULL CHECK (type IN ('announcement', 'marketing', 'alert')),
		template_id TEXT,
		target_data TEXT, -- JSON格式存储目标数据
		schedule_data TEXT, -- JSON格式存储调度数据
		status TEXT NOT NULL CHECK (status IN ('draft', 'scheduled', 'running', 'completed', 'paused', 'cancelled')),
		start_time DATETIME,
		end_time DATETIME,
		stats_data TEXT, -- JSON格式存储统计数据
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
		updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
		FOREIGN KEY (template_id) REFERENCES push_templates(id) ON DELETE SET NULL
	);`

	if _, err := db.Exec(pushCampaignQuery); err != nil {
		return fmt.Errorf("创建推送活动表失败: %v", err)
	}

	// 创建推送送达状态表
	pushDeliveryQuery := `
	CREATE TABLE IF NOT EXISTS push_deliveries (
		id TEXT PRIMARY KEY,
		message_id TEXT NOT NULL,
		user_id TEXT,
		device_type TEXT,
		status TEXT NOT NULL CHECK (status IN ('pending', 'sent', 'delivered', 'failed', 'expired')),
		attempts INTEGER NOT NULL DEFAULT 0,
		last_attempt DATETIME,
		error_code TEXT,
		error_msg TEXT,
		delivered_at DATETIME,
		read_at DATETIME,
		clicked_at DATETIME,
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
		FOREIGN KEY (message_id) REFERENCES push_messages(id) ON DELETE CASCADE
	);`

	if _, err := db.Exec(pushDeliveryQuery); err != nil {
		return fmt.Errorf("创建推送送达状态表失败: %v", err)
	}

	// 创建推送分析表
	pushAnalyticsQuery := `
	CREATE TABLE IF NOT EXISTS push_analytics (
		id TEXT PRIMARY KEY,
		message_id TEXT NOT NULL,
		total_sent INTEGER NOT NULL DEFAULT 0,
		total_delivered INTEGER NOT NULL DEFAULT 0,
		total_read INTEGER NOT NULL DEFAULT 0,
		total_clicked INTEGER NOT NULL DEFAULT 0,
		delivery_rate REAL NOT NULL DEFAULT 0.0,
		read_rate REAL NOT NULL DEFAULT 0.0,
		click_rate REAL NOT NULL DEFAULT 0.0,
		avg_delivery_time REAL NOT NULL DEFAULT 0.0,
		avg_read_time REAL NOT NULL DEFAULT 0.0,
		avg_click_time REAL NOT NULL DEFAULT 0.0,
		device_breakdown TEXT, -- JSON格式存储设备统计
		region_breakdown TEXT, -- JSON格式存储地区统计
		time_breakdown TEXT, -- JSON格式存储时间统计
		analytics_date DATE NOT NULL,
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP
	);`

	if _, err := db.Exec(pushAnalyticsQuery); err != nil {
		return fmt.Errorf("创建推送分析表失败: %v", err)
	}

	// 创建推送事件表
	pushEventQuery := `
	CREATE TABLE IF NOT EXISTS push_events (
		id TEXT PRIMARY KEY,
		type TEXT NOT NULL CHECK (type IN ('user_connect', 'user_disconnect', 'message_sent', 'message_delivered', 'message_read', 'message_clicked', 'error')),
		user_id TEXT,
		message_id TEXT,
		event_data TEXT, -- JSON格式存储事件数据
		timestamp DATETIME NOT NULL,
		source TEXT,
		level TEXT CHECK (level IN ('info', 'warning', 'error', 'debug')),
		trace_id TEXT,
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP
	);`

	if _, err := db.Exec(pushEventQuery); err != nil {
		return fmt.Errorf("创建推送事件表失败: %v", err)
	}

	// 创建推送统计表
	pushStatsQuery := `
	CREATE TABLE IF NOT EXISTS push_stats (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		date DATE NOT NULL,
		total_messages INTEGER NOT NULL DEFAULT 0,
		news_messages INTEGER NOT NULL DEFAULT 0,
		alert_messages INTEGER NOT NULL DEFAULT 0,
		analysis_messages INTEGER NOT NULL DEFAULT 0,
		portfolio_messages INTEGER NOT NULL DEFAULT 0,
		success_rate REAL NOT NULL DEFAULT 0.0,
		avg_delivery_time REAL NOT NULL DEFAULT 0.0,
		active_connections INTEGER NOT NULL DEFAULT 0,
		queue_length INTEGER NOT NULL DEFAULT 0,
		error_rate REAL NOT NULL DEFAULT 0.0,
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP
	);`

	if _, err := db.Exec(pushStatsQuery); err != nil {
		return fmt.Errorf("创建推送统计表失败: %v", err)
	}

	// 创建索引
	indexes := []string{
		"CREATE INDEX IF NOT EXISTS idx_push_subscriptions_user_id ON push_subscriptions(user_id)",
		"CREATE INDEX IF NOT EXISTS idx_push_subscriptions_device_token ON push_subscriptions(device_token)",
		"CREATE INDEX IF NOT EXISTS idx_push_subscriptions_active ON push_subscriptions(is_active)",
		"CREATE INDEX IF NOT EXISTS idx_push_messages_created_at ON push_messages(created_at)",
		"CREATE INDEX IF NOT EXISTS idx_push_messages_type ON push_messages(type)",
		"CREATE INDEX IF NOT EXISTS idx_push_messages_priority ON push_messages(priority)",
		"CREATE INDEX IF NOT EXISTS idx_push_deliveries_message_id ON push_deliveries(message_id)",
		"CREATE INDEX IF NOT EXISTS idx_push_deliveries_user_id ON push_deliveries(user_id)",
		"CREATE INDEX IF NOT EXISTS idx_push_deliveries_status ON push_deliveries(status)",
		"CREATE INDEX IF NOT EXISTS idx_push_analytics_message_id ON push_analytics(message_id)",
		"CREATE INDEX IF NOT EXISTS idx_push_analytics_date ON push_analytics(analytics_date)",
		"CREATE INDEX IF NOT EXISTS idx_push_events_user_id ON push_events(user_id)",
		"CREATE INDEX IF NOT EXISTS idx_push_events_timestamp ON push_events(timestamp)",
		"CREATE INDEX IF NOT EXISTS idx_push_events_type ON push_events(type)",
		"CREATE INDEX IF NOT EXISTS idx_push_rules_active ON push_rules(is_active)",
		"CREATE INDEX IF NOT EXISTS idx_push_rules_priority ON push_rules(priority)",
		"CREATE INDEX IF NOT EXISTS idx_push_campaigns_status ON push_campaigns(status)",
		"CREATE INDEX IF NOT EXISTS idx_push_campaigns_start_time ON push_campaigns(start_time)",
	}

	for _, indexQuery := range indexes {
		if _, err := db.Exec(indexQuery); err != nil {
			logger.Printf("创建索引失败: %s, 错误: %v", indexQuery, err)
		}
	}

	// 初始化默认配置
	if err := initDefaultPushConfig(db); err != nil {
		logger.Printf("初始化默认推送配置失败: %v", err)
	}

	logger.Println("新闻推送数据库表创建成功")
	return nil
}

// initDefaultPushConfig 初始化默认推送配置
func initDefaultPushConfig(db *sql.DB) error {
	// 创建默认推送服务
	defaultServices := []struct {
		id       string
		name     string
		servType string
		config   string
	}{
		{"websocket", "WebSocket服务", "websocket", "{}"},
		{"sse", "Server-Sent Events", "sse", "{}"},
		{"apns", "Apple Push Notification Service", "push_notification", "{}"},
		{"fcm", "Firebase Cloud Messaging", "push_notification", "{}"},
	}

	for _, service := range defaultServices {
		_, err := db.Exec(`
			INSERT OR IGNORE INTO push_services (id, name, type, config, enabled)
			VALUES (?, ?, ?, ?, 1)
		`, service.id, service.name, service.servType, service.config)
		if err != nil {
			return err
		}
	}

	// 创建默认推送模板
	defaultTemplates := []struct {
		id         string
		name       string
		templateType string
		title      string
		content    string
	}{
		{"news_breakout", "新闻突发", "news", "📰 重要新闻", "{{.Title}}\n\n{{.Summary}}"},
		{"price_alert", "价格预警", "alert", "💰 价格提醒", "{{.StockName}} 价格达到 {{.TargetPrice}}\n当前: {{.CurrentPrice}}"},
		{"technical_signal", "技术信号", "analysis", "📈 技术分析", "{{.StockName}} {{.SignalName}}\n建议: {{.Recommendation}}"},
		{"daily_summary", "每日总结", "analysis", "📊 每日总结", "今日市场总结已生成"},
	}

	for _, template := range defaultTemplates {
		_, err := db.Exec(`
			INSERT OR IGNORE INTO push_templates (id, name, type, category, title, content, is_active)
			VALUES (?, ?, ?, 'general', ?, ?, 1)
		`, template.id, template.name, template.templateType, template.title, template.content)
		if err != nil {
			return err
		}
	}

	// 创建默认推送规则
	defaultRules := []struct {
		id    string
		name  string
		trigger string
		condition string
		action string
	}{
		{"urgent_news", "紧急新闻推送",
		 `{"type": "news", "min_relevance": 0.8, "categories": ["breaking"]}`,
			`{"field": "relevance", "operator": "greater_than", "value": 0.8}`,
			`{"type": "send_message", "template": "news_breakout", "parameters": {"priority": "high"}}`,
		},
		{"price_movement", "价格变动预警",
		 `{"type": "price", "change_threshold": 0.05}`,
			`{"field": "abs_change_pct", "operator": "greater_than", "value": 0.05}`,
			`{"type": "send_message", "template": "price_alert", "parameters": {"priority": "medium"}}`,
		},
	}

	for _, rule := range defaultRules {
		_, err := db.Exec(`
			INSERT OR IGNORE INTO push_rules (id, name, description, trigger_data, condition_data, action_data, is_active, priority)
			VALUES (?, ?, '自动推送规则', ?, ?, ?, 1, ?)
		`, rule.id, rule.name, rule.trigger, rule.condition, rule.action, 5)
		if err != nil {
			return err
		}
	}

	return nil
}