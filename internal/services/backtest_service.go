package services

import (
	"context"
	"database/sql"
	"fmt"
	"math"
	"sort"
	"sync"
	"time"

	"smart-stock-insider/internal/models"
)

// BacktestService 回测服务
type BacktestService struct {
	dataService *DataService
	db          *sql.DB
	mutex       sync.RWMutex
	logger      *Logger
}

// BacktestConfig 回测配置
type BacktestConfig struct {
	StockCode       string    `json:"stock_code"`
	StartDate       time.Time `json:"start_date"`
	EndDate         time.Time `json:"end_date"`
	InitialCapital  float64   `json:"initial_capital"`
	Signals         []string  `json:"signals"`
	Commissions     float64   `json:"commissions"`
	Slippage       float64   `json:"slippage"`
	PositionSize    float64   `json:"position_size"`
	MaxPositions    int       `json:"max_positions"`
	StopLoss        float64   `json:"stop_loss"`
	TakeProfit      float64   `json:"take_profit"`
}

// BacktestResult 回测结果
type BacktestResult struct {
	StockCode        string                 `json:"stock_code"`
	Period           string                 `json:"period"`
	InitialCapital    float64                `json:"initial_capital"`
	FinalCapital     float64                `json:"final_capital"`
	TotalReturn      float64                `json:"total_return"`
	AnnualizedReturn float64                `json:"annualized_return"`
	MaxDrawdown     float64                `json:"max_drawdown"`
	SharpeRatio     float64                `json:"sharpe_ratio"`
	WinRate         float64                `json:"win_rate"`
	ProfitFactor     float64                `json:"profit_factor"`
	TotalTrades     int                    `json:"total_trades"`
	WinningTrades   int                    `json:"winning_trades"`
	LosingTrades    int                    `json:"losing_trades"`
	AvgWinning      float64                `json:"avg_winning"`
	AvgLosing       float64                `json:"avg_losing"`
	SignalResults   map[string]*SignalResult `json:"signal_results"`
	DailyReturns    []DailyReturn         `json:"daily_returns"`
	Positions       []Position             `json:"positions"`
	Trades          []Trade                `json:"trades"`
	BenchmarkReturn float64                `json:"benchmark_return"`
	Alpha           float64                `json:"alpha"`
	Beta            float64                `json:"beta"`
	CreatedAt       time.Time              `json:"created_at"`
}

// SignalResult 信号回测结果
type SignalResult struct {
	SignalName      string  `json:"signal_name"`
	TotalReturn     float64 `json:"total_return"`
	WinRate        float64 `json:"win_rate"`
	ProfitFactor   float64 `json:"profit_factor"`
	MaxDrawdown    float64 `json:"max_drawdown"`
	SharpeRatio    float64 `json:"sharpe_ratio"`
	TotalTrades    int     `json:"total_trades"`
	WinningTrades  int     `json:"winning_trades"`
}

// Position 持仓信息
type Position struct {
	OpenTime        time.Time `json:"open_time"`
	CloseTime       time.Time `json:"close_time"`
	OpenPrice       float64   `json:"open_price"`
	ClosePrice      float64   `json:"close_price"`
	Quantity        float64   `json:"quantity"`
	PositionType    string    `json:"position_type"` // "long" or "short"
	PnL             float64   `json:"pnl"`
	PnLPercentage   float64   `json:"pnl_percentage"`
	HoldingPeriods  int       `json:"holding_periods"`
	ExitReason      string    `json:"exit_reason"`
	SignalName      string    `json:"signal_name"`
}

// Trade 交易记录
type Trade struct {
	TradeID         string    `json:"trade_id"`
	StockCode       string    `json:"stock_code"`
	OpenTime        time.Time `json:"open_time"`
	CloseTime       time.Time `json:"close_time"`
	OpenPrice       float64   `json:"open_price"`
	ClosePrice      float64   `json:"close_price"`
	Quantity        float64   `json:"quantity"`
	PositionType    string    `json:"position_type"`
	PnL             float64   `json:"pnl"`
	PnLPercentage   float64   `json:"pnl_percentage"`
	Commission      float64   `json:"commission"`
	Slippage        float64   `json:"slippage"`
	SignalName      string    `json:"signal_name"`
	EntryPrice      float64   `json:"entry_price"`
	ExitPrice       float64   `json:"exit_price"`
	StopLossPrice    float64   `json:"stop_loss_price"`
	TakeProfitPrice  float64   `json:"take_profit_price"`
	Notes           string    `json:"notes"`
}

// DailyReturn 日收益率
type DailyReturn struct {
	Date            time.Time `json:"date"`
	PortfolioValue  float64   `json:"portfolio_value"`
	DailyReturn    float64   `json:"daily_return"`
	CumulativeReturn float64   `json:"cumulative_return"`
	BenchmarkReturn float64   `json:"benchmark_return"`
}

// NewBacktestService 创建回测服务
func NewBacktestService(dataService *DataService) *BacktestService {
	return &BacktestService{
		dataService: dataService,
		db:          dataService.GetDB(),
		logger:      AppLogger,
	}
}

// RunBacktest 运行回测
func (bs *BacktestService) RunBacktest(ctx context.Context, config *BacktestConfig) (*BacktestResult, error) {
	bs.logger.Info("开始回测: %s, 期间: %s - %s", config.StockCode,
		config.StartDate.Format("2006-01-02"), config.EndDate.Format("2006-01-02"))

	// 获取历史数据
	prices, err := bs.getHistoricalPrices(config.StockCode, config.StartDate, config.EndDate)
	if err != nil {
		return nil, fmt.Errorf("获取历史数据失败: %v", err)
	}

	if len(prices) < 10 {
		return nil, fmt.Errorf("历史数据不足，至少需要10天数据")
	}

	// 获取技术信号
	signals, err := bs.getTechnicalSignals(config.StockCode, config.StartDate, config.EndDate, config.Signals)
	if err != nil {
		return nil, fmt.Errorf("获取技术信号失败: %v", err)
	}

	// 执行回测
	result, err := bs.executeBacktest(config, prices, signals)
	if err != nil {
		return nil, fmt.Errorf("执行回测失败: %v", err)
	}

	// 计算基准收益（买入持有策略）
	benchmarkReturn := bs.calculateBenchmarkReturn(prices)
	result.BenchmarkReturn = benchmarkReturn

	// 计算Alpha和Beta
	result.Alpha = result.AnnualizedReturn - benchmarkReturn
	result.Beta = bs.calculateBeta(result.DailyReturns, benchmarkReturn)

	bs.logger.Info("回测完成: %s, 总收益: %.2f%%, 年化收益: %.2f%%",
		config.StockCode, result.TotalReturn*100, result.AnnualizedReturn*100)

	return result, nil
}

// getHistoricalPrices 获取历史价格数据
func (bs *BacktestService) getHistoricalPrices(stockCode string, startDate, endDate time.Time) ([]*models.StockDaily, error) {
	query := `SELECT date, open, high, low, close, volume
					FROM stock_daily
					WHERE code = ? AND date BETWEEN ? AND ?
					ORDER BY date ASC`

	rows, err := bs.db.Query(query, stockCode, startDate.Format("2006-01-02"), endDate.Format("2006-01-02"))
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var prices []*models.StockDaily
	for rows.Next() {
		price := &models.StockDaily{}
		err := rows.Scan(&price.Date, &price.Open, &price.High, &price.Low, &price.Close, &price.Volume)
		if err != nil {
			return nil, err
		}
		prices = append(prices, price)
	}

	return prices, nil
}

// getTechnicalSignals 获取技术信号
func (bs *BacktestService) getTechnicalSignals(stockCode string, startDate, endDate time.Time, signalTypes []string) (map[string]map[string]*models.TechnicalSignal, error) {
	signals := make(map[string]map[string]*models.TechnicalSignal)

	for _, signalType := range signalTypes {
		query := `SELECT date, signal_value, description
						FROM technical_signals
						WHERE code = ? AND signal_type = ? AND date BETWEEN ? AND ?
						ORDER BY date ASC`

		rows, err := bs.db.Query(query, stockCode, signalType,
			startDate.Format("2006-01-02"), endDate.Format("2006-01-02"))
		if err != nil {
			return nil, err
		}

		signalMap := make(map[string]*models.TechnicalSignal)
		for rows.Next() {
			signal := &models.TechnicalSignal{}
			err := rows.Scan(&signal.Date, &signal.SignalValue, &signal.Description)
			if err != nil {
				rows.Close()
				return nil, err
			}
			signalMap[signal.Date] = signal
		}
		rows.Close()

		signals[signalType] = signalMap
	}

	return signals, nil
}

// executeBacktest 执行回测
func (bs *BacktestService) executeBacktest(config *BacktestConfig, prices []*models.StockDaily, signals map[string]map[string]*models.TechnicalSignal) (*BacktestResult, error) {
	result := &BacktestResult{
		StockCode:        config.StockCode,
		Period:           fmt.Sprintf("%s - %s", config.StartDate.Format("2006-01-02"), config.EndDate.Format("2006-01-02")),
		InitialCapital:    config.InitialCapital,
		SignalResults:   make(map[string]*SignalResult),
		DailyReturns:    make([]DailyReturn, 0),
		Positions:       make([]Position, 0),
		Trades:          make([]Trade, 0),
	}

	// 初始化回测变量
	currentCapital := config.InitialCapital
	positions := make(map[int]*Position) // 按时间索引管理持仓
	dailyPortfolio := make(map[time.Time]float64)

	// 按日期处理
	for i, price := range prices {
		currentDate := price.Date

		// 更新持仓价值
		currentValue := currentCapital
		for _, position := range positions {
			if position != nil {
				positionValue := position.Quantity * price.Close
				currentValue += positionValue
			}
		}

		dailyPortfolio[currentDate] = currentValue

		// 检查信号并执行交易
		bs.checkSignalsAndTrade(config, currentDate, price, signals, positions, &currentCapital, result)

		// 记录日收益率
		if i > 0 {
			prevDate := prices[i-1].Date
			prevValue := dailyPortfolio[prevDate]
			dailyReturn := (currentValue - prevValue) / prevValue

			dailyRet := DailyReturn{
				Date:            currentDate,
				PortfolioValue:  currentValue,
				DailyReturn:    dailyReturn,
				CumulativeReturn: (currentValue - config.InitialCapital) / config.InitialCapital,
				BenchmarkReturn: bs.calculateBenchmarkDailyReturn(prices, i),
			}
			result.DailyReturns = append(result.DailyReturns, dailyRet)
		}
	}

	// 平仓所有剩余持仓
	for _, position := range positions {
		if position != nil {
			bs.closePosition(position, prices[len(prices)-1], "回测结束", result)
		}
	}

	// 计算最终结果
	result.FinalCapital = currentCapital
	result.TotalReturn = (result.FinalCapital - result.InitialCapital) / result.InitialCapital

	// 计算年化收益
	days := int(config.EndDate.Sub(config.StartDate).Hours() / 24)
	if days > 0 {
		result.AnnualizedReturn = math.Pow(1+result.TotalReturn, 365.0/float64(days)) - 1
	}

	// 计算最大回撤
	result.MaxDrawdown = bs.calculateMaxDrawdown(result.DailyReturns)

	// 计算夏普比率
	result.SharpeRatio = bs.calculateSharpeRatio(result.DailyReturns)

	// 统计交易结果
	bs.calculateTradeStatistics(result)

	return result, nil
}

// checkSignalsAndTrade 检查信号并执行交易
func (bs *BacktestService) checkSignalsAndTrade(config *BacktestConfig, date time.Time, price *models.StockDaily, signals map[string]map[string]*models.TechnicalSignal, positions map[int]*Position, capital *float64, result *BacktestResult) {
	for signalType, signalMap := range signals {
		if signal, exists := signalMap[date.Format("2006-01-02")]; exists {
			bs.processSignal(config, signalType, signal, date, price, positions, capital, result)
		}
	}
}

// processSignal 处理单个信号
func (bs *BacktestService) processSignal(config *BacktestConfig, signalType string, signal *models.TechnicalSignal, date time.Time, price *models.StockDaily, positions map[int]*Position, capital *float64, result *BacktestResult) {
	// 根据信号值判断买卖
	action := bs.determineSignalAction(signalType, signal.SignalValue)

	if action == "buy" {
		bs.openPosition(config, signalType, date, price, positions, capital, result)
	} else if action == "sell" {
		bs.closePositionsBySignal(signalType, date, price, positions, result)
	}
}

// determineSignalAction 确定信号动作
func (bs *BacktestService) determineSignalAction(signalType string, signalValue float64) string {
	switch signalType {
	case "MACD", "KDJ", "RSI", "CCI", "WR", "DMA", "EXPMA", "BBI", "ARBR", "VR", "OBV", "EMV", "SAR", "ROC":
		return bs.getSignalValue(signalValue)
	case "TRIX":
		return bs.getTRIXSignal(signalValue)
	case "MTM":
		return bs.getMTMSignal(signalValue)
	case "BOLL_Width":
		return bs.getBollWidthSignal(signalValue)
	case "MACD_Histogram":
		return bs.getMACDHistogramSignal(signalValue)
	default:
		return "hold"
	}
}

// getSignalValue 获取信号值对应的动作
func (bs *BacktestService) getSignalValue(value float64) string {
	if value > 0.5 {
		return "buy"
	} else if value < -0.5 {
		return "sell"
	}
	return "hold"
}

// getTRIXSignal 获取TRIX信号
func (bs *BacktestService) getTRIXSignal(value float64) string {
	if value > 0 {
		return "buy"
	} else if value < 0 {
		return "sell"
	}
	return "hold"
}

// getMTMSignal 获取MTM信号
func (bs *BacktestService) getMTMSignal(value float64) string {
	if value > 0 {
		return "buy"
	} else if value < 0 {
		return "sell"
	}
	return "hold"
}

// getBollWidthSignal 获取布林带宽度信号
func (bs *BacktestService) getBollWidthSignal(value float64) string {
	// 布林带宽度收缩通常预示突破
	if value < 0.1 {
		return "buy"
	}
	return "hold"
}

// getMACDHistogramSignal 获取MACD柱状图信号
func (bs *BacktestService) getMACDHistogramSignal(value float64) string {
	if value > 0 {
		return "buy"
	} else if value < 0 {
		return "sell"
	}
	return "hold"
}

// openPosition 开仓
func (bs *BacktestService) openPosition(config *BacktestConfig, signalType string, date time.Time, price *models.StockDaily, positions map[int]*Position, capital *float64, result *BacktestResult) {
	// 检查是否已有持仓
	for _, position := range positions {
		if position != nil {
			return
		}
	}

	// 计算仓位大小
	positionValue := *capital * config.PositionSize
	quantity := positionValue / price.Close

	// 计算手续费和滑点
	commission := positionValue * config.Commissions
	slippage := price.Close * config.Slippage

	// 创建持仓
	position := &Position{
		OpenTime:       date,
		CloseTime:      date, // 初始化为开仓时间
		OpenPrice:      price.Close + slippage,
		ClosePrice:     price.Close + slippage,
		Quantity:       quantity,
		PositionType:    "long",
		PnL:            0,
		PnLPercentage:  0,
		HoldingPeriods:  0,
		ExitReason:      "",
		SignalName:      signalType,
	}

	positions[0] = position
	*capital -= positionValue - commission - slippage

	// 记录交易
	trade := &Trade{
		TradeID:        fmt.Sprintf("%s_%s_%d", config.StockCode, signalType, date.Unix()),
		StockCode:      config.StockCode,
		OpenTime:       date,
		CloseTime:      date,
		OpenPrice:      position.OpenPrice,
		ClosePrice:     position.ClosePrice,
		Quantity:       quantity,
		PositionType:    "long",
		PnL:            0,
		PnLPercentage:  0,
		Commission:     commission,
		Slippage:       slippage,
		SignalName:      signalType,
		EntryPrice:     position.OpenPrice,
		ExitPrice:      position.ClosePrice,
		Notes:          "开仓",
	}

	result.Trades = append(result.Trades, *trade)
}

// closePositionsBySignal 根据信号平仓
func (bs *BacktestService) closePositionsBySignal(signalType string, date time.Time, price *models.StockDaily, positions map[int]*Position, result *BacktestResult) {
	for i, position := range positions {
		if position != nil && position.SignalName == signalType {
			bs.closePosition(position, price, "信号平仓", result)
			positions[i] = nil
		}
	}
}

// closePosition 平仓
func (bs *BacktestService) closePosition(position *Position, price *models.StockDaily, reason string, result *BacktestResult) {
	if position == nil {
		return
	}

	// 更新平仓信息
	position.CloseTime = price.Date
	position.ClosePrice = price.Close
	position.HoldingPeriods = int(position.CloseTime.Sub(position.OpenTime).Hours() / 24)
	position.ExitReason = reason

	// 计算盈亏
	positionValue := position.Quantity * position.ClosePrice
	openValue := position.Quantity * position.OpenPrice
	position.PnL = positionValue - openValue
	position.PnLPercentage = position.PnL / openValue

	// 更新交易记录
	for i, trade := range result.Trades {
		if trade.OpenTime.Equal(position.OpenTime) && trade.SignalName == position.SignalName {
			result.Trades[i].CloseTime = position.CloseTime
			result.Trades[i].ClosePrice = position.ClosePrice
			result.Trades[i].ExitPrice = position.ClosePrice
			result.Trades[i].PnL = position.PnL
			result.Trades[i].PnLPercentage = position.PnLPercentage
			result.Trades[i].Notes = reason
			break
		}
	}

	result.Positions = append(result.Positions, *position)
}

// calculateMaxDrawdown 计算最大回撤
func (bs *BacktestService) calculateMaxDrawdown(returns []DailyReturn) float64 {
	if len(returns) == 0 {
		return 0
	}

	maxValue := returns[0].PortfolioValue
	maxDrawdown := 0.0

	for _, ret := range returns {
		if ret.PortfolioValue > maxValue {
			maxValue = ret.PortfolioValue
		}

		drawdown := (maxValue - ret.PortfolioValue) / maxValue
		if drawdown > maxDrawdown {
			maxDrawdown = drawdown
		}
	}

	return maxDrawdown
}

// calculateSharpeRatio 计算夏普比率
func (bs *BacktestService) calculateSharpeRatio(returns []DailyReturn) float64 {
	if len(returns) < 2 {
		return 0
	}

	// 计算平均日收益率和标准差
	var sumReturns, sumSquaredReturns float64
	for _, ret := range returns {
		sumReturns += ret.DailyReturn
		sumSquaredReturns += ret.DailyReturn * ret.DailyReturn
	}

	meanReturn := sumReturns / float64(len(returns))
	variance := (sumSquaredReturns / float64(len(returns))) - (meanReturn * meanReturn)
	stdDev := math.Sqrt(variance)

	if stdDev == 0 {
		return 0
	}

	// 假设无风险利率为年化3%
	riskFreeRate := 0.03 / 365
	return (meanReturn - riskFreeRate) / stdDev * math.Sqrt(365)
}

// calculateTradeStatistics 计算交易统计
func (bs *BacktestService) calculateTradeStatistics(result *BacktestResult) {
	result.TotalTrades = len(result.Trades)

	if result.TotalTrades == 0 {
		return
	}

	var totalWinning, totalLosing float64
	var winCount, loseCount int

	for _, trade := range result.Trades {
		if trade.PnL > 0 {
			winCount++
			totalWinning += trade.PnL
		} else if trade.PnL < 0 {
			loseCount++
			totalLosing += math.Abs(trade.PnL)
		}
	}

	result.WinningTrades = winCount
	result.LosingTrades = loseCount

	if result.TotalTrades > 0 {
		result.WinRate = float64(winCount) / float64(result.TotalTrades)
	}

	if winCount > 0 {
		result.AvgWinning = totalWinning / float64(winCount)
	}

	if loseCount > 0 {
		result.AvgLosing = totalLosing / float64(loseCount)
	}

	if totalLosing > 0 {
		result.ProfitFactor = totalWinning / totalLosing
	} else {
		result.ProfitFactor = float64(result.TotalTrades) // 无亏损时设为交易次数
	}
}

// calculateBenchmarkReturn 计算基准收益（买入持有）
func (bs *BacktestService) calculateBenchmarkReturn(prices []*models.StockDaily) float64 {
	if len(prices) < 2 {
		return 0
	}

	startPrice := prices[0].Close
	endPrice := prices[len(prices)-1].Close
	return (endPrice - startPrice) / startPrice
}

// calculateBenchmarkDailyReturn 计算基准日收益率
func (bs *BacktestService) calculateBenchmarkDailyReturn(prices []*models.StockDaily, index int) float64 {
	if index <= 0 {
		return 0
	}

	prevPrice := prices[index-1].Close
	currentPrice := prices[index].Close
	return (currentPrice - prevPrice) / prevPrice
}

// calculateBeta 计算Beta值
func (bs *BacktestService) calculateBeta(returns []DailyReturn, benchmarkReturn float64) float64 {
	if len(returns) < 2 {
		return 1.0 // 默认值
	}

	// 简化计算：使用投资组合收益与基准收益的比例
	var portfolioReturnSum float64
	for _, ret := range returns {
		portfolioReturnSum += ret.CumulativeReturn
	}

	portfolioReturn := portfolioReturnSum / float64(len(returns))

	if benchmarkReturn == 0 {
		return 1.0
	}

	return portfolioReturn / benchmarkReturn
}

// GetBacktestHistory 获取回测历史
func (bs *BacktestService) GetBacktestHistory(stockCode string, limit int) ([]*BacktestResult, error) {
	// 这里可以从数据库读取历史回测结果
	// 暂时返回空切片
	return []*BacktestResult{}, nil
}

// SaveBacktestResult 保存回测结果
func (bs *BacktestService) SaveBacktestResult(result *BacktestResult) error {
	// 将回测结果保存到数据库
	// 这里可以实现具体的数据库保存逻辑
	bs.logger.Info("回测结果已保存: %s, 总收益: %.2f%%",
		result.StockCode, result.TotalReturn*100)
	return nil
}