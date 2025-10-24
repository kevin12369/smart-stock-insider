package database

import (
	"database/sql"
	"fmt"
	"time"

	_ "modernc.org/sqlite"
)

// InitDatabase 初始化数据库
func InitDatabase(dbPath string) (*sql.DB, error) {
	db, err := sql.Open("sqlite", dbPath)
	if err != nil {
		return nil, fmt.Errorf("打开数据库失败: %v", err)
	}

	// 启用外键约束和WAL模式
	if err := enableSQLiteSettings(db); err != nil {
		return nil, fmt.Errorf("设置SQLite配置失败: %v", err)
	}

	// 创建表结构
	if err := createTables(db); err != nil {
		return nil, fmt.Errorf("创建数据表失败: %v", err)
	}

	// 插入初始数据
	if err := insertInitialData(db); err != nil {
		return nil, fmt.Errorf("插入初始数据失败: %v", err)
	}

	return db, nil
}

// enableSQLiteSettings 启用SQLite配置
func enableSQLiteSettings(db *sql.DB) error {
	settings := []string{
		"PRAGMA foreign_keys = ON",
		"PRAGMA journal_mode = WAL",
		"PRAGMA synchronous = NORMAL",
		"PRAGMA cache_size = 2000",
		"PRAGMA temp_store = memory",
		"PRAGMA mmap_size = 268435456", // 256MB
	}

	for _, setting := range settings {
		if _, err := db.Exec(setting); err != nil {
			return fmt.Errorf("执行设置失败: %s, %v", setting, err)
		}
	}

	return nil
}

// createTables 创建数据表
func createTables(db *sql.DB) error {
	tables := []string{
		`CREATE TABLE IF NOT EXISTS stock_basic (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			code TEXT NOT NULL UNIQUE,
			name TEXT NOT NULL,
			industry TEXT,
			sector TEXT,
			market TEXT NOT NULL,
			listing_date DATE,
			total_shares BIGINT DEFAULT 0,
			float_shares BIGINT DEFAULT 0,
			market_cap DECIMAL(20,2) DEFAULT 0.00,
			status TEXT DEFAULT 'active',
			is_st INTEGER DEFAULT 0,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
		)`,

		`CREATE TABLE IF NOT EXISTS stock_daily (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			stock_code TEXT NOT NULL,
			trade_date DATE NOT NULL,
			open_price DECIMAL(10,4) NOT NULL,
			high_price DECIMAL(10,4) NOT NULL,
			low_price DECIMAL(10,4) NOT NULL,
			close_price DECIMAL(10,4) NOT NULL,
			volume BIGINT NOT NULL DEFAULT 0,
			amount DECIMAL(20,2) NOT NULL DEFAULT 0.00,
			turnover_rate DECIMAL(8,4) DEFAULT 0.0000,
			pe_ratio DECIMAL(8,4),
			pb_ratio DECIMAL(8,4),
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			UNIQUE(stock_code, trade_date)
		)`,

		`CREATE TABLE IF NOT EXISTS technical_signals (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			stock_code TEXT NOT NULL,
			signal_date DATE NOT NULL,
			signal_type TEXT NOT NULL,
			signal_value DECIMAL(10,6) NOT NULL,
			signal_action TEXT NOT NULL,
			signal_strength DECIMAL(5,4) NOT NULL,
			confidence DECIMAL(5,4) NOT NULL,
			price_at_signal DECIMAL(10,4),
			description TEXT,
			parameters TEXT,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP
		)`,

		`CREATE TABLE IF NOT EXISTS signal_definitions (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			signal_name TEXT NOT NULL UNIQUE,
			signal_type TEXT NOT NULL,
			description TEXT,
			parameters TEXT NOT NULL,
			enabled INTEGER DEFAULT 1,
			priority INTEGER DEFAULT 0,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
		)`,

		`CREATE TABLE IF NOT EXISTS signal_combos (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			combo_name TEXT NOT NULL,
			description TEXT,
			signals TEXT NOT NULL,
			weights TEXT NOT NULL,
			threshold DECIMAL(5,4) NOT NULL DEFAULT 0.5000,
			enabled INTEGER DEFAULT 1,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
		)`,

		`CREATE TABLE IF NOT EXISTS signal_combo_results (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			combo_id INTEGER NOT NULL,
			stock_code TEXT NOT NULL,
			signal_date DATE NOT NULL,
			score DECIMAL(8,4) NOT NULL,
			action TEXT NOT NULL,
			confidence DECIMAL(5,4) NOT NULL,
			details TEXT,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			FOREIGN KEY (combo_id) REFERENCES signal_combos(id)
		)`,

		`CREATE TABLE IF NOT EXISTS ai_analysis_log (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			stock_code TEXT NOT NULL,
			analysis_type TEXT NOT NULL,
			assistant_type TEXT NOT NULL,
			request_data TEXT NOT NULL,
			response_data TEXT NOT NULL,
			processing_time INTEGER NOT NULL,
			success INTEGER NOT NULL DEFAULT 1,
			error_message TEXT,
			confidence DECIMAL(5,4),
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP
		)`,

		`CREATE TABLE IF NOT EXISTS user_portfolio (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			user_id TEXT NOT NULL,
			stock_code TEXT NOT NULL,
			quantity INTEGER NOT NULL DEFAULT 0,
			cost_price DECIMAL(10,4) NOT NULL DEFAULT 0.0000,
			current_price DECIMAL(10,4) NOT NULL DEFAULT 0.0000,
			market_value DECIMAL(20,2) NOT NULL DEFAULT 0.00,
			unrealized_pnl DECIMAL(20,2) NOT NULL DEFAULT 0.00,
			weight DECIMAL(5,4) NOT NULL DEFAULT 0.0000,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			UNIQUE(user_id, stock_code)
		)`,

		`CREATE TABLE IF NOT EXISTS data_quality_log (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			stock_code TEXT,
			check_type TEXT NOT NULL,
			check_date DATE NOT NULL,
			score DECIMAL(5,4) NOT NULL DEFAULT 0.0000,
			issues_count INTEGER NOT NULL DEFAULT 0,
			issues_detail TEXT NOT NULL,
			recommendations TEXT,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP
		)`,

		`CREATE TABLE IF NOT EXISTS system_config (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			config_key TEXT NOT NULL UNIQUE,
			config_value TEXT NOT NULL,
			config_type TEXT NOT NULL,
			description TEXT,
			is_encrypted INTEGER DEFAULT 0,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
		)`,

		`CREATE TABLE IF NOT EXISTS data_sources (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			source_name TEXT NOT NULL UNIQUE,
			source_type TEXT NOT NULL,
			base_url TEXT,
			api_key TEXT,
			config_params TEXT NOT NULL,
			priority INTEGER DEFAULT 0,
			enabled INTEGER DEFAULT 1,
			last_sync_at DATETIME,
			sync_status TEXT DEFAULT 'pending',
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
		)`,

		`CREATE TABLE IF NOT EXISTS task_schedule (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			task_name TEXT NOT NULL UNIQUE,
			task_type TEXT NOT NULL,
			cron_expression TEXT NOT NULL,
			parameters TEXT,
			enabled INTEGER DEFAULT 1,
			last_run_at DATETIME,
			next_run_at DATETIME,
			run_status TEXT DEFAULT 'pending',
			last_result TEXT,
			error_count INTEGER DEFAULT 0,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
		)`,

		`CREATE TABLE IF NOT EXISTS api_access_log (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			endpoint TEXT NOT NULL,
			method TEXT NOT NULL,
			user_id TEXT,
			ip_address TEXT NOT NULL,
			user_agent TEXT,
			request_data TEXT,
			response_status INTEGER NOT NULL,
			response_time INTEGER NOT NULL,
			error_message TEXT,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP
		)`,

		`CREATE TABLE IF NOT EXISTS database_version (
			version TEXT PRIMARY KEY,
			description TEXT,
			applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
		)`,
	}

	// 创建表
	for _, tableSQL := range tables {
		if _, err := db.Exec(tableSQL); err != nil {
			return fmt.Errorf("创建表失败: %v", err)
		}
	}

	// 创建索引
	if err := createIndexes(db); err != nil {
		return fmt.Errorf("创建索引失败: %v", err)
	}

	// 创建触发器
	if err := createTriggers(db); err != nil {
		return fmt.Errorf("创建触发器失败: %v", err)
	}

	// 创建视图
	if err := createViews(db); err != nil {
		return fmt.Errorf("创建视图失败: %v", err)
	}

	return nil
}

// createIndexes 创建索引
func createIndexes(db *sql.DB) error {
	indexes := []string{
		"CREATE INDEX IF NOT EXISTS idx_stock_basic_code ON stock_basic(code)",
		"CREATE INDEX IF NOT EXISTS idx_stock_basic_industry ON stock_basic(industry)",
		"CREATE INDEX IF NOT EXISTS idx_stock_basic_market ON stock_basic(market)",
		"CREATE INDEX IF NOT EXISTS idx_stock_daily_code_date ON stock_daily(stock_code, trade_date)",
		"CREATE INDEX IF NOT EXISTS idx_stock_daily_date ON stock_daily(trade_date)",
		"CREATE INDEX IF NOT EXISTS idx_stock_daily_volume ON stock_daily(volume DESC)",
		"CREATE INDEX IF NOT EXISTS idx_technical_signals_code_date ON technical_signals(stock_code, signal_date)",
		"CREATE INDEX IF NOT EXISTS idx_technical_signals_type ON technical_signals(signal_type)",
		"CREATE INDEX IF NOT EXISTS idx_technical_signals_action ON technical_signals(signal_action)",
		"CREATE INDEX IF NOT EXISTS idx_signal_definitions_type ON signal_definitions(signal_type)",
		"CREATE INDEX IF NOT EXISTS idx_signal_definitions_enabled ON signal_definitions(enabled)",
		"CREATE INDEX IF NOT EXISTS idx_signal_combos_enabled ON signal_combos(enabled)",
		"CREATE INDEX IF NOT EXISTS idx_signal_combo_results_code_date ON signal_combo_results(stock_code, signal_date)",
		"CREATE INDEX IF NOT EXISTS idx_signal_combo_results_score ON signal_combo_results(score DESC)",
		"CREATE INDEX IF NOT EXISTS idx_ai_analysis_log_code_type ON ai_analysis_log(stock_code, analysis_type)",
		"CREATE INDEX IF NOT EXISTS idx_ai_analysis_log_assistant ON ai_analysis_log(assistant_type)",
		"CREATE INDEX IF NOT EXISTS idx_ai_analysis_log_created ON ai_analysis_log(created_at DESC)",
		"CREATE INDEX IF NOT EXISTS idx_user_portfolio_user ON user_portfolio(user_id)",
		"CREATE INDEX IF NOT EXISTS idx_user_portfolio_stock ON user_portfolio(stock_code)",
		"CREATE INDEX IF NOT EXISTS idx_user_portfolio_weight ON user_portfolio(weight DESC)",
		"CREATE INDEX IF NOT EXISTS idx_data_quality_log_type_date ON data_quality_log(check_type, check_date)",
		"CREATE INDEX IF NOT EXISTS idx_data_quality_log_score ON data_quality_log(score)",
		"CREATE INDEX IF NOT EXISTS idx_system_config_key ON system_config(config_key)",
		"CREATE INDEX IF NOT EXISTS idx_system_config_type ON system_config(config_type)",
		"CREATE INDEX IF NOT EXISTS idx_data_sources_enabled ON data_sources(enabled)",
		"CREATE INDEX IF NOT EXISTS idx_data_sources_priority ON data_sources(priority DESC)",
		"CREATE INDEX IF NOT EXISTS idx_task_schedule_enabled ON task_schedule(enabled)",
		"CREATE INDEX IF NOT EXISTS idx_task_schedule_next_run ON task_schedule(next_run_at)",
		"CREATE INDEX IF NOT EXISTS idx_api_access_log_endpoint ON api_access_log(endpoint)",
		"CREATE INDEX IF NOT EXISTS idx_api_access_log_status ON api_access_log(response_status)",
		"CREATE INDEX IF NOT EXISTS idx_api_access_log_created ON api_access_log(created_at DESC)",
	}

	for _, indexSQL := range indexes {
		if _, err := db.Exec(indexSQL); err != nil {
			return fmt.Errorf("创建索引失败: %s, %v", indexSQL, err)
		}
	}

	return nil
}

// createTriggers 创建触发器
func createTriggers(db *sql.DB) error {
	triggers := []string{
		`CREATE TRIGGER IF NOT EXISTS update_stock_basic_updated_at
			AFTER UPDATE ON stock_basic
			BEGIN
				UPDATE stock_basic SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
			END`,

		`CREATE TRIGGER IF NOT EXISTS update_signal_definitions_updated_at
			AFTER UPDATE ON signal_definitions
			BEGIN
				UPDATE signal_definitions SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
			END`,

		`CREATE TRIGGER IF NOT EXISTS update_signal_combos_updated_at
			AFTER UPDATE ON signal_combos
			BEGIN
				UPDATE signal_combos SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
			END`,

		`CREATE TRIGGER IF NOT EXISTS update_system_config_updated_at
			AFTER UPDATE ON system_config
			BEGIN
				UPDATE system_config SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
			END`,

		`CREATE TRIGGER IF NOT EXISTS update_data_sources_updated_at
			AFTER UPDATE ON data_sources
			BEGIN
				UPDATE data_sources SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
			END`,

		`CREATE TRIGGER IF NOT EXISTS update_task_schedule_updated_at
			AFTER UPDATE ON task_schedule
			BEGIN
				UPDATE task_schedule SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
			END`,

		`CREATE TRIGGER IF NOT EXISTS update_user_portfolio_updated_at
			AFTER UPDATE ON user_portfolio
			BEGIN
				UPDATE user_portfolio SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
			END`,
	}

	for _, triggerSQL := range triggers {
		if _, err := db.Exec(triggerSQL); err != nil {
			return fmt.Errorf("创建触发器失败: %s, %v", triggerSQL, err)
		}
	}

	return nil
}

// createViews 创建视图
func createViews(db *sql.DB) error {
	views := []string{
		`CREATE VIEW IF NOT EXISTS v_stock_latest AS
		SELECT
			sb.code,
			sb.name,
			sb.industry,
			sb.market,
			sd.close_price as current_price,
			sd.volume,
			sd.amount,
			sd.trade_date,
			sd.pe_ratio,
			sd.pb_ratio
		FROM stock_basic sb
		LEFT JOIN stock_daily sd ON sb.code = sd.stock_code
		WHERE sd.trade_date = (
			SELECT MAX(trade_date)
			FROM stock_daily sd2
			WHERE sd2.stock_code = sb.code
		)`,

		`CREATE VIEW IF NOT EXISTS v_latest_signals AS
		SELECT
			ts.stock_code,
			ts.signal_type,
			ts.signal_action,
			ts.signal_strength,
			ts.confidence,
			ts.price_at_signal,
			ts.signal_date,
			sb.name as stock_name
		FROM technical_signals ts
		JOIN stock_basic sb ON ts.stock_code = sb.code
		WHERE ts.signal_date = (
			SELECT MAX(signal_date)
			FROM technical_signals ts2
			WHERE ts2.stock_code = ts.stock_code AND ts2.signal_type = ts.signal_type
		)`,
	}

	for _, viewSQL := range views {
		if _, err := db.Exec(viewSQL); err != nil {
			return fmt.Errorf("创建视图失败: %s, %v", viewSQL, err)
		}
	}

	return nil
}

// insertInitialData 插入初始数据
func insertInitialData(db *sql.DB) error {
	// 插入系统配置
	systemConfigs := []struct {
		key, value, configType, description string
	}{
		{"app_name", "智股通", "string", "应用名称"},
		{"app_version", "1.0.0", "string", "应用版本"},
		{"default_risk_tolerance", "0.3", "number", "默认风险容忍度"},
		{"max_analysis_days", "365", "number", "最大分析天数"},
		{"cache_ttl_seconds", "300", "number", "缓存TTL秒数"},
		{"enable_ai_analysis", "true", "boolean", "是否启用AI分析"},
		{"enable_data_quality_check", "true", "boolean", "是否启用数据质量检查"},
	}

	for _, config := range systemConfigs {
		_, err := db.Exec(
			"INSERT OR IGNORE INTO system_config (config_key, config_value, config_type, description) VALUES (?, ?, ?, ?)",
			config.key, config.value, config.configType, config.description,
		)
		if err != nil {
			return fmt.Errorf("插入系统配置失败: %v", err)
		}
	}

	// 插入数据源配置
	dataSources := []struct {
		name, sourceType, baseURL, params string
		priority                              int
	}{
		{"akshare", "api", "https://akshare.akfamily.xyz", `{"timeout": 30, "retry_count": 3}`, 1},
		{"eastmoney", "api", "https://push2.eastmoney.com", `{"timeout": 30, "retry_count": 3}`, 2},
		{"sina", "api", "https://hq.sinajs.cn", `{"timeout": 30, "retry_count": 3}`, 3},
	}

	for _, ds := range dataSources {
		_, err := db.Exec(
			"INSERT OR IGNORE INTO data_sources (source_name, source_type, base_url, config_params, priority, enabled) VALUES (?, ?, ?, ?, ?, 1)",
			ds.name, ds.sourceType, ds.baseURL, ds.params, ds.priority,
		)
		if err != nil {
			return fmt.Errorf("插入数据源配置失败: %v", err)
		}
	}

	// 插入默认技术信号定义
	signalDefinitions := []struct {
		name, signalType, description, params string
		priority                                   int
	}{
		{"MACD金叉", "MACD", "MACD指标金叉信号", `{"fast_period": 12, "slow_period": 26, "signal_period": 9}`, 1},
		{"MACD死叉", "MACD", "MACD指标死叉信号", `{"fast_period": 12, "slow_period": 26, "signal_period": 9}`, 1},
		{"RSI超卖", "RSI", "RSI指标超卖信号", `{"period": 14, "oversold_threshold": 30}`, 2},
		{"RSI超买", "RSI", "RSI指标超买信号", `{"period": 14, "overbought_threshold": 70}`, 2},
		{"KDJ金叉", "KDJ", "KDJ指标金叉信号", `{"period": 9}`, 3},
		{"KDJ死叉", "KDJ", "KDJ指标死叉信号", `{"period": 9}`, 3},
		{"均线金叉", "MA", "短期均线上穿长期均线", `{"short_period": 5, "long_period": 20}`, 4},
		{"均线死叉", "MA", "短期均线下穿长期均线", `{"short_period": 5, "long_period": 20}`, 4},
		{"布林带突破", "BOLL", "价格突破布林带上轨", `{"period": 20, "std_dev": 2}`, 5},
		{"布林带跌破", "BOLL", "价格跌破布林带下轨", `{"period": 20, "std_dev": 2}`, 5},
	}

	for _, sd := range signalDefinitions {
		_, err := db.Exec(
			"INSERT OR IGNORE INTO signal_definitions (signal_name, signal_type, description, parameters, priority) VALUES (?, ?, ?, ?, ?)",
			sd.name, sd.signalType, sd.description, sd.params, sd.priority,
		)
		if err != nil {
			return fmt.Errorf("插入技术信号定义失败: %v", err)
		}
	}

	// 插入默认信号组合
	signalCombos := []struct {
		name, description, signals, weights string
		threshold                               float64
	}{
		{
			"技术面综合",
			"综合多个技术指标的信号组合",
			`["MACD金叉", "RSI超卖", "均线金叉", "布林带突破"]`,
			`{"MACD金叉": 0.3, "RSI超卖": 0.25, "均线金叉": 0.25, "布林带突破": 0.2}`,
			0.6,
		},
		{
			"趋势跟踪",
			"侧重趋势跟踪的信号组合",
			`["均线金叉", "MACD金叉"]`,
			`{"均线金叉": 0.5, "MACD金叉": 0.5}`,
			0.5,
		},
		{
			"超跌反弹",
			"识别超跌反弹机会的信号组合",
			`["RSI超卖", "布林带跌破"]`,
			`{"RSI超卖": 0.6, "布林带跌破": 0.4}`,
			0.7,
		},
	}

	for _, sc := range signalCombos {
		_, err := db.Exec(
			"INSERT OR IGNORE INTO signal_combos (combo_name, description, signals, weights, threshold, enabled) VALUES (?, ?, ?, ?, ?, 1)",
			sc.name, sc.description, sc.signals, sc.weights, sc.threshold,
		)
		if err != nil {
			return fmt.Errorf("插入信号组合失败: %v", err)
		}
	}

	// 插入任务调度配置
	taskSchedules := []struct {
		name, taskType, cronExpr, params string
	}{
		{"数据同步", "sync", "0 */6 * * *", `{"sources": ["akshare", "eastmoney"], "batch_size": 100}`},
		{"技术信号计算", "analysis", "0 */1 * * *", `{"lookback_days": 60, "update_existing": true}`},
		{"数据质量检查", "cleanup", "0 2 * * *", `{"check_types": ["completeness", "accuracy"]}`},
		{"系统备份", "backup", "0 3 * * 0", `{"backup_type": "full", "retention_days": 30}`},
	}

	for _, ts := range taskSchedules {
		_, err := db.Exec(
			"INSERT OR IGNORE INTO task_schedule (task_name, task_type, cron_expression, parameters, enabled) VALUES (?, ?, ?, ?, 1)",
			ts.name, ts.taskType, ts.cronExpr, ts.params,
		)
		if err != nil {
			return fmt.Errorf("插入任务调度配置失败: %v", err)
		}
	}

	// 插入数据库版本信息
	_, err := db.Exec(
		"INSERT OR IGNORE INTO database_version (version, description) VALUES (?, ?)",
		"1.0.0", "智股通初始数据库结构",
	)
	if err != nil {
		return fmt.Errorf("插入数据库版本信息失败: %v", err)
	}

	return nil
}

// CheckDatabaseExists 检查数据库是否存在
func CheckDatabaseExists(dbPath string) bool {
	db, err := sql.Open("sqlite", dbPath)
	if err != nil {
		return false
	}
	defer db.Close()

	// 尝试查询一个关键表是否存在
	var count int
	err = db.QueryRow("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='stock_basic'").Scan(&count)
	return err == nil && count > 0
}

// BackupDatabase 备份数据库
func BackupDatabase(db *sql.DB, backupPath string) error {
	// 使用SQLite的备份API
	_, err := db.Exec(fmt.Sprintf("VACUUM INTO '%s'", backupPath))
	if err != nil {
		return fmt.Errorf("数据库备份失败: %v", err)
	}
	return nil
}

// OptimizeDatabase 优化数据库
func OptimizeDatabase(db *sql.DB) error {
	operations := []string{
		"ANALYZE",
		"VACUUM",
		"REINDEX",
	}

	for _, op := range operations {
		if _, err := db.Exec(op); err != nil {
			return fmt.Errorf("执行数据库优化操作失败: %s, %v", op, err)
		}
	}

	return nil
}

// GetDatabaseStats 获取数据库统计信息
func GetDatabaseStats(db *sql.DB) (map[string]interface{}, error) {
	stats := make(map[string]interface{})

	// 获取表记录数
	tables := []string{"stock_basic", "stock_daily", "technical_signals", "ai_analysis_log"}
	tableCounts := make(map[string]int64)

	for _, table := range tables {
		var count int64
		err := db.QueryRow(fmt.Sprintf("SELECT COUNT(*) FROM %s", table)).Scan(&count)
		if err != nil {
			return nil, fmt.Errorf("获取表 %s 记录数失败: %v", table, err)
		}
		tableCounts[table] = count
	}
	stats["table_counts"] = tableCounts

	// 获取数据库页面大小
	var pageSize int
	err := db.QueryRow("PRAGMA page_size").Scan(&pageSize)
	if err != nil {
		return nil, fmt.Errorf("获取数据库页面大小失败: %v", err)
	}
	stats["page_size"] = pageSize

	// 获取数据库页面数量
	var pageCount int
	err = db.QueryRow("PRAGMA page_count").Scan(&pageCount)
	if err != nil {
		return nil, fmt.Errorf("获取数据库页面数量失败: %v", err)
	}
	stats["page_count"] = pageCount

	// 计算数据库大小（近似）
	stats["estimated_size_bytes"] = int64(pageSize) * int64(pageCount)
	stats["estimated_size_mb"] = float64(stats["estimated_size_bytes"].(int64)) / 1024 / 1024

	return stats, nil
}