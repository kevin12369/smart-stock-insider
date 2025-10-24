package services

import (
	"database/sql"
	"fmt"
	"strings"
	"time"
)

// StockService 股票数据管理服务
type StockService struct {
	dataService *DataService
}

// NewStockService 创建股票服务实例
func NewStockService(dataService *DataService) *StockService {
	return &StockService{
		dataService: dataService,
	}
}

// StockBasicInfo 股票基本信息
type StockBasicInfo struct {
	Code        string    `json:"code"`
	Name        string    `json:"name"`
	Industry    string    `json:"industry"`
	Market      string    `json:"market"`
	ListingDate string    `json:"listing_date"`
	CreatedAt   time.Time `json:"created_at"`
}

// StockDailyData 股票日线数据
type StockDailyData struct {
	ID        int       `json:"id"`
	Code      string    `json:"code"`
	Date      string    `json:"date"`
	Open      float64   `json:"open"`
	High      float64   `json:"high"`
	Low       float64   `json:"low"`
	Close     float64   `json:"close"`
	Volume    int64     `json:"volume"`
	Amount    float64   `json:"amount"`
	Change    float64   `json:"change"`      // 涨跌额
	ChangePct float64   `json:"change_pct"`  // 涨跌幅
	CreatedAt time.Time `json:"created_at"`
}

// AddStockBasic 添加股票基本信息
func (s *StockService) AddStockBasic(stock *StockBasicInfo) error {
	if s.dataService == nil {
		return fmt.Errorf("数据服务未初始化")
	}

	db := s.dataService.GetDB()
	if db == nil {
		return fmt.Errorf("数据库连接不可用")
	}

	query := `INSERT OR REPLACE INTO stock_basic (code, name, industry, market, listing_date, created_at)
	          VALUES (?, ?, ?, ?, ?, ?)`

	_, err := db.Exec(query, stock.Code, stock.Name, stock.Industry,
		stock.Market, stock.ListingDate, time.Now())

	if err != nil {
		AppLogger.Error("添加股票基本信息失败: %v", err)
		return fmt.Errorf("添加股票信息失败: %v", err)
	}

	AppLogger.Info("成功添加股票基本信息: %s - %s", stock.Code, stock.Name)
	return nil
}

// GetStockBasic 获取股票基本信息
func (s *StockService) GetStockBasic(code string) (*StockBasicInfo, error) {
	if s.dataService == nil {
		return nil, fmt.Errorf("数据服务未初始化")
	}

	db := s.dataService.GetDB()
	if db == nil {
		return nil, fmt.Errorf("数据库连接不可用")
	}

	query := `SELECT code, name, industry, market, listing_date, created_at
	          FROM stock_basic WHERE code = ?`

	var stock StockBasicInfo
	var listingDate sql.NullString

	err := db.QueryRow(query, code).Scan(
		&stock.Code, &stock.Name, &stock.Industry,
		&stock.Market, &listingDate, &stock.CreatedAt)

	if err != nil {
		if err == sql.ErrNoRows {
			return nil, fmt.Errorf("股票代码不存在: %s", code)
		}
		return nil, fmt.Errorf("查询股票信息失败: %v", err)
	}

	if listingDate.Valid {
		stock.ListingDate = listingDate.String
	}

	return &stock, nil
}

// GetStockList 获取股票列表
func (s *StockService) GetStockList(limit, offset int, keyword string) ([]StockBasicInfo, int, error) {
	if s.dataService == nil {
		return nil, 0, fmt.Errorf("数据服务未初始化")
	}

	db := s.dataService.GetDB()
	if db == nil {
		return nil, 0, fmt.Errorf("数据库连接不可用")
	}

	// 构建查询条件
	var whereClause string
	var args []interface{}

	if keyword != "" {
		whereClause = "WHERE code LIKE ? OR name LIKE ?"
		keywordPattern := "%" + keyword + "%"
		args = append(args, keywordPattern, keywordPattern)
	}

	// 查询总数
	countQuery := "SELECT COUNT(*) FROM stock_basic " + whereClause
	var total int
	err := db.QueryRow(countQuery, args...).Scan(&total)
	if err != nil {
		return nil, 0, fmt.Errorf("查询股票总数失败: %v", err)
	}

	// 查询数据
	query := `SELECT code, name, industry, market, listing_date, created_at
	          FROM stock_basic ` + whereClause + `
	          ORDER BY code LIMIT ? OFFSET ?`

	queryArgs := append(args, limit, offset)
	rows, err := db.Query(query, queryArgs...)
	if err != nil {
		return nil, 0, fmt.Errorf("查询股票列表失败: %v", err)
	}
	defer rows.Close()

	var stocks []StockBasicInfo
	for rows.Next() {
		var stock StockBasicInfo
		var listingDate sql.NullString

		err := rows.Scan(&stock.Code, &stock.Name, &stock.Industry,
			&stock.Market, &listingDate, &stock.CreatedAt)
		if err != nil {
			AppLogger.Error("扫描股票数据失败: %v", err)
			continue
		}

		if listingDate.Valid {
			stock.ListingDate = listingDate.String
		}

		stocks = append(stocks, stock)
	}

	return stocks, total, nil
}

// AddDailyData 添加日线数据
func (s *StockService) AddDailyData(data *StockDailyData) error {
	if s.dataService == nil {
		return fmt.Errorf("数据服务未初始化")
	}

	db := s.dataService.GetDB()
	if db == nil {
		return fmt.Errorf("数据库连接不可用")
	}

	// 开始事务
	tx, err := db.Begin()
	if err != nil {
		return fmt.Errorf("开始事务失败: %v", err)
	}
	defer tx.Rollback()

	// 获取前一日收盘价用于计算涨跌幅
	var prevClose float64
	prevQuery := `SELECT close FROM stock_daily
	              WHERE code = ? AND date < ?
	              ORDER BY date DESC LIMIT 1`

	err = tx.QueryRow(prevQuery, data.Code, data.Date).Scan(&prevClose)
	if err != nil && err != sql.ErrNoRows {
		AppLogger.Error("查询前一日收盘价失败: %v", err)
	}

	// 计算涨跌额和涨跌幅
	if prevClose > 0 {
		data.Change = data.Close - prevClose
		data.ChangePct = (data.Close - prevClose) / prevClose * 100
	}

	// 插入日线数据
	query := `INSERT OR REPLACE INTO stock_daily
	          (code, date, open, high, low, close, volume, amount, created_at)
	          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`

	_, err = tx.Exec(query, data.Code, data.Date, data.Open, data.High,
		data.Low, data.Close, data.Volume, data.Amount, time.Now())

	if err != nil {
		return fmt.Errorf("插入日线数据失败: %v", err)
	}

	// 更新涨跌额和涨跌幅
	updateQuery := `UPDATE stock_daily
	                SET change = ?, change_pct = ?
	                WHERE code = ? AND date = ?`

	_, err = tx.Exec(updateQuery, data.Change, data.ChangePct, data.Code, data.Date)
	if err != nil {
		return fmt.Errorf("更新涨跌幅失败: %v", err)
	}

	// 提交事务
	if err = tx.Commit(); err != nil {
		return fmt.Errorf("提交事务失败: %v", err)
	}

	AppLogger.Info("成功添加日线数据: %s %s", data.Code, data.Date)
	return nil
}

// GetDailyData 获取日线数据
func (s *StockService) GetDailyData(code string, limit int) ([]StockDailyData, error) {
	if s.dataService == nil {
		return nil, fmt.Errorf("数据服务未初始化")
	}

	db := s.dataService.GetDB()
	if db == nil {
		return nil, fmt.Errorf("数据库连接不可用")
	}

	query := `SELECT id, code, date, open, high, low, close, volume, amount,
	          change, change_pct, created_at
	          FROM stock_daily
	          WHERE code = ?
	          ORDER BY date DESC
	          LIMIT ?`

	rows, err := db.Query(query, code, limit)
	if err != nil {
		return nil, fmt.Errorf("查询日线数据失败: %v", err)
	}
	defer rows.Close()

	var data []StockDailyData
	for rows.Next() {
		var daily StockDailyData
		err := rows.Scan(&daily.ID, &daily.Code, &daily.Date, &daily.Open,
			&daily.High, &daily.Low, &daily.Close, &daily.Volume,
			&daily.Amount, &daily.Change, &daily.ChangePct, &daily.CreatedAt)
		if err != nil {
			AppLogger.Error("扫描日线数据失败: %v", err)
			continue
		}
		data = append(data, daily)
	}

	return data, nil
}

// GetLatestData 获取最新行情数据
func (s *StockService) GetLatestData(codes []string) ([]StockDailyData, error) {
	if s.dataService == nil {
		return nil, fmt.Errorf("数据服务未初始化")
	}

	if len(codes) == 0 {
		return nil, fmt.Errorf("股票代码列表不能为空")
	}

	db := s.dataService.GetDB()
	if db == nil {
		return nil, fmt.Errorf("数据库连接不可用")
	}

	// 构建IN查询
	placeholders := strings.Repeat("?,", len(codes))
	placeholders = placeholders[:len(placeholders)-1] // 移除最后的逗号

	query := fmt.Sprintf(`
		SELECT sd.id, sd.code, sd.date, sd.open, sd.high, sd.low, sd.close,
		       sd.volume, sd.amount, sd.change, sd.change_pct, sd.created_at,
		       sb.name as stock_name
		FROM stock_daily sd
		INNER JOIN stock_basic sb ON sd.code = sb.code
		WHERE sd.code IN (%s)
		AND sd.date = (
			SELECT MAX(date) FROM stock_daily sd2
			WHERE sd2.code = sd.code
		)
		ORDER BY sd.code
	`, placeholders)

	// 转换参数
	args := make([]interface{}, len(codes))
	for i, code := range codes {
		args[i] = code
	}

	rows, err := db.Query(query, args...)
	if err != nil {
		return nil, fmt.Errorf("查询最新数据失败: %v", err)
	}
	defer rows.Close()

	var data []StockDailyData
	for rows.Next() {
		var daily StockDailyData
		var stockName string

		err := rows.Scan(&daily.ID, &daily.Code, &daily.Date, &daily.Open,
			&daily.High, &daily.Low, &daily.Close, &daily.Volume,
			&daily.Amount, &daily.Change, &daily.ChangePct,
			&daily.CreatedAt, &stockName)
		if err != nil {
			AppLogger.Error("扫描最新数据失败: %v", err)
			continue
		}
		data = append(data, daily)
	}

	return data, nil
}

// DeleteStock 删除股票及相关数据
func (s *StockService) DeleteStock(code string) error {
	if s.dataService == nil {
		return fmt.Errorf("数据服务未初始化")
	}

	db := s.dataService.GetDB()
	if db == nil {
		return fmt.Errorf("数据库连接不可用")
	}

	// 开始事务
	tx, err := db.Begin()
	if err != nil {
		return fmt.Errorf("开始事务失败: %v", err)
	}
	defer tx.Rollback()

	// 删除相关数据表中的记录
	tables := []string{"stock_daily", "technical_signals", "ai_analysis_log", "stock_basic"}

	for _, table := range tables {
		query := fmt.Sprintf("DELETE FROM %s WHERE code = ?", table)
		_, err = tx.Exec(query, code)
		if err != nil {
			return fmt.Errorf("删除%s数据失败: %v", table, err)
		}
	}

	// 提交事务
	if err = tx.Commit(); err != nil {
		return fmt.Errorf("提交事务失败: %v", err)
	}

	AppLogger.Info("成功删除股票数据: %s", code)
	return nil
}

// GetStockStats 获取股票统计信息
func (s *StockService) GetStockStats(code string) (map[string]interface{}, error) {
	if s.dataService == nil {
		return nil, fmt.Errorf("数据服务未初始化")
	}

	db := s.dataService.GetDB()
	if db == nil {
		return nil, fmt.Errorf("数据库连接不可用")
	}

	stats := make(map[string]interface{})

	// 获取基本信息
	basic, err := s.GetStockBasic(code)
	if err != nil {
		return nil, err
	}
	stats["basic"] = basic

	// 获取数据统计
	queries := map[string]string{
		"total_records":     "SELECT COUNT(*) FROM stock_daily WHERE code = ?",
		"latest_date":       "SELECT MAX(date) FROM stock_daily WHERE code = ?",
		"earliest_date":     "SELECT MIN(date) FROM stock_daily WHERE code = ?",
		"avg_volume":        "SELECT AVG(volume) FROM stock_daily WHERE code = ?",
		"max_price":         "SELECT MAX(high) FROM stock_daily WHERE code = ?",
		"min_price":         "SELECT MIN(low) FROM stock_daily WHERE code = ?",
		"total_signals":     "SELECT COUNT(*) FROM technical_signals WHERE code = ?",
	}

	for key, query := range queries {
		var result interface{}
		err = db.QueryRow(query, code).Scan(&result)
		if err != nil {
			AppLogger.Debug("查询%s失败: %v", key, err)
			stats[key] = nil
		} else {
			stats[key] = result
		}
	}

	return stats, nil
}