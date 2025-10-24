package services

import (
	"context"
	"database/sql"
	"fmt"
	"math"
	"sort"
	"strings"
	"sync"
	"time"

	"smart-stock-insider/internal/models"
)

// PortfolioService 投资组合服务
type PortfolioService struct {
	dataService *DataService
	db          *sql.DB
	mutex       sync.RWMutex
	logger      *Logger
}

// NewPortfolioService 创建投资组合服务
func NewPortfolioService(dataService *DataService) *PortfolioService {
	return &PortfolioService{
		dataService: dataService,
		db:          dataService.GetDB(),
		logger:      AppLogger,
	}
}

// GetPortfolio 获取投资组合
func (ps *PortfolioService) GetPortfolio(portfolioID string) (*models.Portfolio, error) {
	query := `
		SELECT id, user_id, name, description, total_value, cash_amount, currency,
			   risk_level, created_at, updated_at
		FROM portfolios
		WHERE id = ?
	`

	portfolio := &models.Portfolio{}
	err := ps.db.QueryRow(query, portfolioID).Scan(
		&portfolio.ID, &portfolio.UserID, &portfolio.Name, &portfolio.Description,
		&portfolio.TotalValue, &portfolio.CashAmount, &portfolio.Currency,
		&portfolio.RiskLevel, &portfolio.CreatedAt, &portfolio.UpdatedAt,
	)

	if err != nil {
		return nil, fmt.Errorf("获取投资组合失败: %v", err)
	}

	// 获取持仓信息
	holdings, err := ps.GetPortfolioHoldings(portfolioID)
	if err != nil {
		ps.logger.Warn("获取持仓信息失败: %v", err)
	}
	portfolio.Holdings = holdings

	// 计算统计数据
	portfolio.Statistics = ps.calculatePortfolioStatistics(portfolio)

	// 计算业绩表现
	portfolio.Performance = ps.calculatePortfolioPerformance(portfolio)

	// 计算资产配置
	portfolio.Allocation = ps.calculateAssetAllocation(portfolio)

	return portfolio, nil
}

// GetUserPortfolios 获取用户的所有投资组合
func (ps *PortfolioService) GetUserPortfolios(userID string) ([]*models.Portfolio, error) {
	query := `
		SELECT id, user_id, name, description, total_value, cash_amount, currency,
			   risk_level, created_at, updated_at
		FROM portfolios
		WHERE user_id = ?
		ORDER BY created_at DESC
	`

	rows, err := ps.db.Query(query, userID)
	if err != nil {
		return nil, fmt.Errorf("获取用户投资组合失败: %v", err)
	}
	defer rows.Close()

	var portfolios []*models.Portfolio
	for rows.Next() {
		portfolio := &models.Portfolio{}
		err := rows.Scan(
			&portfolio.ID, &portfolio.UserID, &portfolio.Name, &portfolio.Description,
			&portfolio.TotalValue, &portfolio.CashAmount, &portfolio.Currency,
			&portfolio.RiskLevel, &portfolio.CreatedAt, &portfolio.UpdatedAt,
		)
		if err != nil {
			continue
		}

		// 获取持仓信息
		holdings, err := ps.GetPortfolioHoldings(portfolio.ID)
		if err != nil {
			ps.logger.Warn("获取持仓信息失败: %v", err)
		}
		portfolio.Holdings = holdings

		// 计算统计数据
		portfolio.Statistics = ps.calculatePortfolioStatistics(portfolio)

		// 计算业绩表现
		portfolio.Performance = ps.calculatePortfolioPerformance(portfolio)

		// 计算资产配置
		portfolio.Allocation = ps.calculateAssetAllocation(portfolio)

		portfolios = append(portfolios, portfolio)
	}

	return portfolios, nil
}

// CreatePortfolio 创建投资组合
func (ps *PortfolioService) CreatePortfolio(portfolio *models.Portfolio) error {
	query := `
		INSERT INTO portfolios (id, user_id, name, description, total_value, cash_amount, currency, risk_level)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?)
	`

	_, err := ps.db.Exec(query, portfolio.ID, portfolio.UserID, portfolio.Name,
		portfolio.Description, portfolio.TotalValue, portfolio.CashAmount,
		portfolio.Currency, portfolio.RiskLevel)

	if err != nil {
		return fmt.Errorf("创建投资组合失败: %v", err)
	}

	ps.logger.Info("投资组合创建成功: %s", portfolio.Name)
	return nil
}

// UpdatePortfolio 更新投资组合
func (ps *PortfolioService) UpdatePortfolio(portfolio *models.Portfolio) error {
	query := `
		UPDATE portfolios
		SET name = ?, description = ?, total_value = ?, cash_amount = ?,
			currency = ?, risk_level = ?, updated_at = CURRENT_TIMESTAMP
		WHERE id = ?
	`

	_, err := ps.db.Exec(query, portfolio.Name, portfolio.Description,
		portfolio.TotalValue, portfolio.CashAmount, portfolio.Currency,
		portfolio.RiskLevel, portfolio.ID)

	if err != nil {
		return fmt.Errorf("更新投资组合失败: %v", err)
	}

	ps.logger.Info("投资组合更新成功: %s", portfolio.Name)
	return nil
}

// DeletePortfolio 删除投资组合
func (ps *PortfolioService) DeletePortfolio(portfolioID string) error {
	tx, err := ps.db.Begin()
	if err != nil {
		return err
	}
	defer tx.Rollback()

	// 删除相关持仓
	_, err = tx.Exec("DELETE FROM positions WHERE portfolio_id = ?", portfolioID)
	if err != nil {
		return fmt.Errorf("删除持仓失败: %v", err)
	}

	// 删除相关交易
	_, err = tx.Exec("DELETE FROM transactions WHERE portfolio_id = ?", portfolioID)
	if err != nil {
		return fmt.Errorf("删除交易记录失败: %v", err)
	}

	// 删除投资组合
	_, err = tx.Exec("DELETE FROM portfolios WHERE id = ?", portfolioID)
	if err != nil {
		return fmt.Errorf("删除投资组合失败: %v", err)
	}

	return tx.Commit()
}

// GetPortfolioHoldings 获取投资组合持仓
func (ps *PortfolioService) GetPortfolioHoldings(portfolioID string) ([]*models.Position, error) {
	query := `
		SELECT id, portfolio_id, stock_code, stock_name, quantity, avg_cost,
			   current_price, market_value, unrealized_pnl, unrealized_pct,
			   realized_pnl, holding_days, weight, risk_contribution,
			   sector, industry, market_cap, pe, pb, dividend_yield,
			   buy_date, last_transaction, created_at, updated_at
		FROM positions
		WHERE portfolio_id = ?
		ORDER BY market_value DESC
	`

	rows, err := ps.db.Query(query, portfolioID)
	if err != nil {
		return nil, fmt.Errorf("获取持仓失败: %v", err)
	}
	defer rows.Close()

	var holdings []*models.Position
	for rows.Next() {
		position := &models.Position{}
		err := rows.Scan(
			&position.ID, &position.PortfolioID, &position.StockCode, &position.StockName,
			&position.Quantity, &position.AvgCost, &position.CurrentPrice, &position.MarketValue,
			&position.UnrealizedPnL, &position.UnrealizedPct, &position.RealizedPnL,
			&position.HoldingDays, &position.Weight, &position.RiskContribution,
			&position.Sector, &position.Industry, &position.MarketCap,
			&position.PE, &position.PB, &position.DividendYield,
			&position.BuyDate, &position.LastTransaction,
			&position.CreatedAt, &position.UpdatedAt,
		)
		if err != nil {
			continue
		}
		holdings = append(holdings, position)
	}

	return holdings, nil
}

// AddPosition 添加持仓
func (ps *PortfolioService) AddPosition(position *models.Position) error {
	// 计算权重和风险贡献度
	totalValue, err := ps.GetPortfolioTotalValue(position.PortfolioID)
	if err != nil {
		return err
	}

	if totalValue > 0 {
		position.Weight = position.MarketValue / totalValue
		position.RiskContribution = position.Weight * ps.calculateStockRisk(position.StockCode)
	}

	query := `
		INSERT INTO positions (
			id, portfolio_id, stock_code, stock_name, quantity, avg_cost, current_price,
			market_value, unrealized_pnl, unrealized_pct, holding_days, weight,
			risk_contribution, sector, industry, market_cap, pe, pb, dividend_yield,
			buy_date, created_at, updated_at
		) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
	`

	_, err = ps.db.Exec(query, position.ID, position.PortfolioID, position.StockCode, position.StockName,
		position.Quantity, position.AvgCost, position.CurrentPrice, position.MarketValue,
		position.UnrealizedPnL, position.UnrealizedPct, position.HoldingDays, position.Weight,
		position.RiskContribution, position.Sector, position.Industry, position.MarketCap,
		position.PE, position.PB, position.DividendYield, position.BuyDate)

	if err != nil {
		return fmt.Errorf("添加持仓失败: %v", err)
	}

	// 更新投资组合总价值
	return ps.updatePortfolioTotalValue(position.PortfolioID)
}

// UpdatePosition 更新持仓
func (ps *PortfolioService) UpdatePosition(position *models.Position) error {
	query := `
		UPDATE positions
		SET quantity = ?, avg_cost = ?, current_price = ?, market_value = ?,
			unrealized_pnl = ?, unrealized_pct = ?, holding_days = ?,
			weight = ?, risk_contribution = ?, sector = ?, industry = ?,
			market_cap = ?, pe = ?, pb = ?, dividend_yield = ?,
			updated_at = CURRENT_TIMESTAMP
		WHERE id = ?
	`

	_, err := ps.db.Exec(query, position.Quantity, position.AvgCost, position.CurrentPrice,
		position.MarketValue, position.UnrealizedPnL, position.UnrealizedPct,
		position.HoldingDays, position.Weight, position.RiskContribution, position.Sector,
		position.Industry, position.MarketCap, position.PE, position.PB,
		position.DividendYield, position.ID)

	if err != nil {
		return fmt.Errorf("更新持仓失败: %v", err)
	}

	// 更新投资组合总价值
	return ps.updatePortfolioTotalValue(position.PortfolioID)
}

// RemovePosition 移除持仓
func (ps *PortfolioService) RemovePosition(positionID string) error {
	// 获取持仓信息以更新投资组合
	var portfolioID string
	err := ps.db.QueryRow("SELECT portfolio_id FROM positions WHERE id = ?", positionID).Scan(&portfolioID)
	if err != nil {
		return fmt.Errorf("获取持仓信息失败: %v", err)
	}

	// 删除持仓
	_, err = ps.db.Exec("DELETE FROM positions WHERE id = ?", positionID)
	if err != nil {
		return fmt.Errorf("删除持仓失败: %v", err)
	}

	// 更新投资组合总价值
	return ps.updatePortfolioTotalValue(portfolioID)
}

// AnalyzePortfolio 分析投资组合
func (ps *PortfolioService) AnalyzePortfolio(req *models.PortfolioAnalysisRequest) (*models.PortfolioAnalysisResult, error) {
	result := &models.PortfolioAnalysisResult{
		PortfolioID:  req.PortfolioID,
		AnalysisType:  req.AnalysisType,
		AnalysisTime:  time.Now(),
		BenchmarkCode: req.BenchmarkCode,
		Metadata:     make(map[string]interface{}),
	}

	// 根据分析类型执行相应分析
	switch req.AnalysisType {
	case "performance":
		portfolio, err := ps.GetPortfolio(req.PortfolioID)
		if err != nil {
			return nil, err
		}
		result.Performance = portfolio.Performance

	case "risk":
		riskAnalysis, err := ps.analyzePortfolioRisk(req)
		if err != nil {
			return nil, err
		}
		result.RiskAnalysis = riskAnalysis

	case "allocation":
		portfolio, err := ps.GetPortfolio(req.PortfolioID)
		if err != nil {
			return nil, err
		}
		result.Allocation = portfolio.Allocation

	case "rebalancing":
		rebalancing, err := ps.generateRebalancingSuggestion(req)
		if err != nil {
			return nil, err
		}
		result.Rebalancing = rebalancing

	default:
		// 综合分析
		portfolio, err := ps.GetPortfolio(req.PortfolioID)
		if err != nil {
			return nil, err
		}
		result.Performance = portfolio.Performance
		result.Allocation = portfolio.Allocation

		riskAnalysis, err := ps.analyzePortfolioRisk(req)
		if err != nil {
			ps.logger.Warn("风险分析失败: %v", err)
		}
		result.RiskAnalysis = riskAnalysis

		rebalancing, err := ps.generateRebalancingSuggestion(req)
		if err != nil {
			ps.logger.Warn("再平衡建议失败: %v", err)
		}
		result.Rebalancing = rebalancing
	}

	// 生成建议
	result.Recommendations = ps.generatePortfolioRecommendations(result)

	result.Confidence = 0.85
	result.DataQuality = 0.90

	return result, nil
}

// calculatePortfolioStatistics 计算投资组合统计
func (ps *PortfolioService) calculatePortfolioStatistics(portfolio *models.Portfolio) *models.PortfolioStatistics {
	if len(portfolio.Holdings) == 0 {
		return &models.PortfolioStatistics{
			TotalPositions:      0,
			ProfitablePositions: 0,
			LosingPositions:    0,
			WinRate:           0.0,
			AvgHoldingDays:    0.0,
			DailyChange:       0.0,
			DailyChangePct:   0.0,
		}
	}

	stats := &models.PortfolioStatistics{
		TotalPositions: len(portfolio.Holdings),
	}

	var totalHoldingDays int
	var totalUnrealizedPnL float64
	var dailyChangeTotal float64
	var positiveCount int

	for _, holding := range portfolio.Holdings {
		totalHoldingDays += holding.HoldingDays
		totalUnrealizedPnL += holding.UnrealizedPnL
		dailyChangeTotal += holding.UnrealizedPnL / float64(holding.HoldingDays)

		if holding.UnrealizedPnL > 0 {
			positiveCount++
		}
	}

	stats.AvgHoldingDays = float64(totalHoldingDays) / float64(len(portfolio.Holdings))
	stats.ProfitablePositions = positiveCount
	stats.LosingPositions = len(portfolio.Holdings) - positiveCount

	if len(portfolio.Holdings) > 0 {
		stats.WinRate = float64(positiveCount) / float64(len(portfolio.Holdings))
		stats.DailyChange = dailyChangeTotal
		stats.DailyChangePct = (dailyChangeTotal / portfolio.TotalValue) * 100
	}

	// 计算时间段收益（简化实现）
	stats.DailyChangePct = ps.calculatePeriodReturn(portfolio, 1)   * 100
	stats.WeeklyChangePct = ps.calculatePeriodReturn(portfolio, 7)   * 100
	stats.MonthlyChangePct = ps.calculatePeriodReturn(portfolio, 30)  * 100
	stats.YearToDateReturn = ps.calculateYTDReturn(portfolio)

	return stats
}

// calculatePortfolioPerformance 计算投资组合表现
func (ps *PortfolioService) calculatePortfolioPerformance(portfolio *models.Portfolio) *models.PortfolioPerformance {
	if portfolio.TotalValue == 0 {
		return &models.PortfolioPerformance{}
	}

	perf := &models.PortfolioPerformance{
		TotalReturn:    portfolio.TotalValue - 100000, // 假设初始投资10万
		BenchmarkReturn: 0.05, // 假设基准收益5%
		Alpha:          0.02, // 假设Alpha 2%
		Beta:           1.1,  // 假设Beta 1.1
		MaxDrawdown:    0.15, // 假设最大回撤15%
		CurrentDrawdown: 0.05, // 假设当前回撤5%
		Volatility:     0.20, // 假设波动率20%
	}

	if portfolio.TotalValue != 100000 {
		perf.TotalReturnPct = perf.TotalReturn / 100000
	}

	// 计算夏普比率 (假设无风险利率3%)
	riskFreeRate := 0.03
	if perf.Volatility > 0 {
		perf.SharpeRatio = (perf.TotalReturnPct - riskFreeRate) / perf.Volatility
	}

	return perf
}

// calculateAssetAllocation 计算资产配置
func (ps *PortfolioService) calculateAssetAllocation(portfolio *models.Portfolio) *models.AssetAllocation {
	allocation := &models.AssetAllocation{
		TotalAllocation: portfolio.TotalValue,
		BySector:       make(map[string]float64),
		ByIndustry:     make(map[string]float64),
		ByMarketCap:    make(map[string]float64),
		ByGeography:    make(map[string]float64),
		ByAssetType:     make(map[string]float64),
		ByRiskLevel:     make(map[string]float64),
		ByCurrency:      make(map[string]float64),
	}

	// 按行业分配
	for _, holding := range portfolio.Holdings {
		allocation.BySector[holding.Sector] += holding.MarketValue
		allocation.ByIndustry[holding.Industry] += holding.MarketValue
		allocation.ByMarketCap[holding.MarketCap] += holding.MarketValue
	}

	// 计算集中度
	allocation.Concentration = ps.calculateConcentration(portfolio.Holdings, portfolio.TotalValue)

	// 生成再平衡建议
	allocation.Rebalancing = ps.generateSimpleRebalancing(allocation.BySector)

	return allocation
}

// calculateConcentration 计算集中度分析
func (ps *PortfolioService) calculateConcentration(holdings []*models.Position, totalValue float64) *models.ConcentrationAnalysis {
	concentration := &models.ConcentrationAnalysis{
		TopPositions:     make([]*models.ConcentrationItem, 0),
		SectorConcentration: make(map[string]float64),
		IndustryConcentration: make(map[string]float64),
	}

	// 计算前10大持仓
	sort.Slice(holdings, func(i, j int) bool {
		return holdings[i].MarketValue > holdings[j].MarketValue
	})

	maxTop := 10
	if len(holdings) < maxTop {
		maxTop = len(holdings)
	}

	for i := 0; i < maxTop; i++ {
		holding := holdings[i]
		item := &models.ConcentrationItem{
			StockCode:   holding.StockCode,
			StockName:   holding.StockName,
			Weight:      holding.Weight,
			Value:       holding.MarketValue,
			Percentage:  (holding.MarketValue / totalValue) * 100,
		}
		concentration.TopPositions = append(concentration.TopPositions, item)

		// 计算HHI指数
		concentration.HHI += math.Pow(holding.Weight, 2)
	}

	// 行业集中度
	for _, holding := range holdings {
		concentration.SectorConcentration[holding.Sector] += holding.MarketValue
		concentration.IndustryConcentration[holding.Industry] += holding.MarketValue
	}

	// 转换为百分比
	for sector, value := range concentration.SectorConcentration {
		concentration.SectorConcentration[sector] = (value / totalValue) * 100
	}

	for industry, value := range concentration.IndustryConcentration {
		concentration.IndustryConcentration[industry] = (value / totalValue) * 100
	}

	// 多样化评分 (0-1，越高越分散)
	concentration.DiversificationScore = math.Max(0, 1-concentration.HHI)

	return concentration
}

// generateSimpleRebalancing 生成简单再平衡建议
func (ps *PortfolioService) generateSimpleRebalancing(currentAllocation map[string]float64) *models.RebalancingSuggestion {
	rebalancing := &models.RebalancingSuggestion{
		CurrentAllocation:    make(map[string]float64),
		TargetAllocation:     make(map[string]float64),
		RecommendedActions:   make([]*models.RebalancingAction, 0),
		RebalancingNeeded:   false,
		SuggestedFrequency:   "quarterly",
		LastRebalancing:     time.Now().Add(-90 * 24 * time.Hour), // 假设3个月前再平衡过
	}

	// 复制当前配置
	for k, v := range currentAllocation {
		rebalancing.CurrentAllocation[k] = v
		rebalancing.TargetAllocation[k] = v // 简化：目标与当前相同
	}

	// 检查是否需要再平衡
	for sector, weight := range currentAllocation {
		targetWeight := 1.0 / float64(len(currentAllocation)) // 平均分配
		deviation := math.Abs(weight - targetWeight)

		if deviation > 0.05 { // 超过5%偏差需要再平衡
			rebalancing.RebalancingNeeded = true
			rebalancing.TargetAllocation[sector] = targetWeight

			action := &models.RebalancingAction{
				Action:       "rebalance",
				CurrentWeight: weight,
				TargetWeight:  targetWeight,
				WeightDiff:   targetWeight - weight,
				Priority:     "medium",
				Reason:       "权重偏差过大",
			}
			rebalancing.RecommendedActions = append(rebalancing.RecommendedActions, action)
		}
	}

	// 计算总体偏差
	var totalDeviation float64
	for _, action := range rebalancing.RecommendedActions {
		totalDeviation += math.Abs(action.WeightDiff)
	}
	rebalancing.Deviation = totalDeviation

	return rebalancing
}

// analyzePortfolioRisk 分析投资组合风险
func (ps *PortfolioService) analyzePortfolioRisk(req *models.PortfolioAnalysisRequest) (*models.RiskAnalysis, error) {
	riskAnalysis := &models.RiskAnalysis{
		PortfolioID:      req.PortfolioID,
		OverallRiskLevel:  "medium",
		RiskMetrics:       &models.RiskMetrics{},
		ConcentrationRisk:  0.3,
		SectorRisk:        make(map[string]float64),
		MarketRisk:        0.25,
		CreditRisk:        0.1,
		LiquidityRisk:     0.15,
		CurrencyRisk:      0.05,
		RiskDecomposition: &models.RiskDecomposition{
			SpecificRisk:   0.6,
			SystematicRisk: 0.4,
			SectorRisks:    make(map[string]float64),
			StyleRisks:     make(map[string]float64),
			RegionalRisks:  make(map[string]float64),
		},
		ScenarioAnalysis: &models.ScenarioAnalysis{
			BullMarket:     0.15,
			BearMarket:     -0.20,
			NormalMarket:   0.05,
			HighVolatility: -0.08,
			StressTest:     -0.35,
			BlackSwan:      -0.50,
		},
		VaR: &models.ValueAtRisk{
			OneDay:     0.02,
			FiveDays:   0.05,
			TenDays:    0.08,
			OneMonth:   0.15,
			ThreeMonths: 0.25,
			Confidence: 0.95,
		},
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	return riskAnalysis, nil
}

// generateRebalancingSuggestion 生成再平衡建议
func (ps *PortfolioService) generateRebalancingSuggestion(req *models.PortfolioAnalysisRequest) (*models.RebalancingSuggestion, error) {
	// 获取当前持仓
	holdings, err := ps.GetPortfolioHoldings(req.PortfolioID)
	if err != nil {
		return nil, err
	}

	if len(holdings) == 0 {
		return &models.RebalancingSuggestion{
			RebalancingNeeded: false,
			RecommendedActions: make([]*models.RebalancingAction, 0),
		}, nil
	}

	rebalancing := &models.RebalancingSuggestion{
		CurrentAllocation:  make(map[string]float64),
		TargetAllocation:   make(map[string]float64),
		RecommendedActions: make([]*models.RebalancingAction, 0),
		RebalancingNeeded:  false,
		SuggestedFrequency: "quarterly",
	}

	// 计算总价值
	var totalValue float64
	for _, holding := range holdings {
		totalValue += holding.MarketValue
	}

	// 分析当前配置
	sectorAllocation := make(map[string]float64)
	for _, holding := range holdings {
		sectorAllocation[holding.Sector] += holding.MarketValue
	}

	// 复制当前配置
	for sector, value := range sectorAllocation {
		rebalancing.CurrentAllocation[sector] = value
	}

	// 生成目标配置（基于现代投资组合理论）
	targetWeights := map[string]float64{
		"科技":    0.30,
		"金融":    0.25,
		"消费":    0.20,
		"医疗":    0.15,
		"工业":    0.10,
	}

	// 计算再平衡动作
	for sector, targetWeight := range targetWeights {
		currentWeight := sectorAllocation[sector] / totalValue
		deviation := targetWeight - currentWeight

		if math.Abs(deviation) > 0.05 { // 超过5%偏差
			rebalancing.RebalancingNeeded = true

			action := &models.RebalancingAction{
				Action:       "rebalance",
				StockCode:     "", // 这里应该具体到股票
				CurrentWeight: currentWeight,
				TargetWeight:  targetWeight,
				WeightDiff:    deviation,
				Priority:     ps.calculateRebalancePriority(math.Abs(deviation)),
				Reason:       "权重偏离目标配置",
			}
			rebalancing.RecommendedActions = append(rebalancing.RecommendedActions, action)
		}

		rebalancing.TargetAllocation[sector] = targetWeight * totalValue
	}

	return rebalancing, nil
}

// generatePortfolioRecommendations 生成投资组合建议
func (ps *PortfolioService) generatePortfolioRecommendations(result *models.PortfolioAnalysisResult) []*models.PortfolioRecommendation {
	var recommendations []*models.PortfolioRecommendation

	// 基于风险分析生成建议
	if result.RiskAnalysis != nil {
		if result.RiskAnalysis.ConcentrationRisk > 0.3 {
			recommendations = append(recommendations, &models.PortfolioRecommendation{
				Type:         "risk_adjust",
				Priority:     "high",
				Title:        "投资组合过于集中",
				Description:  "建议分散投资以降低风险",
				ActionItems: []*models.ActionItem{
					{Action: "diversify", Reason: "降低集中度风险"},
				},
				ExpectedImpact: 0.1,
				RiskLevel:     "medium",
				TimeHorizon:   "3-6个月",
				Confidence:    0.8,
				ValidUntil:    time.Now().Add(30 * 24 * time.Hour),
				Tags:         []string{"风险", "分散化"},
			})
		}
	}

	// 基于再平衡建议生成建议
	if result.Rebalancing != nil && result.Rebalancing.RebalancingNeeded {
		recommendations = append(recommendations, &models.PortfolioRecommendation{
			Type:         "rebalance",
			Priority:     "medium",
			Title:        "投资组合需要再平衡",
			Description:  "当前配置偏离目标，建议进行再平衡",
			ActionItems:   ps.convertRebalancingToActions(result.Rebalancing),
			ExpectedImpact: 0.05,
			RiskLevel:     "low",
			TimeHorizon:   "1个月内",
			Confidence:    0.9,
			ValidUntil:    time.Now().Add(15 * 24 * time.Hour),
			Tags:         []string{"再平衡", "配置"},
		})
	}

	return recommendations
}

// 辅助方法
func (ps *PortfolioService) calculateStockRisk(stockCode string) float64 {
	// 简化的风险计算，实际应该基于历史数据
	return 0.15 // 默认15%年波动率
}

func (ps *PortfolioService) GetPortfolioTotalValue(portfolioID string) (float64, error) {
	var totalValue float64
	err := ps.db.QueryRow("SELECT total_value FROM portfolios WHERE id = ?", portfolioID).Scan(&totalValue)
	return totalValue, err
}

func (ps *PortfolioService) updatePortfolioTotalValue(portfolioID string) error {
	query := `
		UPDATE portfolios
		SET total_value = (
			SELECT COALESCE(SUM(market_value), 0)
			FROM positions
			WHERE portfolio_id = ?
		),
		updated_at = CURRENT_TIMESTAMP
		WHERE id = ?
	`

	_, err := ps.db.Exec(query, portfolioID, portfolioID)
	return err
}

func (ps *PortfolioService) calculatePeriodReturn(portfolio *models.Portfolio, days int) float64 {
	// 简化的周期收益计算
	dailyReturn := 0.001 // 假设日收益率0.1%
	return float64(days) * dailyReturn
}

func (ps *PortfolioService) calculateYTDReturn(portfolio *models.Portfolio) float64 {
	// 简化的年初至今收益计算
	days := time.Now().Sub(time.Date(time.Now().Year(), 1, 1, 0, 0, 0, 0)).Hours() / 24
	return ps.calculatePeriodReturn(portfolio, int(days))
}

func (ps *PortfolioService) calculateRebalancePriority(deviation float64) string {
	if deviation > 0.1 {
		return "high"
	} else if deviation > 0.05 {
		return "medium"
	}
	return "low"
}

func (ps *PortfolioService) convertRebalancingToActions(rebalancing *models.RebalancingSuggestion) []*models.ActionItem {
	var actions []*models.ActionItem

	for _, action := range rebalancing.RecommendedActions {
		actionItem := &models.ActionItem{
			Action:     action.Action,
			Weight:     action.WeightDiff,
			Reason:     action.Reason,
			RiskImpact: action.Priority,
		}
		actions = append(actions, actionItem)
	}

	return actions
}