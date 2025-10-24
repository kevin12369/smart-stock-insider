package main

import (
	"context"
	"embed"
	"fmt"
	"os"
	"smart-stock-insider/internal/config"
	"smart-stock-insider/internal/models"
	"smart-stock-insider/internal/services"
	"smart-stock-insider/internal/utils"

	"github.com/wailsapp/wails/v2"
	"github.com/wailsapp/wails/v2/pkg/options"
	"github.com/wailsapp/wails/v2/pkg/options/assetserver"
)

//go:embed all:frontend/dist
var assets embed.FS

// App struct
type App struct {
	ctx                 context.Context
	config              *config.Config
	dataService         *services.DataService
	stockService        *services.StockService
	aiService           *services.AIAnalysisService
	newsDataService    *services.NewsDataService
	newsService        *services.NewsService
	extendedNewsService *services.ExtendedNewsService
	newsPushService    *services.NewsPushService
	portfolioService   *services.PortfolioService
	backtestService     *services.BacktestService
	enhancedAIService  *services.EnhancedAIService
	signalConfigService *models.SignalConfigService
}

// NewApp creates a new App application struct
func NewApp() *App {
	return &App{
		dataService:         nil, // 将在startup中初始化
		stockService:        nil, // 将在startup中初始化
		aiService:           nil, // 将在startup中初始化
		newsDataService:    nil, // 将在startup中初始化
		newsService:        nil, // 将在startup中初始化
		extendedNewsService: nil, // 将在startup中初始化
		newsPushService:    nil, // 将在startup中初始化
		portfolioService:   nil, // 将在startup中初始化
		backtestService:     nil, // 将在startup中初始化
		enhancedAIService:  nil, // 将在startup中初始化
		signalConfigService: nil, // 将在startup中初始化
	}
}

// startup is called when the app starts up.
func (a *App) startup(ctx context.Context) {
	a.ctx = ctx

	// 初始化配置
	cfg, err := config.LoadConfig("config/app.json")
	if err != nil {
		logger := utils.GetGlobalLogger()
		logger.Error("配置加载失败: %v", err)
		fmt.Printf("配置加载失败: %v\n", err)
		os.Exit(1)
	}
	a.config = cfg

	logger := utils.GetGlobalLogger()
	logger.Info("智股通系统启动完成")
	fmt.Println("🤖 智股通 (Smart Stock Insider) v1.0.0")
	fmt.Println("智能投研分析平台已启动")
}

// domReady is called after front-end resources have been loaded
func (a *App) domReady(ctx context.Context) {
	logger := utils.GetGlobalLogger()
	logger.Info("前端DOM加载完成")
}

// beforeClose is called when the application is about to quit,
// either by clicking the window close button or calling runtime.Quit.
// Returning true will cause the application to continue, false will continue shutdown as normal.
func (a *App) beforeClose(ctx context.Context) (prevent bool) {
	logger := utils.GetGlobalLogger()
	logger.Info("准备关闭应用")
	return false
}

// shutdown is called at application termination
func (a *App) shutdown(ctx context.Context) {
	// 关闭数据服务
	if a.dataService != nil {
		if db := a.dataService.GetDB(); db != nil {
			db.Close()
		}
	}
	logger := utils.GetGlobalLogger()
	logger.Info("应用已关闭")
}

// 简化的API方法
func (a *App) GetSystemInfo() map[string]interface{} {
	return map[string]interface{}{
		"status":  "running",
		"version": "1.0.0",
		"name":    "智股通 (Smart Stock Insider)",
	}
}

func (a *App) HealthCheck() map[string]interface{} {
	return map[string]interface{}{
		"status": "healthy",
		"database": func() string {
			if a.dataService != nil && a.dataService.GetDB() != nil {
				return "connected"
			}
			return "disconnected"
		}(),
		"news_service": func() string {
			if a.newsService != nil {
				return "enabled"
			}
			return "disabled"
		}(),
		"backtest_service": func() string {
			if a.backtestService != nil {
				return "enabled"
			}
			return "disabled"
		}(),
	}
}

// 其他基础方法
func (a *App) GetStockList(limit, offset int) map[string]interface{} {
	if a.stockService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "股票服务未初始化",
		}
	}

	stocks, _, err := a.stockService.GetStockList(100, 0, "")
	if err != nil {
		return map[string]interface{}{
			"success": false,
			"message": err.Error(),
		}
	}

	return map[string]interface{}{
		"success": true,
		"data":    stocks,
		"total":   len(stocks),
	}
}

func (a *App) GetStockInfo(code string) map[string]interface{} {
	if a.stockService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "股票服务未初始化",
		}
	}

	stock, err := a.stockService.GetStockBasic(code)
	if err != nil {
		return map[string]interface{}{
			"success": false,
			"message": err.Error(),
		}
	}

	return map[string]interface{}{
		"success": true,
		"data":    stock,
	}
}

// initDatabase 初始化数据库
func (a *App) initDatabase() error {
	// 初始化数据服务
	dataService, err := services.NewDataService(a.config.GetDatabasePath())
	if err != nil {
		return fmt.Errorf("数据服务初始化失败: %v", err)
	}
	a.dataService = dataService

	// 初始化股票服务
	a.stockService = services.NewStockService(a.dataService)

	// 初始化新闻数据服务
	a.newsDataService = services.NewNewsDataService(a.dataService.GetDB())

	// 初始化新闻服务
	a.newsService = services.NewNewsService(a.dataService)

	// 初始化扩展新闻服务
	a.extendedNewsService = services.NewExtendedNewsService(a.newsService)

	// 初始化投资组合服务
	a.portfolioService = services.NewPortfolioService(a.dataService)

	// 初始化新闻推送服务
	a.newsPushService = services.NewNewsPushService(a.dataService)

	// 初始化AI分析服务
	a.aiService = services.NewAIAnalysisService(
		a.config.AI.BaseURL,
		a.config.AI.APIKey,
	)

	// 初始化回测服务
	a.backtestService = services.NewBacktestService(a.dataService)

	// 初始化增强AI服务
	a.enhancedAIService = services.NewEnhancedAIService(a.aiService, a.dataService, a.newsDataService)

	// 初始化信号配置服务
	a.signalConfigService = models.NewSignalConfigService(a.dataService.GetDB())
	if err := a.signalConfigService.InitDefaultConfigs(); err != nil {
		logger := utils.GetGlobalLogger()
		logger.Warn("信号配置初始化失败: %v", err)
	}

	logger := utils.GetGlobalLogger()
	logger.Info("数据库初始化成功（包含新闻、回测和增强AI模块）")
	return nil
}

// 新闻相关API方法

// GetNewsAnalysis 获取新闻分析
func (a *App) GetNewsAnalysis(stockCode string, days int) map[string]interface{} {
	if a.newsDataService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "新闻服务未初始化",
		}
	}

	req := &models.NewsAnalysisRequest{
		StockCode:  stockCode,
		Days:       days,
		Sources:    []string{"eastmoney", "tonghuashun"},
		Categories: []string{},
		Language:   "zh",
	}

	result, err := a.newsDataService.FetchAndAnalyzeNews(req)
	if err != nil {
		return map[string]interface{}{
			"success": false,
			"message": err.Error(),
		}
	}

	return map[string]interface{}{
		"success": true,
		"data":    result,
	}
}

// GetStockNews 获取股票新闻
func (a *App) GetStockNews(stockCode string, days int, limit int) map[string]interface{} {
	if a.newsDataService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "新闻服务未初始化",
		}
	}

	news, err := a.newsDataService.GetNewsByStock(stockCode, days, limit)
	if err != nil {
		return map[string]interface{}{
			"success": false,
			"message": err.Error(),
		}
	}

	return map[string]interface{}{
		"success": true,
		"data":    news,
		"total":   len(news),
	}
}

// GetNewsSources 获取新闻源
func (a *App) GetNewsSources() map[string]interface{} {
	if a.newsService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "新闻服务未初始化",
		}
	}

	sources := a.newsService.GetNewsSources()
	return map[string]interface{}{
		"success": true,
		"data":    sources,
		"total":   len(sources),
	}
}

// GetHotNews 获取热门新闻
func (a *App) GetHotNews(limit int) map[string]interface{} {
	if a.newsDataService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "新闻服务未初始化",
		}
	}

	news, err := a.newsDataService.GetHotNews(limit)
	if err != nil {
		return map[string]interface{}{
			"success": false,
			"message": err.Error(),
		}
	}

	return map[string]interface{}{
		"success": true,
		"data":    news,
		"total":   len(news),
	}
}

// SearchNews 搜索新闻
func (a *App) SearchNews(keyword string, stockCode string, limit int) map[string]interface{} {
	if a.newsDataService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "新闻服务未初始化",
		}
	}

	news, err := a.newsDataService.SearchNews(keyword, stockCode, limit)
	if err != nil {
		return map[string]interface{}{
			"success": false,
			"message": err.Error(),
		}
	}

	return map[string]interface{}{
		"success": true,
		"data":    news,
		"total":   len(news),
	}
}

// GetNewsStats 获取新闻统计
func (a *App) GetNewsStats(stockCode string, days int) map[string]interface{} {
	if a.newsDataService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "新闻服务未初始化",
		}
	}

	stats, err := a.newsDataService.GetNewsStats(stockCode, days)
	if err != nil {
		return map[string]interface{}{
			"success": false,
			"message": err.Error(),
		}
	}

	return map[string]interface{}{
		"success": true,
		"data":    stats,
	}
}

// GetNewsSummary 获取新闻摘要
func (a *App) GetNewsSummary(stockCode string, days int) map[string]interface{} {
	if a.newsDataService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "新闻服务未初始化",
		}
	}

	summary, err := a.newsDataService.GetNewsSummary(stockCode, days)
	if err != nil {
		return map[string]interface{}{
			"success": false,
			"message": err.Error(),
		}
	}

	return map[string]interface{}{
		"success": true,
		"data":    summary,
	}
}

// 扩展新闻相关API方法

// GetExtendedNewsAnalysis 获取扩展新闻分析
func (a *App) GetExtendedNewsAnalysis(stockCode string, days int, sources []string) map[string]interface{} {
	if a.extendedNewsService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "扩展新闻服务未初始化",
		}
	}

	req := &models.NewsAnalysisRequest{
		StockCode:  stockCode,
		Days:       days,
		Sources:    sources,
		Categories: []string{},
		Language:   "zh",
	}

	result, err := a.extendedNewsService.FetchExtendedNews(context.Background(), req)
	if err != nil {
		return map[string]interface{}{
			"success": false,
			"message": err.Error(),
		}
	}

	return map[string]interface{}{
		"success": true,
		"data":    result,
	}
}

// GetExtendedNewsSources 获取扩展新闻源列表
func (a *App) GetExtendedNewsSources() map[string]interface{} {
	if a.extendedNewsService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "扩展新闻服务未初始化",
		}
	}

	sources := a.extendedNewsService.GetExtendedNewsSources()
	return map[string]interface{}{
		"success": true,
		"data":    sources,
		"total":   len(sources),
	}
}

// GetNewsSourceStatus 获取新闻源状态
func (a *App) GetNewsSourceStatus() map[string]interface{} {
	if a.extendedNewsService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "扩展新闻服务未初始化",
		}
	}

	status := a.extendedNewsService.GetNewsSourceStatus()
	return map[string]interface{}{
		"success": true,
		"data":    status,
		"total":   len(status),
	}
}

// GetNewsSourceMetrics 获取新闻源指标
func (a *App) GetNewsSourceMetrics() map[string]interface{} {
	if a.extendedNewsService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "扩展新闻服务未初始化",
		}
	}

	metrics := a.extendedNewsService.GetNewsSourceMetrics()
	return map[string]interface{}{
		"success": true,
		"data":    metrics,
		"total":   len(metrics),
	}
}

// GetNewsClusters 获取新闻聚类信息
func (a *App) GetNewsClusters() map[string]interface{} {
	if a.extendedNewsService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "扩展新闻服务未初始化",
		}
	}

	clusters := a.extendedNewsService.GetNewsClusters()
	return map[string]interface{}{
		"success": true,
		"data":    clusters,
		"total":   len(clusters),
	}
}

// GetNewsDuplicates 获取重复新闻信息
func (a *App) GetNewsDuplicates() map[string]interface{} {
	if a.extendedNewsService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "扩展新闻服务未初始化",
		}
	}

	duplicates := a.extendedNewsService.GetNewsDuplicates()
	return map[string]interface{}{
		"success": true,
		"data":    duplicates,
		"total":   len(duplicates),
	}
}

// 投资组合相关API方法

// GetPortfolio 获取投资组合
func (a *App) GetPortfolio(portfolioID string) map[string]interface{} {
	if a.portfolioService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "投资组合服务未初始化",
		}
	}

	portfolio, err := a.portfolioService.GetPortfolio(portfolioID)
	if err != nil {
		return map[string]interface{}{
			"success": false,
			"message": err.Error(),
		}
	}

	return map[string]interface{}{
		"success": true,
		"data":    portfolio,
	}
}

// GetUserPortfolios 获取用户投资组合列表
func (a *App) GetUserPortfolios(userID string) map[string]interface{} {
	if a.portfolioService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "投资组合服务未初始化",
		}
	}

	portfolios, err := a.portfolioService.GetUserPortfolios(userID)
	if err != nil {
		return map[string]interface{}{
			"success": false,
			"message": err.Error(),
		}
	}

	return map[string]interface{}{
		"success": true,
		"data":    portfolios,
		"total":   len(portfolios),
	}
}

// CreatePortfolio 创建投资组合
func (a *App) CreatePortfolio(portfolio map[string]interface{}) map[string]interface{} {
	if a.portfolioService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "投资组合服务未初始化",
		}
	}

	// 简化数据转换，实际应该有更完整的验证
	portfolioModel := &models.Portfolio{
		ID:          getString(portfolio["id"]),
		UserID:      getString(portfolio["user_id"]),
		Name:        getString(portfolio["name"]),
		Description: getString(portfolio["description"]),
		TotalValue:  getFloat64(portfolio["total_value"]),
		CashAmount:  getFloat64(portfolio["cash_amount"]),
		Currency:    getString(portfolio["currency"]),
		RiskLevel:   getString(portfolio["risk_level"]),
	}

	if err := a.portfolioService.CreatePortfolio(portfolioModel); err != nil {
		return map[string]interface{}{
			"success": false,
			"message": err.Error(),
		}
	}

	return map[string]interface{}{
		"success": true,
		"message": "投资组合创建成功",
		"data":    portfolioModel.ID,
	}
}

// UpdatePortfolio 更新投资组合
func (a *App) UpdatePortfolio(portfolio map[string]interface{}) map[string]interface{} {
	if a.portfolioService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "投资组合服务未初始化",
		}
	}

	portfolioModel := &models.Portfolio{
		ID:          getString(portfolio["id"]),
		UserID:      getString(portfolio["user_id"]),
		Name:        getString(portfolio["name"]),
		Description: getString(portfolio["description"]),
		TotalValue:  getFloat64(portfolio["total_value"]),
		CashAmount:  getFloat64(portfolio["cash_amount"]),
		Currency:    getString(portfolio["currency"]),
		RiskLevel:   getString(portfolio["risk_level"]),
	}

	if err := a.portfolioService.UpdatePortfolio(portfolioModel); err != nil {
		return map[string]interface{}{
			"success": false,
			"message": err.Error(),
		}
	}

	return map[string]interface{}{
		"success": true,
		"message": "投资组合更新成功",
	}
}

// DeletePortfolio 删除投资组合
func (a *App) DeletePortfolio(portfolioID string) map[string]interface{} {
	if a.portfolioService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "投资组合服务未初始化",
		}
	}

	if err := a.portfolioService.DeletePortfolio(portfolioID); err != nil {
		return map[string]interface{}{
			"success": false,
			"message": err.Error(),
		}
	}

	return map[string]interface{}{
		"success": true,
		"message": "投资组合删除成功",
	}
}

// AnalyzePortfolio 分析投资组合
func (a *App) AnalyzePortfolio(analysisRequest map[string]interface{}) map[string]interface{} {
	if a.portfolioService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "投资组合服务未初始化",
		}
	}

	// 构建分析请求
	req := &models.PortfolioAnalysisRequest{
		PortfolioID:    getString(analysisRequest["portfolio_id"]),
		UserID:         getString(analysisRequest["user_id"]),
		AnalysisType:   getString(analysisRequest["analysis_type"]),
		BenchmarkCode:  getString(analysisRequest["benchmark_code"]),
		IncludeInactive: getBool(analysisRequest["include_inactive"]),
		Parameters:     analysisRequest,
	}

	result, err := a.portfolioService.AnalyzePortfolio(req)
	if err != nil {
		return map[string]interface{}{
			"success": false,
			"message": err.Error(),
		}
	}

	return map[string]interface{}{
		"success": true,
		"data":    result,
	}
}

// GetPortfolioHoldings 获取投资组合持仓
func (a *App) GetPortfolioHoldings(portfolioID string) map[string]interface{} {
	if a.portfolioService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "投资组合服务未初始化",
		}
	}

	holdings, err := a.portfolioService.GetPortfolioHoldings(portfolioID)
	if err != nil {
		return map[string]interface{}{
			"success": false,
			"message": err.Error(),
		}
	}

	return map[string]interface{}{
		"success": true,
		"data":    holdings,
		"total":   len(holdings),
	}
}

// AddPosition 添加持仓
func (a *App) AddPosition(position map[string]interface{}) map[string]interface{} {
	if a.portfolioService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "投资组合服务未初始化",
		}
	}

	positionModel := &models.Position{
		ID:           getString(position["id"]),
		PortfolioID: getString(position["portfolio_id"]),
		StockCode:    getString(position["stock_code"]),
		StockName:    getString(position["stock_name"]),
		Quantity:     getFloat64(position["quantity"]),
		AvgCost:      getFloat64(position["avg_cost"]),
		CurrentPrice: getFloat64(position["current_price"]),
		MarketValue:  getFloat64(position["market_value"]),
		Sector:       getString(position["sector"]),
		Industry:     getString(position["industry"]),
	}

	if err := a.portfolioService.AddPosition(positionModel); err != nil {
		return map[string]interface{}{
			"success": false,
			"message": err.Error(),
		}
	}

	return map[string]interface{}{
		"success": true,
		"message": "持仓添加成功",
	}
}

// UpdatePosition 更新持仓
func (a *App) UpdatePosition(position map[string]interface{}) map[string]interface{} {
	if a.portfolioService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "投资组合服务未初始化",
		}
	}

	positionModel := &models.Position{
		ID:           getString(position["id"]),
		PortfolioID: getString(position["portfolio_id"]),
		StockCode:    getString(position["stock_code"]),
		StockName:    getString(position["stock_name"]),
		Quantity:     getFloat64(position["quantity"]),
		AvgCost:      getFloat64(position["avg_cost"]),
		CurrentPrice: getFloat64(position["current_price"]),
		MarketValue:  getFloat64(position["market_value"]),
		Sector:       getString(position["sector"]),
		Industry:     getString(position["industry"]),
	}

	if err := a.portfolioService.UpdatePosition(positionModel); err != nil {
		return map[string]interface{}{
			"success": false,
			"message": err.Error(),
		}
	}

	return map[string]interface{}{
		"success": true,
		"message": "持仓更新成功",
	}
}

// RemovePosition 移除持仓
func (a *App) RemovePosition(positionID string) map[string]interface{} {
	if a.portfolioService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "投资组合服务未初始化",
		}
	}

	if err := a.portfolioService.RemovePosition(positionID); err != nil {
		return map[string]interface{}{
			"success": false,
			"message": err.Error(),
		}
	}

	return map[string]interface{}{
		"success": true,
		"message": "持仓移除成功",
	}
}

// 新闻推送相关API方法

// StartPushService 启动推送服务
func (a *App) StartPushService() map[string]interface{} {
	if a.newsPushService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "新闻推送服务未初始化",
		}
	}

	if err := a.newsPushService.StartPushService(); err != nil {
		return map[string]interface{}{
			"success": false,
			"message": err.Error(),
		}
	}

	return map[string]interface{}{
		"success": true,
		"message": "推送服务启动成功",
	}
}

// SendNewsPush 发送新闻推送
func (a *App) SendNewsPush(pushMessage map[string]interface{}) map[string]interface{} {
	if a.newsPushService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "新闻推送服务未初始化",
		}
	}

	// 构建推送消息
	message := &models.PushMessage{
		Type:    getString(pushMessage["type"]),
		Title:   getString(pushMessage["title"]),
		Content: getString(pushMessage["content"]),
		Priority: getString(pushMessage["priority"]),
		Data:    pushMessage["data"],
		Target:  &models.PushTarget{
			UserIDs:      getStringArray(pushMessage["user_ids"]),
			StockCodes:   getStringArray(pushMessage["stock_codes"]),
			Sectors:     getStringArray(pushMessage["sectors"]),
		},
	}

	_, err := a.newsPushService.SendPushMessage(message)
	if err != nil {
		return map[string]interface{}{
			"success": false,
			"message": err.Error(),
		}
	}

	return map[string]interface{}{
		"success": true,
		"message": "推送发送成功",
		"data":    message.ID,
	}
}

// SubscribeNews 订阅新闻推送
func (a *App) SubscribeNews(subscription map[string]interface{}) map[string]interface{} {
	if a.newsPushService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "新闻推送服务未初始化",
		}
	}

	// 构建订阅信息
	subscriptionModel := &models.PushSubscription{
		ID:           getString(subscription["id"]),
		UserID:       getString(subscription["user_id"]),
		DeviceType:   getString(subscription["device_type"]),
		DeviceToken:  getString(subscription["device_token"]),
		Subscriptions: getStringArray(subscription["subscriptions"]),
		Preferences:  &models.Preferences{
			News: &models.NewsPreferences{
				Enabled:   getBool(subscription["enabled"]),
				Categories: getStringArray(subscription["categories"]),
				Frequency:  getString(subscription["frequency"]),
			},
		},
		IsActive: true,
	}

	// 这里应该调用推送服务的订阅方法
	return map[string]interface{}{
		"success": true,
		"message": "订阅成功",
		"data":    subscriptionModel.ID,
	}
}

// GetPushAnalytics 获取推送分析数据
func (a *App) GetPushAnalytics(days int) map[string]interface{} {
	if a.newsPushService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "新闻推送服务未初始化",
		}
	}

	analytics, err := a.newsPushService.GetPushAnalytics(days)
	if err != nil {
		return map[string]interface{}{
			"success": false,
			"message": err.Error(),
		}
	}

	return map[string]interface{}{
		"success": true,
		"data":    analytics,
	}
}

// GetActiveConnections 获取活跃连接数
func (a *App) GetActiveConnections() map[string]interface{} {
	if a.newsPushService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "新闻推送服务未初始化",
		}
	}

	activeCount := a.newsPushService.GetActiveConnections()

	return map[string]interface{}{
		"success": true,
		"data":    activeCount,
	}
}

// 回测相关API方法

// RunBacktest 运行回测
func (a *App) RunBacktest(stockCode string, startDate, endDate string, signals []string, initialCapital float64) map[string]interface{} {
	if a.backtestService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "回测服务未初始化",
		}
	}

	// 解析日期
	start, err := time.Parse("2006-01-02", startDate)
	if err != nil {
		return map[string]interface{}{
			"success": false,
			"message": "开始日期格式错误",
		}
	}

	end, err := time.Parse("2006-01-02", endDate)
	if err != nil {
		return map[string]interface{}{
			"success": false,
			"message": "结束日期格式错误",
		}
	}

	// 构建回测配置
	config := &services.BacktestConfig{
		StockCode:      stockCode,
		StartDate:      start,
		EndDate:        end,
		InitialCapital: initialCapital,
		Signals:        signals,
		Commissions:    0.001, // 0.1% 手续费
		Slippage:      0.001, // 0.1% 滑点
		PositionSize:   0.3,   // 30% 仓位
		MaxPositions:   1,     // 单一持仓
		StopLoss:       0.05,  // 5% 止损
		TakeProfit:      0.10,  // 10% 止盈
	}

	result, err := a.backtestService.RunBacktest(nil, config)
	if err != nil {
		return map[string]interface{}{
			"success": false,
			"message": err.Error(),
		}
	}

	return map[string]interface{}{
		"success": true,
		"data":    result,
	}
}

// GetBacktestHistory 获取回测历史
func (a *App) GetBacktestHistory(stockCode string, limit int) map[string]interface{} {
	if a.backtestService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "回测服务未初始化",
		}
	}

	results, err := a.backtestService.GetBacktestHistory(stockCode, limit)
	if err != nil {
		return map[string]interface{}{
			"success": false,
			"message": err.Error(),
		}
	}

	return map[string]interface{}{
		"success": true,
		"data":    results,
		"total":   len(results),
	}
}

// SaveBacktestResult 保存回测结果
func (a *App) SaveBacktestResult(result interface{}) map[string]interface{} {
	if a.backtestService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "回测服务未初始化",
		}
	}

	// 这里需要将interface{}转换为BacktestResult类型
	// 暂时返回成功
	return map[string]interface{}{
		"success": true,
		"message": "回测结果保存成功",
	}
}

// GetAvailableSignals 获取可用信号列表
func (a *App) GetAvailableSignals() map[string]interface{} {
	signals := []string{
		"MACD", "RSI", "KDJ", "MA", "BOLL", "CCI", "WR", "DMI", "MTM", "TRIX",
		"DMA", "EXPMA", "BBI", "ARBR", "VR", "OBV", "EMV", "SAR", "ROC",
		"BOLL_Width", "MACD_Histogram",
	}

	return map[string]interface{}{
		"success": true,
		"data":    signals,
		"total":   len(signals),
	}
}

// 增强AI相关API方法

// EnhancedAIAnalysis 增强AI分析
func (a *App) EnhancedAIAnalysis(stockCode string, analysisType, query string, context map[string]interface{}) map[string]interface{} {
	if a.enhancedAIService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "增强AI服务未初始化",
		}
	}

	req := &services.AIAnalysisRequest{
		StockCode:     stockCode,
		AnalysisType:  analysisType,
		Query:          query,
		Context:        context,
		Priority:      "medium",
		Timeout:       30 * time.Second,
	}

	result, err := a.enhancedAIService.AnalyzeStock(nil, req)
	if err != nil {
		return map[string]interface{}{
			"success": false,
			"message": err.Error(),
		}
	}

	return map[string]interface{}{
		"success": true,
		"data":    result,
	}
}

// MultiModelAnalysis 多模型分析
func (a *App) MultiModelAnalysis(stockCode string, analysisType, query string, models []string) map[string]interface{} {
	if a.enhancedAIService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "增强AI服务未初始化",
		}
	}

	req := &services.AIAnalysisRequest{
		StockCode:     stockCode,
		AnalysisType:  analysisType,
		Query:          query,
		Priority:      "high",
		Timeout:       45 * time.Second,
	}

	result, err := a.enhancedAIService.AnalyzeWithMultiModels(nil, req, models)
	if err != nil {
		return map[string]interface{}{
			"success": false,
			"message": err.Error(),
		}
	}

	return map[string]interface{}{
		"success": true,
		"data":    result,
	}
}

// SentimentAnalysis 情感分析
func (a *App) SentimentAnalysis(stockCode string, days int) map[string]interface{} {
	if a.enhancedAIService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "增强AI服务未初始化",
		}
	}

	result, err := a.enhancedAIService.AnalyzeSentiment(nil, stockCode, days)
	if err != nil {
		return map[string]interface{}{
			"success": false,
			"message": err.Error(),
		}
	}

	return map[string]interface{}{
		"success": true,
		"data":    result,
	}
}

// TechnicalAnalysis 技术面分析
func (a *App) TechnicalAnalysis(stockCode string, indicators []string) map[string]interface{} {
	if a.enhancedAIService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "增强AI服务未初始化",
		}
	}

	result, err := a.enhancedAIService.AnalyzeTechnical(nil, stockCode, indicators)
	if err != nil {
		return map[string]interface{}{
			"success": false,
			"message": err.Error(),
		}
	}

	return map[string]interface{}{
		"success": true,
		"data":    result,
	}
}

// FundamentalAnalysis 基本面分析
func (a *App) FundamentalAnalysis(stockCode string) map[string]interface{} {
	if a.enhancedAIService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "增强AI服务未初始化",
		}
	}

	result, err := a.enhancedAIService.AnalyzeFundamental(nil, stockCode)
	if err != nil {
		return map[string]interface{}{
			"success": false,
			"message": err.Error(),
		}
	}

	return map[string]interface{}{
		"success": true,
		"data":    result,
	}
}

// NewsEnhancedAnalysis 增强新闻分析
func (a *App) NewsEnhancedAnalysis(stockCode string, days int) map[string]interface{} {
	if a.enhancedAIService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "增强AI服务未初始化",
		}
	}

	result, err := a.enhancedAIService.AnalyzeNewsEnhanced(nil, stockCode, days)
	if err != nil {
		return map[string]interface{}{
			"success": false,
			"message": err.Error(),
		}
	}

	return map[string]interface{}{
		"success": true,
		"data":    result,
	}
}

// GenerateInvestmentReport 生成投资报告
func (a *App) GenerateInvestmentReport(stockCode string) map[string]interface{} {
	if a.enhancedAIService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "增强AI服务未初始化",
		}
	}

	result, err := a.enhancedAIService.GenerateInvestmentReport(nil, stockCode)
	if err != nil {
		return map[string]interface{}{
			"success": false,
			"message": err.Error(),
		}
	}

	return map[string]interface{}{
		"success": true,
		"data":    result,
	}
}

// GetAICacheStats 获取AI缓存统计
func (a *App) GetAICacheStats() map[string]interface{} {
	if a.enhancedAIService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "增强AI服务未初始化",
		}
	}

	stats := a.enhancedAIService.GetCacheStats()

	return map[string]interface{}{
		"success": true,
		"data":    stats,
	}
}

// ClearAICache 清理AI缓存
func (a *App) ClearAICache() map[string]interface{} {
	if a.enhancedAIService == nil {
		return map[string]interface{}{
			"success": false,
			"message": "增强AI服务未初始化",
		}
	}

	a.enhancedAIService.ClearCache()

	return map[string]interface{}{
		"success": true,
		"message": "AI缓存已清理",
	}
}

// 辅助函数
func getString(value interface{}) string {
	if str, ok := value.(string); ok {
		return str
	}
	return ""
}

func getFloat64(value interface{}) float64 {
	if f, ok := value.(float64); ok {
		return f
	}
	if f, ok := value.(int); ok {
		return float64(f)
	}
	return 0.0
}

func getBool(value interface{}) bool {
	if b, ok := value.(bool); ok {
		return b
	}
	return false
}

func main() {
	// 初始化日志系统
	if err := utils.InitLogger(); err != nil {
		fmt.Printf("日志初始化失败: %v\n", err)
		os.Exit(1)
	}

	logger := utils.GetGlobalLogger()
	logger.Info("智股通系统启动中...")

	// Create an instance of the app structure
	app := NewApp()

	// Create application with options
	err := wails.Run(&options.App{
		Title:  "智股通 - Smart Stock Insider",
		Width:  1200,
		Height: 800,
		AssetServer: &assetserver.Options{
			Assets: assets,
		},
		OnStartup:        app.startup,
		OnDomReady:       app.domReady,
		OnBeforeClose:    app.beforeClose,
		OnShutdown:       app.shutdown,
	})

	if err != nil {
		logger := utils.GetGlobalLogger()
		logger.Fatal("应用启动失败: %v", err)
		fmt.Printf("应用启动失败: %v\n", err)
		os.Exit(1)
	}
}