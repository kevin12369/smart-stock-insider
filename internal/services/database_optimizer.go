package services

import (
	"context"
	"database/sql"
	"fmt"
	"log"
	"strings"
	"time"
)

// DatabaseOptimizer 数据库优化器
type DatabaseOptimizer struct {
	db *sql.DB
}

// NewDatabaseOptimizer 创建数据库优化器
func NewDatabaseOptimizer(db *sql.DB) *DatabaseOptimizer {
	return &DatabaseOptimizer{db: db}
}

// OptimizationOptimization 优化选项
type OptimizationOptimization struct {
	EnableIndexOptimization   bool
	EnableQueryOptimization    bool
	EnableConnectionPooling     bool
	EnablePreparedStatement   bool
	EnableBatchOperations     bool
}

// DefaultOptimizationOptions 默认优化选项
func DefaultOptimizationOptions() *OptimizationOptimization {
	return &OptimizationOptimization{
		EnableIndexOptimization: true,
		EnableQueryOptimization:  true,
		EnableConnectionPooling:   true,
		EnablePreparedStatement:  true,
		EnableBatchOperations:    true,
	}
}

// OptimizeDatabase 优化数据库
func (do *DatabaseOptimizer) OptimizeDatabase(ctx context.Context, options *OptimizationOptimization) error {
	if options == nil {
		options = DefaultOptimizationOptions()
	}

	var errors []error

	// 1. 连接池优化
	if options.EnableConnectionPooling {
		if err := do.optimizeConnectionPool(); err != nil {
			errors = append(errors, fmt.Errorf("连接池优化失败: %w", err))
		}
	}

	// 2. 索引优化
	if options.EnableIndexOptimization {
		if err := do.optimizeIndexes(ctx); err != nil {
			errors = append(errors, fmt.Errorf("索引优化失败: %w", err))
		}
	}

	// 3. 查询优化
	if options.EnableQueryOptimization {
		if err := do.optimizeQueryPerformance(ctx); err != nil {
			errors = append(errors, fmt.Errorf("查询优化失败: %w", err))
		}
	}

	// 4. 分析表统计信息
	if err := do.analyzeTableStatistics(ctx); err != nil {
		errors = append(errors, fmt.Errorf("统计信息分析失败: %w", err))
	}

	if len(errors) > 0 {
		return fmt.Errorf("数据库优化部分失败: %v", errors)
	}

	return nil
}

// optimizeConnectionPool 优化连接池
func (do *DatabaseOptimizer) optimizeConnectionPool() error {
	// 设置连接池参数
	do.db.SetMaxOpenConns(25)        // 最大打开连接数
	do.db.SetMaxIdleConns(10)        // 最大空闲连接数
	do.db.SetConnMaxLifetime(5 * time.Minute) // 连接最大生存时间
	do.db.SetConnMaxIdleTime(2 * time.Minute) // 空闲连接最大生存时间

	log.Println("数据库连接池优化完成")
	return nil
}

// optimizeIndexes 优化索引
func (do *DatabaseOptimizer) optimizeIndexes(ctx context.Context) error {
	// 获取表名
	tables, err := do.getTableList(ctx)
	if err != nil {
		return err
	}

	for _, table := range tables {
		if err := do.optimizeTableIndexes(ctx, table); err != nil {
			log.Printf("优化表 %s 索引失败: %v", table, err)
		}
	}

	return nil
}

// getTableList 获取表列表
func (do *DatabaseOptimizer) getTableList(ctx context.Context) ([]string, error) {
	query := `
		SELECT name FROM sqlite_master
		WHERE type='table' AND name NOT LIKE 'sqlite_%'
		ORDER BY name
	`

	rows, err := do.db.QueryContext(ctx, query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var tables []string
	for rows.Next() {
		var tableName string
		if err := rows.Scan(&tableName); err != nil {
			return nil, err
		}
		tables = append(tables, tableName)
	}

	return tables, nil
}

// optimizeTableIndexes 优化表索引
func (do *DatabaseOptimizer) optimizeTableIndexes(ctx context.Context, tableName string) error {
	// 检查并创建必要的索引
	indexes := do.getRequiredIndexes(tableName)

	for _, index := range indexes {
		if err := do.createIndexIfNotExists(ctx, index); err != nil {
			log.Printf("创建索引失败: %v", err)
		}
	}

	return nil
}

// getRequiredIndexes 获取必需的索引
func (do *DatabaseOptimizer) getRequiredIndexes(tableName string) []IndexDefinition {
	switch tableName {
	case "stock_basic":
		return []IndexDefinition{
			{Table: tableName, Name: "idx_stock_code", Columns: []string{"code"}, Unique: true},
			{Table: tableName, Name: "idx_stock_market", Columns: []string{"market"}},
			{Table: tableName, Name: "idx_stock_industry", Columns: []string{"industry"}},
		}
	case "stock_daily":
		return []IndexDefinition{
			{Table: tableName, Name: "idx_daily_code_date", Columns: []string{"code", "date"}},
			{Table: tableName, Name: "idx_daily_date", Columns: []string{"date"}},
			{Table: tableName, Name: "idx_daily_volume", Columns: []string{"volume"}},
		}
	case "technical_signals":
		return []IndexDefinition{
			{Table: tableName, Name: "idx_signal_code_date", Columns: []string{"code", "date"}},
			{Table: tableName, Name: "idx_signal_type", Columns: []string{"signal_type"}},
			{Table: tableName, Name: "idx_signal_strength", Columns: []string{"strength"}},
			{Table: tableName, Name: "idx_signal_created", Columns: []string{"created_at"}},
		}
	case "news_items":
		return []IndexDefinition{
			{Table: tableName, Name: "idx_news_source", Columns: []string{"source"}},
			{Table: tableName, Name: "idx_news_category", Columns: []string{"category"}},
			{Table: tableName, Name: "idx_news_publish_time", Columns: []string{"publish_time"}},
			{Table: tableName, Name: "idx_news_codes", Columns: []string{"stock_codes"}},
		}
	case "user_portfolio":
		return []IndexDefinition{
			{Table: tableName, Name: "idx_portfolio_user", Columns: []string{"user_id"}},
			{Table: tableName, Name: "idx_portfolio_updated", Columns: []string{"updated_at"}},
		}
	default:
		return []IndexDefinition{}
	}
}

// IndexDefinition 索引定义
type IndexDefinition struct {
	Table    string
	Name     string
	Columns  []string
	Unique   bool
	Partial  string
	Descending bool
}

// createIndexIfNotExists 如果索引不存在则创建
func (do *DatabaseOptimizer) createIndexIfNotExists(ctx context.Context, index IndexDefinition) error {
	// 检查索引是否存在
	var count int
	checkQuery := `
		SELECT COUNT(*) FROM sqlite_master
		WHERE type='index' AND name=?
	`
	err := do.db.QueryRowContext(ctx, checkQuery, index.Name).Scan(&count)
	if err != nil {
		return err
	}

	if count > 0 {
		return nil // 索引已存在
	}

	// 创建索引
	var uniqueClause string
	if index.Unique {
		uniqueClause = "UNIQUE"
	}

	var columns []string
	for _, col := range index.Columns {
		if index.Descending {
			columns = append(columns, col+" DESC")
		} else {
			columns = append(columns, col+" ASC")
		}
	}

	query := fmt.Sprintf("CREATE %s INDEX %s ON %s (%s)",
		uniqueClause, index.Name, index.Table, strings.Join(columns, ", "))

	_, err = do.db.ExecContext(ctx, query)
	if err != nil {
		return err
	}

	log.Printf("创建索引: %s", index.Name)
	return nil
}

// optimizeQueryPerformance 优化查询性能
func (do *DatabaseOptimizer) optimizeQueryPerformance(ctx context.Context) error {
	// 启用WAL模式以提升并发性能
	if _, err := do.db.ExecContext(ctx, "PRAGMA journal_mode=WAL"); err != nil {
		return err
	}

	// 设置同步模式为NORMAL以提升写入性能
	if _, err := do.db.ExecContext(ctx, "PRAGMA synchronous=NORMAL"); err != nil {
		return err
	}

	// 设置缓存大小
	if _, err := do.db.ExecContext(ctx, "PRAGMA cache_size=10000"); err != nil {
		return err
	}

	// 设置临时存储为内存
	if _, err := do.db.ExecContext(ctx, "PRAGMA temp_store=memory"); err != nil {
		return err
	}

	// 启用查询计划器优化
	if _, err := do.db.ExecContext(ctx, "PRAGMA optimize"); err != nil {
		return err
	}

	log.Println("查询性能优化完成")
	return nil
}

// analyzeTableStatistics 分析表统计信息
func (do *DatabaseOptimizer) analyzeTableStatistics(ctx context.Context) error {
	tables, err := do.getTableList(ctx)
	if err != nil {
		return err
	}

	for _, table := range tables {
		query := fmt.Sprintf("ANALYZE %s", table)
		if _, err := do.db.ExecContext(ctx, query); err != nil {
			log.Printf("分析表 %s 统计信息失败: %v", table, err)
		} else {
			log.Printf("分析表 %s 统计信息完成", table)
		}
	}

	return nil
}

// GetDatabaseStats 获取数据库统计信息
func (do *DatabaseOptimizer) GetDatabaseStats(ctx context.Context) (map[string]interface{}, error) {
	stats := make(map[string]interface{})

	// 获取数据库页数
	var pageCount int
	err := do.db.QueryRowContext(ctx, "PRAGMA page_count").Scan(&pageCount)
	if err != nil {
		return nil, err
	}
	stats["page_count"] = pageCount

	// 获取页面大小
	var pageSize int
	err = do.db.QueryRowContext(ctx, "PRAGMA page_size").Scan(&pageSize)
	if err != nil {
		return nil, err
	}
	stats["page_size"] = pageSize

	// 计算数据库大小
	stats["database_size"] = pageCount * pageSize

	// 获取缓存命中率
	var cacheHits, cacheMisses int
	do.db.QueryRowContext(ctx, "PRAGMA cache_hits").Scan(&cacheHits)
	do.db.QueryRowContext(ctx, "PRAGMA cache_misses").Scan(&cacheMisses)

	if cacheHits+cacheMisses > 0 {
		stats["cache_hit_rate"] = float64(cacheHits) / float64(cacheHits+cacheMisses)
	}

	// 获取表统计信息
	tableStats := make(map[string]interface{})
	tables, err := do.getTableList(ctx)
	if err != nil {
		return nil, err
	}

	for _, table := range tables {
		var rowCount int
		err := do.db.QueryRowContext(ctx, fmt.Sprintf("SELECT COUNT(*) FROM %s", table)).Scan(&rowCount)
		if err != nil {
			continue
		}

		tableStats[table] = map[string]interface{}{
			"row_count": rowCount,
		}
	}
	stats["tables"] = tableStats

	return stats, nil
}

// VacuumDatabase 清理数据库碎片
func (do *DatabaseOptimizer) VacuumDatabase(ctx context.Context) error {
	log.Println("开始数据库VACUUM操作...")

	start := time.Now()
	_, err := do.db.ExecContext(ctx, "VACUUM")
	duration := time.Since(start)

	if err != nil {
		return fmt.Errorf("VACUUM操作失败: %w", err)
	}

	log.Printf("数据库VACUUM操作完成，耗时: %v", duration)
	return nil
}

// OptimizeForProduction 生产环境优化
func (do *DatabaseOptimizer) OptimizeForProduction(ctx context.Context) error {
	options := &OptimizationOptimization{
		EnableIndexOptimization: true,
		EnableQueryOptimization:  true,
		EnableConnectionPooling:   true,
		EnablePreparedStatement:  true,
		EnableBatchOperations:    true,
	}

	return do.OptimizeDatabase(ctx, options)
}

// OptimizeForDevelopment 开发环境优化
func (do *DatabaseOptimizer) OptimizeForDevelopment(ctx context.Context) error {
	options := &OptimizationOptimization{
		EnableIndexOptimization: true,
		EnableQueryOptimization: false, // 开发环境关闭查询优化以便调试
		EnableConnectionPooling:   true,
		EnablePreparedStatement:  false,
		EnableBatchOperations:    true,
	}

	return do.OptimizeDatabase(ctx, options)
}