package models

import (
	"database/sql"
	"time"

	_ "modernc.org/sqlite"
)

// Database 数据库连接管理
type Database struct {
	db *sql.DB
}

// NewDatabase 创建新的数据库连接
func NewDatabase(dbPath string) (*Database, error) {
	db, err := sql.Open("sqlite", dbPath)
	if err != nil {
		return nil, err
	}

	database := &Database{db: db}
	if err := database.createTables(); err != nil {
		return nil, err
	}

	return database, nil
}

// Close 关闭数据库连接
func (d *Database) Close() error {
	return d.db.Close()
}

// createTables 创建数据表
func (d *Database) createTables() error {
	// 创建基础表
	queries := []string{
		`CREATE TABLE IF NOT EXISTS stock_basic (
			code TEXT PRIMARY KEY,
			name TEXT NOT NULL,
			industry TEXT,
			market TEXT,
			listing_date TEXT,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP
		) WITHOUT ROWID`,
		`CREATE TABLE IF NOT EXISTS stock_daily (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			code TEXT NOT NULL,
			date TEXT NOT NULL,
			open REAL NOT NULL,
			high REAL NOT NULL,
			low REAL NOT NULL,
			close REAL NOT NULL,
			volume INTEGER NOT NULL,
			amount REAL NOT NULL,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			UNIQUE(code, date)
		)`,
		`CREATE INDEX IF NOT EXISTS idx_stock_daily_code ON stock_daily(code)`,
		`CREATE INDEX IF NOT EXISTS idx_stock_daily_date ON stock_daily(date)`,
		`CREATE INDEX IF NOT EXISTS idx_stock_daily_code_date ON stock_daily(code, date)`,
		`CREATE TABLE IF NOT EXISTS technical_signals (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			code TEXT NOT NULL,
			date TEXT NOT NULL,
			signal_type TEXT NOT NULL,
			signal_value REAL NOT NULL,
			description TEXT,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			UNIQUE(code, date, signal_type)
		)`,
		`CREATE INDEX IF NOT EXISTS idx_technical_signals_code ON technical_signals(code)`,
		`CREATE INDEX IF NOT EXISTS idx_technical_signals_date ON technical_signals(date)`,
		`CREATE INDEX IF NOT EXISTS idx_technical_signals_type ON technical_signals(signal_type)`,
		`CREATE TABLE IF NOT EXISTS ai_analysis_log (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			code TEXT NOT NULL,
			analysis_type TEXT NOT NULL,
			content TEXT NOT NULL,
			confidence REAL,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP
		)`,
		`CREATE INDEX IF NOT EXISTS idx_ai_analysis_code ON ai_analysis_log(code)`,
		`CREATE INDEX IF NOT EXISTS idx_ai_analysis_type ON ai_analysis_log(analysis_type)`,
	}

	for _, query := range queries {
		if _, err := d.db.Exec(query); err != nil {
			return err
		}
	}

	// 创建新闻相关表
	if err := CreateNewsTables(d.db); err != nil {
		return err
	}

	// 创建扩展新闻相关表
	if err := CreateExtendedNewsTables(d.db); err != nil {
		return err
	}

	// 创建投资组合相关表
	if err := CreatePortfolioTables(d.db); err != nil {
		return err
	}

	// 创建新闻推送相关表
	if err := CreateNewsPushTables(d.db); err != nil {
		return err
	}

	return nil
}

// GetDB 获取数据库连接
func (d *Database) GetDB() *sql.DB {
	return d.db
}

// StockBasic 股票基本信息
type StockBasic struct {
	Code        string    `json:"code"`
	Name        string    `json:"name"`
	Industry    string    `json:"industry"`
	Market      string    `json:"market"`
	ListingDate string    `json:"listing_date"`
	CreatedAt   time.Time `json:"created_at"`
	UpdatedAt   time.Time `json:"updated_at"`
}

// StockDaily 日线行情数据
type StockDaily struct {
	ID        int       `json:"id"`
	Code      string    `json:"code"`
	Date      time.Time `json:"date"`
	Open      float64   `json:"open"`
	High      float64   `json:"high"`
	Low       float64   `json:"low"`
	Close     float64   `json:"close"`
	Volume    int64     `json:"volume"`
	Amount    float64   `json:"amount"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

// TechnicalSignal 技术信号
type TechnicalSignal struct {
	ID          int       `json:"id"`
	Code        string    `json:"code"`
	Date        string    `json:"date"`
	SignalType  string    `json:"signal_type"`
	SignalValue float64   `json:"signal_value"`
	Description string    `json:"description"`
	CreatedAt   time.Time `json:"created_at"`
}

// AIAnalysisLog AI分析记录
type AIAnalysisLog struct {
	ID           int       `json:"id"`
	Code         string    `json:"code"`
	AnalysisType string    `json:"analysis_type"`
	Content      string    `json:"content"`
	Confidence   float64   `json:"confidence"`
	CreatedAt    time.Time `json:"created_at"`
}