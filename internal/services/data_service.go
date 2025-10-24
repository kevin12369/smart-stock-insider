package services

import (
	"database/sql"
	"fmt"
	"os"
	"path/filepath"
	"sync"
	"time"

	"smart-stock-insider/internal/models"
	_ "modernc.org/sqlite"
)

// DataService 数据服务
type DataService struct {
	db     *models.Database
	dbPath string
	mutex  sync.RWMutex
}

// NewDataService 创建数据服务实例
func NewDataService(dbPath string) (*DataService, error) {
	// 确保数据库目录存在
	dir := filepath.Dir(dbPath)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return nil, fmt.Errorf("创建数据库目录失败: %v", err)
	}

	// 连接数据库
	database, err := models.NewDatabase(dbPath)
	if err != nil {
		return nil, fmt.Errorf("连接数据库失败: %v", err)
	}

	service := &DataService{
		db:     database,
		dbPath: dbPath,
	}

	AppLogger.Info("数据服务初始化成功: %s", dbPath)
	return service, nil
}

// Close 关闭数据库连接
func (s *DataService) Close() error {
	s.mutex.Lock()
	defer s.mutex.Unlock()

	if s.db != nil {
		err := s.db.Close()
		s.db = nil
		if err != nil {
			AppLogger.Error("关闭数据库连接失败: %v", err)
			return err
		}
		AppLogger.Info("数据库连接已关闭")
	}
	return nil
}

// GetDB 获取数据库连接
func (s *DataService) GetDB() *sql.DB {
	s.mutex.RLock()
	defer s.mutex.RUnlock()

	if s.db != nil {
		return s.db.GetDB()
	}
	return nil
}

// IsConnected 检查数据库连接状态
func (s *DataService) IsConnected() bool {
	s.mutex.RLock()
	defer s.mutex.RUnlock()

	if s.db != nil && s.db.GetDB() != nil {
		err := s.db.GetDB().Ping()
		return err == nil
	}
	return false
}

// GetDatabaseInfo 获取数据库信息
func (s *DataService) GetDatabaseInfo() map[string]interface{} {
	s.mutex.RLock()
	defer s.mutex.RUnlock()

	info := make(map[string]interface{})
	info["path"] = s.dbPath
	info["connected"] = s.IsConnected()
	info["created_at"] = time.Now().Format("2006-01-02 15:04:05")

	if s.db != nil && s.db.GetDB() != nil {
		// 获取数据库统计信息
		stats := s.getDatabaseStats()
		info["stats"] = stats
	}

	return info
}

// getDatabaseStats 获取数据库统计信息
func (s *DataService) getDatabaseStats() map[string]int {
	stats := make(map[string]int)

	if s.db == nil || s.db.GetDB() == nil {
		return stats
	}

	db := s.db.GetDB()

	// 统计各表的记录数
	tables := []string{"stock_basic", "stock_daily", "technical_signals", "ai_analysis_log"}

	for _, table := range tables {
		var count int
		query := fmt.Sprintf("SELECT COUNT(*) FROM %s", table)
		err := db.QueryRow(query).Scan(&count)
		if err != nil {
			AppLogger.Debug("获取表 %s 记录数失败: %v", table, err)
			count = 0
		}
		stats[table] = count
	}

	return stats
}

// BackupDatabase 备份数据库
func (s *DataService) BackupDatabase(backupPath string) error {
	s.mutex.RLock()
	defer s.mutex.RUnlock()

	if !s.IsConnected() {
		return fmt.Errorf("数据库未连接")
	}

	// 确保备份目录存在
	backupDir := filepath.Dir(backupPath)
	if err := os.MkdirAll(backupDir, 0755); err != nil {
		return fmt.Errorf("创建备份目录失败: %v", err)
	}

	// 执行数据库备份
	source, err := os.Open(s.dbPath)
	if err != nil {
		return fmt.Errorf("打开源数据库失败: %v", err)
	}
	defer source.Close()

	destination, err := os.Create(backupPath)
	if err != nil {
		return fmt.Errorf("创建备份文件失败: %v", err)
	}
	defer destination.Close()

	// 复制文件
	_, err = destination.ReadFrom(source)
	if err != nil {
		return fmt.Errorf("复制数据库文件失败: %v", err)
	}

	AppLogger.Info("数据库备份成功: %s", backupPath)
	return nil
}

// RestoreDatabase 恢复数据库
func (s *DataService) RestoreDatabase(backupPath string) error {
	s.mutex.Lock()
	defer s.mutex.Unlock()

	// 关闭当前连接
	if s.db != nil {
		s.db.Close()
	}

	// 恢复数据库文件
	source, err := os.Open(backupPath)
	if err != nil {
		return fmt.Errorf("打开备份文件失败: %v", err)
	}
	defer source.Close()

	destination, err := os.Create(s.dbPath)
	if err != nil {
		return fmt.Errorf("创建数据库文件失败: %v", err)
	}
	defer destination.Close()

	// 复制文件
	_, err = destination.ReadFrom(source)
	if err != nil {
		return fmt.Errorf("恢复数据库文件失败: %v", err)
	}

	// 重新连接数据库
	database, err := models.NewDatabase(s.dbPath)
	if err != nil {
		return fmt.Errorf("重新连接数据库失败: %v", err)
	}

	s.db = database
	AppLogger.Info("数据库恢复成功: %s", backupPath)
	return nil
}

// VacuumDatabase 优化数据库
func (s *DataService) VacuumDatabase() error {
	s.mutex.Lock()
	defer s.mutex.Unlock()

	if !s.IsConnected() {
		return fmt.Errorf("数据库未连接")
	}

	_, err := s.db.GetDB().Exec("VACUUM")
	if err != nil {
		return fmt.Errorf("数据库优化失败: %v", err)
	}

	AppLogger.Info("数据库优化完成")
	return nil
}

// GetDatabaseSize 获取数据库文件大小
func (s *DataService) GetDatabaseSize() (int64, error) {
	fileInfo, err := os.Stat(s.dbPath)
	if err != nil {
		return 0, err
	}
	return fileInfo.Size(), nil
}


// GetAllStockBasic 获取所有股票基本信息
func (s *DataService) GetAllStockBasic() ([]*models.StockBasic, error) {
	s.mutex.RLock()
	defer s.mutex.RUnlock()

	if !s.IsConnected() {
		return nil, fmt.Errorf("数据库未连接")
	}

	query := `SELECT code, name, industry, market, listing_date, created_at, updated_at
			  FROM stock_basic ORDER BY code`

	rows, err := s.db.GetDB().Query(query)
	if err != nil {
		return nil, fmt.Errorf("查询股票基本信息失败: %v", err)
	}
	defer rows.Close()

	var stocks []*models.StockBasic
	for rows.Next() {
		stock := &models.StockBasic{}
		err := rows.Scan(&stock.Code, &stock.Name, &stock.Industry,
			&stock.Market, &stock.ListingDate, &stock.CreatedAt, &stock.UpdatedAt)
		if err != nil {
			return nil, fmt.Errorf("扫描股票基本信息失败: %v", err)
		}
		stocks = append(stocks, stock)
	}

	return stocks, nil
}

// SaveStockBasic 保存股票基本信息
func (s *DataService) SaveStockBasic(stock *models.StockBasic) error {
	s.mutex.Lock()
	defer s.mutex.Unlock()

	if !s.IsConnected() {
		return fmt.Errorf("数据库未连接")
	}

	query := `INSERT OR REPLACE INTO stock_basic
			  (code, name, industry, market, listing_date, created_at, updated_at)
			  VALUES (?, ?, ?, ?, ?, ?, ?)`

	_, err := s.db.GetDB().Exec(query, stock.Code, stock.Name, stock.Industry,
		stock.Market, stock.ListingDate, stock.CreatedAt, stock.UpdatedAt)

	if err != nil {
		return fmt.Errorf("保存股票基本信息失败: %v", err)
	}

	AppLogger.Debug("保存股票基本信息: %s - %s", stock.Code, stock.Name)
	return nil
}

// UpdateStockBasic 更新股票基本信息
func (s *DataService) UpdateStockBasic(stock *models.StockBasic) error {
	s.mutex.Lock()
	defer s.mutex.Unlock()

	if !s.IsConnected() {
		return fmt.Errorf("数据库未连接")
	}

	query := `UPDATE stock_basic SET
			  name = ?, industry = ?, market = ?, listing_date = ?, updated_at = ?
			  WHERE code = ?`

	_, err := s.db.GetDB().Exec(query, stock.Name, stock.Industry,
		stock.Market, stock.ListingDate, stock.UpdatedAt, stock.Code)

	if err != nil {
		return fmt.Errorf("更新股票基本信息失败: %v", err)
	}

	AppLogger.Debug("更新股票基本信息: %s - %s", stock.Code, stock.Name)
	return nil
}

// SaveStockDaily 保存日线数据
func (s *DataService) SaveStockDaily(daily *models.StockDaily) error {
	s.mutex.Lock()
	defer s.mutex.Unlock()

	if !s.IsConnected() {
		return fmt.Errorf("数据库未连接")
	}

	query := `INSERT OR REPLACE INTO stock_daily
			  (code, date, open, high, low, close, volume, amount, created_at, updated_at)
			  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`

	_, err := s.db.GetDB().Exec(query, daily.Code, daily.Date, daily.Open, daily.High,
		daily.Low, daily.Close, daily.Volume, daily.Amount, daily.CreatedAt, daily.UpdatedAt)

	if err != nil {
		return fmt.Errorf("保存日线数据失败: %v", err)
	}

	AppLogger.Debug("保存日线数据: %s - %s", daily.Code, daily.Date.Format("2006-01-02"))
	return nil
}