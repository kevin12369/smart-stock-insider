package models

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"time"
)

// CreatePortfolioTables 创建投资组合相关数据库表
func CreatePortfolioTables(db *sql.DB) error {
	logger := log.Default()

	// 创建投资组合表
	portfolioQuery := `
	CREATE TABLE IF NOT EXISTS portfolios (
		id TEXT PRIMARY KEY,
		user_id TEXT NOT NULL,
		name TEXT NOT NULL,
		description TEXT,
		total_value REAL NOT NULL DEFAULT 0,
		cash_amount REAL NOT NULL DEFAULT 0,
		currency TEXT NOT NULL DEFAULT 'CNY',
		risk_level TEXT NOT NULL DEFAULT 'moderate',
		benchmark_code TEXT,
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
		updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
	);`

	if _, err := db.Exec(portfolioQuery); err != nil {
		return fmt.Errorf("创建投资组合表失败: %v", err)
	}

	// 创建持仓表
	positionQuery := `
	CREATE TABLE IF NOT EXISTS positions (
		id TEXT PRIMARY KEY,
		portfolio_id TEXT NOT NULL,
		stock_code TEXT NOT NULL,
		stock_name TEXT NOT NULL,
		quantity REAL NOT NULL,
		avg_cost REAL NOT NULL,
		current_price REAL NOT NULL,
		market_value REAL NOT NULL,
		unrealized_pnl REAL NOT NULL DEFAULT 0,
		unrealized_pct REAL NOT NULL DEFAULT 0,
		realized_pnl REAL NOT NULL DEFAULT 0,
		holding_days INTEGER NOT NULL DEFAULT 0,
		weight REAL NOT NULL DEFAULT 0,
		risk_contribution REAL NOT NULL DEFAULT 0,
		sector TEXT,
		industry TEXT,
		market_cap TEXT,
		pe REAL,
		pb REAL,
		dividend_yield REAL,
		buy_date TEXT,
		last_transaction TEXT,
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
		updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
		FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE,
		FOREIGN KEY (stock_code) REFERENCES stock_basic(code) ON UPDATE CASCADE
	);`

	if _, err := db.Exec(positionQuery); err != nil {
		return fmt.Errorf("创建持仓表失败: %v", err)
	}

	// 创建交易记录表
	transactionQuery := `
	CREATE TABLE IF NOT EXISTS transactions (
		id TEXT PRIMARY KEY,
		portfolio_id TEXT NOT NULL,
		position_id TEXT,
		stock_code TEXT NOT NULL,
		stock_name TEXT NOT NULL,
		transaction_type TEXT NOT NULL CHECK (transaction_type IN ('buy', 'sell', 'dividend', 'split')),
		quantity REAL NOT NULL,
		price REAL NOT NULL,
		amount REAL NOT NULL,
		fee REAL NOT NULL DEFAULT 0,
		tax REAL NOT NULL DEFAULT 0,
		notes TEXT,
		executed_at DATETIME NOT NULL,
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
		FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE,
		FOREIGN KEY (position_id) REFERENCES positions(id) ON DELETE SET NULL,
		FOREIGN KEY (stock_code) REFERENCES stock_basic(code) ON UPDATE CASCADE
	);`

	if _, err := db.Exec(transactionQuery); err != nil {
		return fmt.Errorf("创建交易记录表失败: %v", err)
	}

	// 创建投资组合分析缓存表
	analysisQuery := `
	CREATE TABLE IF NOT EXISTS portfolio_analysis_cache (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		portfolio_id TEXT NOT NULL,
		analysis_type TEXT NOT NULL,
		analysis_data TEXT NOT NULL, -- JSON格式存储分析结果
		benchmark_code TEXT,
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
		expires_at DATETIME NOT NULL,
		FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE,
		UNIQUE(portfolio_id, analysis_type)
	);`

	if _, err := db.Exec(analysisQuery); err != nil {
		return fmt.Errorf("创建分析缓存表失败: %v", err)
	}

	// 创建投资组合预警表
	alertQuery := `
	CREATE TABLE IF NOT EXISTS portfolio_alerts (
		id TEXT PRIMARY KEY,
		portfolio_id TEXT NOT NULL,
		user_id TEXT NOT NULL,
		alert_type TEXT NOT NULL CHECK (alert_type IN ('risk', 'performance', 'allocation', 'news')),
		severity TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
		title TEXT NOT NULL,
		message TEXT NOT NULL,
		trigger_value REAL,
		threshold_value REAL,
		condition TEXT NOT NULL CHECK (condition IN ('above', 'below', 'percentage_change')),
		is_active BOOLEAN NOT NULL DEFAULT 1,
		is_read BOOLEAN NOT NULL DEFAULT 0,
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
		read_at DATETIME,
		expires_at DATETIME,
		FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE
	);`

	if _, err := db.Exec(alertQuery); err != nil {
		return fmt.Errorf("创建预警表失败: %v", err)
	}

	// 创建投资组合配置表
	configQuery := `
	CREATE TABLE IF NOT EXISTS portfolio_config (
		id INTEGER PRIMARY KEY CHECK (id = 1),
		auto_rebalance BOOLEAN NOT NULL DEFAULT 0,
		rebalance_frequency TEXT NOT NULL DEFAULT 'monthly',
		rebalance_threshold REAL NOT NULL DEFAULT 0.05,
		risk_tolerance TEXT NOT NULL DEFAULT 'moderate',
		max_position_weight REAL NOT NULL DEFAULT 0.20,
		min_position_weight REAL NOT NULL DEFAULT 0.01,
		currency_hedging BOOLEAN NOT NULL DEFAULT 0,
		updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
	);`

	if _, err := db.Exec(configQuery); err != nil {
		return fmt.Errorf("创建投资组合配置表失败: %v", err)
	}

	// 创建投资组合快照表
	snapshotQuery := `
	CREATE TABLE IF NOT EXISTS portfolio_snapshots (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		portfolio_id TEXT NOT NULL,
		snapshot_date DATE NOT NULL,
		total_value REAL NOT NULL,
		cash_amount REAL NOT NULL,
		investment_value REAL NOT NULL,
		daily_return REAL,
		daily_return_pct REAL,
		positions_count INTEGER NOT NULL,
		top_holdings TEXT, -- JSON格式存储前5大持仓
		sector_allocation TEXT, -- JSON格式存储行业配置
		risk_level TEXT,
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
		FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE,
		UNIQUE(portfolio_id, snapshot_date)
	);`

	if _, err := db.Exec(snapshotQuery); err != nil {
		return fmt.Errorf("创建快照表失败: %v", err)
	}

	// 创建索引
	indexes := []string{
		"CREATE INDEX IF NOT EXISTS idx_portfolios_user_id ON portfolios(user_id)",
		"CREATE INDEX IF NOT EXISTS idx_portfolios_created_at ON portfolios(created_at)",
		"CREATE INDEX IF NOT EXISTS idx_positions_portfolio_id ON positions(portfolio_id)",
		"CREATE INDEX IF NOT EXISTS idx_positions_stock_code ON positions(stock_code)",
		"CREATE INDEX IF NOT EXISTS idx_positions_market_value ON positions(market_value)",
		"CREATE INDEX IF NOT EXISTS idx_transactions_portfolio_id ON transactions(portfolio_id)",
		"CREATE INDEX IF NOT EXISTS idx_transactions_executed_at ON transactions(executed_at)",
		"CREATE INDEX IF NOT EXISTS idx_portfolio_analysis_portfolio_id ON portfolio_analysis_cache(portfolio_id)",
		"CREATE INDEX IF NOT EXISTS idx_portfolio_analysis_type ON portfolio_analysis_cache(analysis_type)",
		"CREATE INDEX IF NOT EXISTS idx_portfolio_analysis_expires ON portfolio_analysis_cache(expires_at)",
		"CREATE INDEX IF NOT EXISTS idx_portfolio_alerts_portfolio_id ON portfolio_alerts(portfolio_id)",
		"CREATE INDEX IF NOT EXISTS idx_portfolio_alerts_active ON portfolio_alerts(is_active)",
		"CREATE INDEX IF NOT EXISTS idx_portfolio_alerts_created_at ON portfolio_alerts(created_at)",
		"CREATE INDEX IF NOT EXISTS idx_portfolio_snapshots_portfolio_id ON portfolio_snapshots(portfolio_id)",
		"CREATE INDEX IF NOT EXISTS idx_portfolio_snapshots_date ON portfolio_snapshots(snapshot_date)",
	}

	for _, indexQuery := range indexes {
		if _, err := db.Exec(indexQuery); err != nil {
			logger.Printf("创建索引失败: %s, 错误: %v", indexQuery, err)
		}
	}

	// 初始化默认配置
	if err := initDefaultPortfolioConfig(db); err != nil {
		logger.Printf("初始化默认投资组合配置失败: %v", err)
	}

	logger.Println("投资组合数据库表创建成功")
	return nil
}

// initDefaultPortfolioConfig 初始化默认投资组合配置
func initDefaultPortfolioConfig(db *sql.DB) error {
	// 检查是否已有配置
	var count int
	err := db.QueryRow("SELECT COUNT(*) FROM portfolio_config").Scan(&count)
	if err != nil {
		return err
	}

	if count > 0 {
		return nil // 配置已存在
	}

	// 插入默认配置
	_, err = db.Exec(`
		INSERT INTO portfolio_config (id, auto_rebalance, rebalance_frequency, rebalance_threshold,
								risk_tolerance, max_position_weight, min_position_weight, currency_hedging)
		VALUES (1, 0, 'monthly', 0.05, 'moderate', 0.20, 0.01, 0)
	`)

	return err
}

// PortfolioRepository 投资组合数据访问层
type PortfolioRepository struct {
	db     *sql.DB
	logger *log.Logger
}

// NewPortfolioRepository 创建投资组合数据访问层
func NewPortfolioRepository(db *sql.DB) *PortfolioRepository {
	return &PortfolioRepository{
		db:     db,
		logger: log.Default(),
	}
}

// SavePortfolio 保存投资组合
func (repo *PortfolioRepository) SavePortfolio(portfolio *Portfolio) error {
	query := `
		INSERT OR REPLACE INTO portfolios
		(id, user_id, name, description, total_value, cash_amount, currency, risk_level, updated_at)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
	`

	_, err := repo.db.Exec(query, portfolio.ID, portfolio.UserID, portfolio.Name,
		portfolio.Description, portfolio.TotalValue, portfolio.CashAmount,
		portfolio.Currency, portfolio.RiskLevel)

	return err
}

// GetPortfolio 获取投资组合
func (repo *PortfolioRepository) GetPortfolio(portfolioID string) (*Portfolio, error) {
	query := `
		SELECT id, user_id, name, description, total_value, cash_amount, currency,
			   risk_level, created_at, updated_at
		FROM portfolios
		WHERE id = ?
	`

	portfolio := &Portfolio{}
	err := repo.db.QueryRow(query, portfolioID).Scan(
		&portfolio.ID, &portfolio.UserID, &portfolio.Name, &portfolio.Description,
		&portfolio.TotalValue, &portfolio.CashAmount, &portfolio.Currency,
		&portfolio.RiskLevel,
		&portfolio.CreatedAt, &portfolio.UpdatedAt,
	)

	if err != nil {
		return nil, err
	}

	return portfolio, nil
}

// GetUserPortfolios 获取用户投资组合列表
func (repo *PortfolioRepository) GetUserPortfolios(userID string) ([]*Portfolio, error) {
	query := `
		SELECT id, user_id, name, description, total_value, cash_amount, currency,
			   risk_level, created_at, updated_at
		FROM portfolios
		WHERE user_id = ?
		ORDER BY created_at DESC
	`

	rows, err := repo.db.Query(query, userID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var portfolios []*Portfolio
	for rows.Next() {
		portfolio := &Portfolio{}
		err := rows.Scan(
			&portfolio.ID, &portfolio.UserID, &portfolio.Name, &portfolio.Description,
			&portfolio.TotalValue, &portfolio.CashAmount, &portfolio.Currency,
			&portfolio.RiskLevel,
			&portfolio.CreatedAt, &portfolio.UpdatedAt,
		)
		if err != nil {
			continue
		}
		portfolios = append(portfolios, portfolio)
	}

	return portfolios, nil
}

// SavePosition 保存持仓
func (repo *PortfolioRepository) SavePosition(position *Position) error {
	query := `
		INSERT OR REPLACE INTO positions
		(id, portfolio_id, stock_code, stock_name, quantity, avg_cost, current_price,
		 market_value, unrealized_pnl, unrealized_pct, realized_pnl, holding_days,
		 weight, risk_contribution, sector, industry, market_cap, pe, pb, dividend_yield,
		 buy_date, updated_at)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
	`

	_, err := repo.db.Exec(query, position.ID, position.PortfolioID, position.StockCode, position.StockName,
		position.Quantity, position.AvgCost, position.CurrentPrice, position.MarketValue,
		position.UnrealizedPnL, position.UnrealizedPct, position.RealizedPnL, position.HoldingDays,
		position.Weight, position.RiskContribution, position.Sector, position.Industry, position.MarketCap,
		position.PE, position.PB, position.DividendYield, position.BuyDate)

	return err
}

// GetPositions 获取投资组合持仓
func (repo *PortfolioRepository) GetPositions(portfolioID string) ([]*Position, error) {
	query := `
		SELECT id, portfolio_id, stock_code, stock_name, quantity, avg_cost, current_price,
			   market_value, unrealized_pnl, unrealized_pct, realized_pnl, holding_days,
			   weight, risk_contribution, sector, industry, market_cap, pe, pb, dividend_yield,
			   buy_date, created_at, updated_at
		FROM positions
		WHERE portfolio_id = ?
		ORDER BY market_value DESC
	`

	rows, err := repo.db.Query(query, portfolioID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var positions []*Position
	for rows.Next() {
		position := &Position{}
		err := rows.Scan(
			&position.ID, &position.PortfolioID, &position.StockCode, &position.StockName,
			&position.Quantity, &position.AvgCost, &position.CurrentPrice, &position.MarketValue,
			&position.UnrealizedPnL, &position.UnrealizedPct, &position.RealizedPnL, &position.HoldingDays,
			&position.Weight, &position.RiskContribution, &position.Sector, &position.Industry, &position.MarketCap,
			&position.PE, &position.PB, &position.DividendYield, &position.BuyDate,
			&position.CreatedAt, &position.UpdatedAt,
		)
		if err != nil {
			continue
		}
		positions = append(positions, position)
	}

	return positions, nil
}

// SaveTransaction 保存交易记录
func (repo *PortfolioRepository) SaveTransaction(transaction *Transaction) error {
	query := `
		INSERT OR REPLACE INTO transactions
		(id, portfolio_id, position_id, stock_code, stock_name, transaction_type,
		 quantity, price, amount, fee, tax, notes, executed_at, created_at)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
	`

	_, err := repo.db.Exec(query, transaction.ID, transaction.PortfolioID, transaction.PositionID,
		transaction.StockCode, transaction.StockName, transaction.TransactionType,
		transaction.Quantity, transaction.Price, transaction.Amount, transaction.Fee, transaction.Tax,
		transaction.Notes, transaction.ExecutedAt)

	return err
}

// GetTransactions 获取交易记录
func (repo *PortfolioRepository) GetTransactions(portfolioID string, limit int) ([]*Transaction, error) {
	query := `
		SELECT id, portfolio_id, position_id, stock_code, stock_name, transaction_type,
			   quantity, price, amount, fee, tax, notes, executed_at, created_at
		FROM transactions
		WHERE portfolio_id = ?
		ORDER BY executed_at DESC
	`

	if limit > 0 {
		query += fmt.Sprintf(" LIMIT %d", limit)
	}

	rows, err := repo.db.Query(query, portfolioID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var transactions []*Transaction
	for rows.Next() {
		transaction := &Transaction{}
		err := rows.Scan(
			&transaction.ID, &transaction.PortfolioID, &transaction.PositionID,
			&transaction.StockCode, &transaction.StockName, &transaction.TransactionType,
			&transaction.Quantity, &transaction.Price, &transaction.Amount, &transaction.Fee, &transaction.Tax,
			&transaction.Notes, &transaction.ExecutedAt, &transaction.CreatedAt,
		)
		if err != nil {
			continue
		}
		transactions = append(transactions, transaction)
	}

	return transactions, nil
}

// SavePortfolioSnapshot 保存投资组合快照
func (repo *PortfolioRepository) SavePortfolioSnapshot(snapshot *PortfolioSnapshot) error {
	query := `
		INSERT OR REPLACE INTO portfolio_snapshots
		(portfolio_id, snapshot_date, total_value, cash_amount, investment_value,
		 daily_return, daily_return_pct, positions_count, top_holdings,
		 sector_allocation, risk_level, created_at)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
	`

	topHoldingsJSON, _ := json.Marshal(snapshot.TopHoldings)
	sectorAllocationJSON, _ := json.Marshal(snapshot.SectorAllocation)

	_, err := repo.db.Exec(query, snapshot.PortfolioID, snapshot.SnapshotDate, snapshot.TotalValue,
		snapshot.CashAmount, snapshot.InvestmentValue, snapshot.DailyReturn, snapshot.DailyReturnPct,
		snapshot.PositionsCount, string(topHoldingsJSON), string(sectorAllocationJSON),
		snapshot.RiskLevel)

	return err
}

// PortfolioSnapshot 投资组合快照
type PortfolioSnapshot struct {
	ID               int                    `json:"id"`
	PortfolioID      string                 `json:"portfolio_id"`
	SnapshotDate     time.Time              `json:"snapshot_date"`
	TotalValue       float64                `json:"total_value"`
	CashAmount       float64                `json:"cash_amount"`
	InvestmentValue  float64                `json:"investment_value"`
	DailyReturn      float64                `json:"daily_return"`
	DailyReturnPct   float64                `json:"daily_return_pct"`
	PositionsCount   int                    `json:"positions_count"`
	TopHoldings      []string               `json:"top_holdings"`
	SectorAllocation  map[string]float64    `json:"sector_allocation"`
	RiskLevel        string                 `json:"risk_level"`
	CreatedAt        time.Time              `json:"created_at"`
}