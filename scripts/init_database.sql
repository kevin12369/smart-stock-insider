-- 智股通数据库初始化脚本
-- SQLite数据库表结构定义

-- 启用外键约束和WAL模式
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = 2000;

-- =============================================
-- 股票基础信息表
-- =============================================
CREATE TABLE IF NOT EXISTS stock_basic (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,                    -- 股票代码
    name TEXT NOT NULL,                           -- 股票名称
    industry TEXT,                               -- 所属行业
    sector TEXT,                                 -- 所属板块
    market TEXT NOT NULL,                        -- 交易市场 (SH, SZ, BJ)
    listing_date DATE,                           -- 上市日期
    total_shares BIGINT DEFAULT 0,               -- 总股本
    float_shares BIGINT DEFAULT 0,               -- 流通股本
    market_cap DECIMAL(20,2) DEFAULT 0.00,       -- 总市值
    status TEXT DEFAULT 'active',               -- 状态 (active, delisted, suspended)
    is_st INTEGER DEFAULT 0,                    -- 是否ST
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_stock_basic_code ON stock_basic(code);
CREATE INDEX IF NOT EXISTS idx_stock_basic_industry ON stock_basic(industry);
CREATE INDEX IF NOT EXISTS idx_stock_basic_market ON stock_basic(market);

-- =============================================
-- 股票日线行情表
-- =============================================
CREATE TABLE IF NOT EXISTS stock_daily (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_code TEXT NOT NULL,                     -- 股票代码
    trade_date DATE NOT NULL,                     -- 交易日期
    open_price DECIMAL(10,4) NOT NULL,            -- 开盘价
    high_price DECIMAL(10,4) NOT NULL,            -- 最高价
    low_price DECIMAL(10,4) NOT NULL,             -- 最低价
    close_price DECIMAL(10,4) NOT NULL,           -- 收盘价
    volume BIGINT NOT NULL DEFAULT 0,             -- 成交量
    amount DECIMAL(20,2) NOT NULL DEFAULT 0.00,   -- 成交额
    turnover_rate DECIMAL(8,4) DEFAULT 0.0000,    -- 换手率
    pe_ratio DECIMAL(8,4),                       -- 市盈率
    pb_ratio DECIMAL(8,4),                       -- 市净率
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_code, trade_date)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_stock_daily_code_date ON stock_daily(stock_code, trade_date);
CREATE INDEX IF NOT EXISTS idx_stock_daily_date ON stock_daily(trade_date);
CREATE INDEX IF NOT EXISTS idx_stock_daily_volume ON stock_daily(volume DESC);

-- =============================================
-- 技术信号表
-- =============================================
CREATE TABLE IF NOT EXISTS technical_signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_code TEXT NOT NULL,                     -- 股票代码
    signal_date DATE NOT NULL,                    -- 信号日期
    signal_type TEXT NOT NULL,                    -- 信号类型 (MACD, RSI, KDJ, MA, BOLL, etc.)
    signal_value DECIMAL(10,6) NOT NULL,          -- 信号值
    signal_action TEXT NOT NULL,                  -- 信号动作 (buy, sell, hold)
    signal_strength DECIMAL(5,4) NOT NULL,       -- 信号强度 (0-1)
    confidence DECIMAL(5,4) NOT NULL,            -- 置信度 (0-1)
    price_at_signal DECIMAL(10,4),               -- 信号时的价格
    description TEXT,                             -- 信号描述
    parameters TEXT,                              -- 信号参数 (JSON格式)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX(stock_code, signal_date, signal_type)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_technical_signals_code_date ON technical_signals(stock_code, signal_date);
CREATE INDEX IF NOT EXISTS idx_technical_signals_type ON technical_signals(signal_type);
CREATE INDEX IF NOT EXISTS idx_technical_signals_action ON technical_signals(signal_action);

-- =============================================
-- 信号定义配置表
-- =============================================
CREATE TABLE IF NOT EXISTS signal_definitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    signal_name TEXT NOT NULL UNIQUE,            -- 信号名称
    signal_type TEXT NOT NULL,                    -- 信号类型
    description TEXT,                             -- 信号描述
    parameters TEXT NOT NULL,                     -- 信号参数 (JSON格式)
    enabled INTEGER DEFAULT 1,                   -- 是否启用
    priority INTEGER DEFAULT 0,                  -- 优先级
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_signal_definitions_type ON signal_definitions(signal_type);
CREATE INDEX IF NOT EXISTS idx_signal_definitions_enabled ON signal_definitions(enabled);

-- =============================================
-- 信号组合表
-- =============================================
CREATE TABLE IF NOT EXISTS signal_combos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    combo_name TEXT NOT NULL,                     -- 组合名称
    description TEXT,                             -- 组合描述
    signals TEXT NOT NULL,                        -- 信号列表 (JSON格式)
    weights TEXT NOT NULL,                        -- 权重配置 (JSON格式)
    threshold DECIMAL(5,4) NOT NULL DEFAULT 0.5000, -- 阈值
    enabled INTEGER DEFAULT 1,                   -- 是否启用
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_signal_combos_enabled ON signal_combos(enabled);

-- =============================================
-- 信号组合结果表
-- =============================================
CREATE TABLE IF NOT EXISTS signal_combo_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    combo_id INTEGER NOT NULL,                    -- 组合ID
    stock_code TEXT NOT NULL,                     -- 股票代码
    signal_date DATE NOT NULL,                    -- 信号日期
    score DECIMAL(8,4) NOT NULL,                  -- 综合评分
    action TEXT NOT NULL,                         -- 推荐动作
    confidence DECIMAL(5,4) NOT NULL,            -- 置信度
    details TEXT,                                -- 详细信息 (JSON格式)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (combo_id) REFERENCES signal_combos(id),
    INDEX(stock_code, signal_date, combo_id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_signal_combo_results_code_date ON signal_combo_results(stock_code, signal_date);
CREATE INDEX IF NOT EXISTS idx_signal_combo_results_score ON signal_combo_results(score DESC);

-- =============================================
-- AI分析记录表
-- =============================================
CREATE TABLE IF NOT EXISTS ai_analysis_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_code TEXT NOT NULL,                     -- 股票代码
    analysis_type TEXT NOT NULL,                  -- 分析类型 (technical, fundamental, news, risk)
    assistant_type TEXT NOT NULL,                 -- 助手类型
    request_data TEXT NOT NULL,                   -- 请求数据 (JSON格式)
    response_data TEXT NOT NULL,                  -- 响应数据 (JSON格式)
    processing_time INTEGER NOT NULL,             -- 处理时间 (毫秒)
    success INTEGER NOT NULL DEFAULT 1,           -- 是否成功
    error_message TEXT,                           -- 错误信息
    confidence DECIMAL(5,4),                     -- 置信度
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX(stock_code, analysis_type, created_at)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_ai_analysis_log_code_type ON ai_analysis_log(stock_code, analysis_type);
CREATE INDEX IF NOT EXISTS idx_ai_analysis_log_assistant ON ai_analysis_log(assistant_type);
CREATE INDEX IF NOT EXISTS idx_ai_analysis_log_created ON ai_analysis_log(created_at DESC);

-- =============================================
-- 用户投资组合表
-- =============================================
CREATE TABLE IF NOT EXISTS user_portfolio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,                        -- 用户ID
    stock_code TEXT NOT NULL,                     -- 股票代码
    quantity INTEGER NOT NULL DEFAULT 0,          -- 持仓数量
    cost_price DECIMAL(10,4) NOT NULL DEFAULT 0.0000, -- 成本价
    current_price DECIMAL(10,4) NOT NULL DEFAULT 0.0000, -- 当前价
    market_value DECIMAL(20,2) NOT NULL DEFAULT 0.00,   -- 市值
    unrealized_pnl DECIMAL(20,2) NOT NULL DEFAULT 0.00,  -- 浮动盈亏
    weight DECIMAL(5,4) NOT NULL DEFAULT 0.0000,    -- 权重
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, stock_code)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_user_portfolio_user ON user_portfolio(user_id);
CREATE INDEX IF NOT EXISTS idx_user_portfolio_stock ON user_portfolio(stock_code);
CREATE INDEX IF NOT EXISTS idx_user_portfolio_weight ON user_portfolio(weight DESC);

-- =============================================
-- 数据质量监控表
-- =============================================
CREATE TABLE IF NOT EXISTS data_quality_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_code TEXT,                              -- 股票代码 (空表示整体检查)
    check_type TEXT NOT NULL,                     -- 检查类型 (completeness, accuracy, consistency, timeliness)
    check_date DATE NOT NULL,                     -- 检查日期
    score DECIMAL(5,4) NOT NULL DEFAULT 0.0000,    -- 质量评分 (0-1)
    issues_count INTEGER NOT NULL DEFAULT 0,      -- 问题数量
    issues_detail TEXT NOT NULL,                  -- 问题详情 (JSON格式)
    recommendations TEXT,                         -- 改进建议
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX(stock_code, check_type, check_date)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_data_quality_log_type_date ON data_quality_log(check_type, check_date);
CREATE INDEX IF NOT EXISTS idx_data_quality_log_score ON data_quality_log(score);

-- =============================================
-- 系统配置表
-- =============================================
CREATE TABLE IF NOT EXISTS system_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_key TEXT NOT NULL UNIQUE,              -- 配置键
    config_value TEXT NOT NULL,                   -- 配置值
    config_type TEXT NOT NULL,                    -- 配置类型 (string, number, boolean, json)
    description TEXT,                             -- 配置描述
    is_encrypted INTEGER DEFAULT 0,              -- 是否加密
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_system_config_key ON system_config(config_key);
CREATE INDEX IF NOT EXISTS idx_system_config_type ON system_config(config_type);

-- =============================================
-- 数据源配置表
-- =============================================
CREATE TABLE IF NOT EXISTS data_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT NOT NULL UNIQUE,             -- 数据源名称
    source_type TEXT NOT NULL,                    -- 数据源类型 (api, file, database)
    base_url TEXT,                               -- 基础URL
    api_key TEXT,                                -- API密钥 (加密存储)
    config_params TEXT NOT NULL,                  -- 配置参数 (JSON格式)
    priority INTEGER DEFAULT 0,                  -- 优先级
    enabled INTEGER DEFAULT 1,                   -- 是否启用
    last_sync_at DATETIME,                       -- 最后同步时间
    sync_status TEXT DEFAULT 'pending',           -- 同步状态
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_data_sources_enabled ON data_sources(enabled);
CREATE INDEX IF NOT EXISTS idx_data_sources_priority ON data_sources(priority DESC);

-- =============================================
-- 任务调度表
-- =============================================
CREATE TABLE IF NOT EXISTS task_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_name TEXT NOT NULL UNIQUE,               -- 任务名称
    task_type TEXT NOT NULL,                      -- 任务类型 (sync, analysis, backup, cleanup)
    cron_expression TEXT NOT NULL,                -- Cron表达式
    parameters TEXT,                              -- 任务参数 (JSON格式)
    enabled INTEGER DEFAULT 1,                   -- 是否启用
    last_run_at DATETIME,                        -- 最后运行时间
    next_run_at DATETIME,                        -- 下次运行时间
    run_status TEXT DEFAULT 'pending',            -- 运行状态
    last_result TEXT,                             -- 最后运行结果
    error_count INTEGER DEFAULT 0,               -- 错误次数
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_task_schedule_enabled ON task_schedule(enabled);
CREATE INDEX IF NOT EXISTS idx_task_schedule_next_run ON task_schedule(next_run_at);

-- =============================================
-- API访问日志表
-- =============================================
CREATE TABLE IF NOT EXISTS api_access_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    endpoint TEXT NOT NULL,                       -- API端点
    method TEXT NOT NULL,                         -- HTTP方法
    user_id TEXT,                                -- 用户ID
    ip_address TEXT NOT NULL,                     -- IP地址
    user_agent TEXT,                              -- User-Agent
    request_data TEXT,                            -- 请求数据
    response_status INTEGER NOT NULL,             -- 响应状态码
    response_time INTEGER NOT NULL,               -- 响应时间 (毫秒)
    error_message TEXT,                           -- 错误信息
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX(endpoint, method, created_at),
    INDEX(user_id, created_at),
    INDEX(response_status, created_at)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_api_access_log_endpoint ON api_access_log(endpoint);
CREATE INDEX IF NOT EXISTS idx_api_access_log_status ON api_access_log(response_status);
CREATE INDEX IF NOT EXISTS idx_api_access_log_created ON api_access_log(created_at DESC);

-- =============================================
-- 插入初始数据
-- =============================================

-- 插入系统配置
INSERT OR IGNORE INTO system_config (config_key, config_value, config_type, description) VALUES
('app_name', '智股通', 'string', '应用名称'),
('app_version', '1.0.0', 'string', '应用版本'),
('default_risk_tolerance', '0.3', 'number', '默认风险容忍度'),
('max_analysis_days', '365', 'number', '最大分析天数'),
('cache_ttl_seconds', '300', 'number', '缓存TTL秒数'),
('enable_ai_analysis', 'true', 'boolean', '是否启用AI分析'),
('enable_data_quality_check', 'true', 'boolean', '是否启用数据质量检查');

-- 插入数据源配置
INSERT OR IGNORE INTO data_sources (source_name, source_type, base_url, config_params, priority, enabled) VALUES
('akshare', 'api', 'https://akshare.akfamily.xyz', '{"timeout": 30, "retry_count": 3}', 1, 1),
('eastmoney', 'api', 'https://push2.eastmoney.com', '{"timeout": 30, "retry_count": 3}', 2, 1),
('sina', 'api', 'https://hq.sinajs.cn', '{"timeout": 30, "retry_count": 3}', 3, 1);

-- 插入默认技术信号定义
INSERT OR IGNORE INTO signal_definitions (signal_name, signal_type, description, parameters, priority) VALUES
('MACD金叉', 'MACD', 'MACD指标金叉信号', '{"fast_period": 12, "slow_period": 26, "signal_period": 9}', 1),
('MACD死叉', 'MACD', 'MACD指标死叉信号', '{"fast_period": 12, "slow_period": 26, "signal_period": 9}', 1),
('RSI超卖', 'RSI', 'RSI指标超卖信号', '{"period": 14, "oversold_threshold": 30}', 2),
('RSI超买', 'RSI', 'RSI指标超买信号', '{"period": 14, "overbought_threshold": 70}', 2),
('KDJ金叉', 'KDJ', 'KDJ指标金叉信号', '{"period": 9}', 3),
('KDJ死叉', 'KDJ', 'KDJ指标死叉信号', '{"period": 9}', 3),
('均线金叉', 'MA', '短期均线上穿长期均线', '{"short_period": 5, "long_period": 20}', 4),
('均线死叉', 'MA', '短期均线下穿长期均线', '{"short_period": 5, "long_period": 20}', 4),
('布林带突破', 'BOLL', '价格突破布林带上轨', '{"period": 20, "std_dev": 2}', 5),
('布林带跌破', 'BOLL', '价格跌破布林带下轨', '{"period": 20, "std_dev": 2}', 5);

-- 插入默认信号组合
INSERT OR IGNORE INTO signal_combos (combo_name, description, signals, weights, threshold, enabled) VALUES
('技术面综合', '综合多个技术指标的信号组合',
 '["MACD金叉", "RSI超卖", "均线金叉", "布林带突破"]',
 '{"MACD金叉": 0.3, "RSI超卖": 0.25, "均线金叉": 0.25, "布林带突破": 0.2}',
 0.6, 1),
('趋势跟踪', '侧重趋势跟踪的信号组合',
 '["均线金叉", "MACD金叉"]',
 '{"均线金叉": 0.5, "MACD金叉": 0.5}',
 0.5, 1),
('超跌反弹', '识别超跌反弹机会的信号组合',
 '["RSI超卖", "布林带跌破"]',
 '{"RSI超卖": 0.6, "布林带跌破": 0.4}',
 0.7, 1);

-- 插入任务调度配置
INSERT OR IGNORE INTO task_schedule (task_name, task_type, cron_expression, parameters, enabled) VALUES
('数据同步', 'sync', '0 */6 * * *', '{"sources": ["akshare", "eastmoney"], "batch_size": 100}', 1),
('技术信号计算', 'analysis', '0 */1 * * *', '{"lookback_days": 60, "update_existing": true}', 1),
('数据质量检查', 'cleanup', '0 2 * * *', '{"check_types": ["completeness", "accuracy"]}', 1),
('系统备份', 'backup', '0 3 * * 0', '{"backup_type": "full", "retention_days": 30}', 1);

-- =============================================
-- 创建触发器和视图
-- =============================================

-- 创建更新时间的触发器
CREATE TRIGGER IF NOT EXISTS update_stock_basic_updated_at
    AFTER UPDATE ON stock_basic
    BEGIN
        UPDATE stock_basic SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_signal_definitions_updated_at
    AFTER UPDATE ON signal_definitions
    BEGIN
        UPDATE signal_definitions SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_signal_combos_updated_at
    AFTER UPDATE ON signal_combos
    BEGIN
        UPDATE signal_combos SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_system_config_updated_at
    AFTER UPDATE ON system_config
    BEGIN
        UPDATE system_config SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_data_sources_updated_at
    AFTER UPDATE ON data_sources
    BEGIN
        UPDATE data_sources SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_task_schedule_updated_at
    AFTER UPDATE ON task_schedule
    BEGIN
        UPDATE task_schedule SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_user_portfolio_updated_at
    AFTER UPDATE ON user_portfolio
    BEGIN
        UPDATE user_portfolio SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

-- 创建视图
CREATE VIEW IF NOT EXISTS v_stock_latest AS
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
    sd.pb_ratio,
    (sd.close_price - LAG(sd.close_price) OVER (PARTITION BY sb.code ORDER BY sd.trade_date)) / LAG(sd.close_price) OVER (PARTITION BY sb.code ORDER BY sd.trade_date) * 100 as price_change_pct
FROM stock_basic sb
LEFT JOIN stock_daily sd ON sb.code = sd.code
WHERE sd.trade_date = (
    SELECT MAX(trade_date)
    FROM stock_daily sd2
    WHERE sd2.stock_code = sb.code
);

-- 创建最新技术信号视图
CREATE VIEW IF NOT EXISTS v_latest_signals AS
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
);

-- =============================================
-- 数据库版本信息
-- =============================================

CREATE TABLE IF NOT EXISTS database_version (
    version TEXT PRIMARY KEY,
    description TEXT,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO database_version (version, description) VALUES
('1.0.0', '智股通初始数据库结构');

-- 完成初始化
SELECT 'Database initialization completed successfully.' as message;