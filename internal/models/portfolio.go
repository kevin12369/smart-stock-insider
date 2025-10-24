package models

import (
	"time"
)

// Portfolio 投资组合
type Portfolio struct {
	ID          string                 `json:"id"`
	UserID      string                 `json:"user_id"`
	Name        string                 `json:"name"`
	Description string                 `json:"description"`
	TotalValue  float64                `json:"total_value"`
	CashAmount  float64                `json:"cash_amount"`
	Currency    string                 `json:"currency"`
	RiskLevel   string                 `json:"risk_level"`    // conservative, moderate, aggressive
	CreatedAt   time.Time              `json:"created_at"`
	UpdatedAt   time.Time              `json:"updated_at"`
	Holdings    []*Position            `json:"holdings"`
	Statistics  *PortfolioStatistics   `json:"statistics"`
	Performance *PortfolioPerformance  `json:"performance"`
	Allocation  *AssetAllocation      `json:"allocation"`
}

// PortfolioStatistics 投资组合统计
type PortfolioStatistics struct {
	TotalPositions      int     `json:"total_positions"`
	ProfitablePositions int     `json:"profitable_positions"`
	LosingPositions    int     `json:"losing_positions"`
	WinRate           float64 `json:"win_rate"`
	AvgHoldingDays    float64 `json:"avg_holding_days"`
	DailyChange       float64 `json:"daily_change"`
	DailyChangePct   float64 `json:"daily_change_pct"`
	WeeklyChange      float64 `json:"weekly_change"`
	WeeklyChangePct  float64 `json:"weekly_change_pct"`
	MonthlyChange    float64 `json:"monthly_change"`
	MonthlyChangePct float64 `json:"monthly_change_pct"`
	YearToDateReturn  float64 `json:"ytd_return"`
	AnnualizedReturn  float64 `json:"annualized_return"`
}

// PortfolioPerformance 投资组合表现
type PortfolioPerformance struct {
	TotalReturn          float64 `json:"total_return"`
	TotalReturnPct       float64 `json:"total_return_pct"`
	BenchmarkReturn      float64 `json:"benchmark_return"`
	BenchmarkReturnPct   float64 `json:"benchmark_return_pct"`
	Alpha               float64 `json:"alpha"`
	Beta                float64 `json:"beta"`
	SharpeRatio         float64 `json:"sharpe_ratio"`
	SortinoRatio        float64 `json:"sortino_ratio"`
	MaxDrawdown         float64 `json:"max_drawdown"`
	CurrentDrawdown     float64 `json:"current_drawdown"`
	Volatility          float64 `json:"volatility"`
	InformationRatio     float64 `json:"information_ratio"`
	TreynorRatio        float64 `json:"treynor_ratio"`
	CalmarRatio         float64 `json:"calmar_ratio"`
	TrackingError       float64 `json:"tracking_error"`
	UpCapture          float64 `json:"up_capture"`
	DownCapture        float64 `json:"down_capture"`
}

// Position 持仓
type Position struct {
	ID              string    `json:"id"`
	PortfolioID     string    `json:"portfolio_id"`
	StockCode       string    `json:"stock_code"`
	StockName       string    `json:"stock_name"`
	Quantity        float64   `json:"quantity"`
	AvgCost         float64   `json:"avg_cost"`
	CurrentPrice    float64   `json:"current_price"`
	MarketValue     float64   `json:"market_value"`
	UnrealizedPnL   float64   `json:"unrealized_pnl"`
	UnrealizedPct    float64   `json:"unrealized_pct"`
	RealizedPnL     float64   `json:"realized_pnl"`
	HoldingDays     int       `json:"holding_days"`
	Weight          float64   `json:"weight"`         // 在组合中的权重
	RiskContribution float64   `json:"risk_contribution"` // 风险贡献度
	Sector          string    `json:"sector"`
	Industry       string    `json:"industry"`
	MarketCap       string    `json:"market_cap"`
	PE             float64   `json:"pe"`
	PB             float64   `json:"pb"`
	DividendYield  float64   `json:"dividend_yield"`
	BuyDate        time.Time `json:"buy_date"`
	LastTransaction time.Time `json:"last_transaction"`
	CreatedAt       time.Time `json:"created_at"`
	UpdatedAt       time.Time `json:"updated_at"`
}

// Transaction 交易记录
type Transaction struct {
	ID            string    `json:"id"`
	PortfolioID   string    `json:"portfolio_id"`
	PositionID    string    `json:"position_id"`
	StockCode     string    `json:"stock_code"`
	StockName     string    `json:"stock_name"`
	TransactionType string   `json:"transaction_type"` // buy, sell, dividend, split
	Quantity      float64   `json:"quantity"`
	Price         float64   `json:"price"`
	Amount        float64   `json:"amount"`
	Fee           float64   `json:"fee"`
	Tax           float64   `json:"tax"`
	Notes         string    `json:"notes"`
	ExecutedAt    time.Time `json:"executed_at"`
	CreatedAt     time.Time `json:"created_at"`
}

// AssetAllocation 资产配置
type AssetAllocation struct {
	TotalAllocation float64                      `json:"total_allocation"`
	BySector      map[string]float64            `json:"by_sector"`
	ByIndustry    map[string]float64            `json:"by_industry"`
	ByMarketCap   map[string]float64            `json:"by_market_cap"`
	ByGeography  map[string]float64            `json:"by_geography"`
	ByAssetType   map[string]float64            `json:"by_asset_type"`
	ByRiskLevel   map[string]float64            `json:"by_risk_level"`
	ByCurrency    map[string]float64            `json:"by_currency"`
	Concentration  *ConcentrationAnalysis         `json:"concentration"`
	Rebalancing   *RebalancingSuggestion       `json:"rebalancing"`
}

// ConcentrationAnalysis 集中度分析
type ConcentrationAnalysis struct {
	TopPositions       []*ConcentrationItem `json:"top_positions"`
	SectorConcentration map[string]float64   `json:"sector_concentration"`
	IndustryConcentration map[string]float64 `json:"industry_concentration"`
	HHI                float64           `json:"hhi"` // Herfindahl-Hirschman Index
	DiversificationScore float64           `json:"diversification_score"` // 0-1
}

// ConcentrationItem 集中度项
type ConcentrationItem struct {
	StockCode   string  `json:"stock_code"`
	StockName   string  `json:"stock_name"`
	Weight      float64 `json:"weight"`
	Value       float64 `json:"value"`
	Percentage  float64 `json:"percentage"`
}

// RebalancingSuggestion 再平衡建议
type RebalancingSuggestion struct {
	RecommendedActions []*RebalancingAction `json:"recommended_actions"`
	RebalancingNeeded  bool                `json:"rebalancing_needed"`
	CurrentAllocation   map[string]float64  `json:"current_allocation"`
	TargetAllocation    map[string]float64  `json:"target_allocation"`
	Deviation          float64             `json:"deviation"`
	SuggestedFrequency   string              `json:"suggested_frequency"` // monthly, quarterly, semiannually
	LastRebalancing    time.Time           `json:"last_rebalancing"`
}

// RebalancingAction 再平衡动作
type RebalancingAction struct {
	Action      string  `json:"action"`      // buy, sell, rebalance
	StockCode    string  `json:"stock_code"`
	StockName    string  `json:"stock_name"`
	CurrentWeight float64 `json:"current_weight"`
	TargetWeight  float64 `json:"target_weight"`
	WeightDiff    float64 `json:"weight_diff"`
	Amount       float64 `json:"amount"`
	Priority     string  `json:"priority"`    // high, medium, low
	Reason       string  `json:"reason"`
}

// RiskAnalysis 风险分析
type RiskAnalysis struct {
	PortfolioID           string    `json:"portfolio_id"`
	OverallRiskLevel      string    `json:"overall_risk_level"`    // low, medium, high, very_high
	RiskMetrics           *RiskMetrics `json:"risk_metrics"`
	ConcentrationRisk     float64    `json:"concentration_risk"`
	SectorRisk           map[string]float64 `json:"sector_risk"`
	MarketRisk          float64    `json:"market_risk"`
	CreditRisk          float64    `json:"credit_risk"`
	LiquidityRisk       float64    `json:"liquidity_risk"`
	CurrencyRisk        float64    `json:"currency_risk"`
	RiskDecomposition   *RiskDecomposition `json:"risk_decomposition"`
	ScenarioAnalysis     *ScenarioAnalysis `json:"scenario_analysis"`
	VaR                 *ValueAtRisk `json:"var"` // Value at Risk
	CreatedAt           time.Time   `json:"created_at"`
	UpdatedAt           time.Time   `json:"updated_at"`
}

// RiskMetrics 风险指标
type RiskMetrics struct {
	Volatility      float64 `json:"volatility"`
	Beta            float64 `json:"beta"`
	Alpha           float64 `json:"alpha"`
	SharpeRatio     float64 `json:"sharpe_ratio"`
	SortinoRatio    float64 `json:"sortino_ratio"`
	MaxDrawdown     float64 `json:"max_drawdown"`
	CurrentDrawdown float64 `json:"current_drawdown"`
	DownsideDev     float64 `json:"downside_deviation"`
	UpCapture       float64 `json:"up_capture"`
	DownCapture     float64 `json:"down_capture"`
	TrackingError   float64 `json:"tracking_error"`
	InformationRatio float64 `json:"information_ratio"`
	CalmarRatio     float64 `json:"calmar_ratio"`
}

// RiskDecomposition 风险分解
type RiskDecomposition struct {
	SpecificRisk    float64            `json:"specific_risk"`
	SystematicRisk  float64            `json:"systematic_risk"`
	SectorRisks    map[string]float64 `json:"sector_risks"`
	StyleRisks      map[string]float64 `json:"style_risks"`     // growth, value, size, momentum
	RegionalRisks   map[string]float64 `json:"regional_risks"`
}

// ScenarioAnalysis 情景分析
type ScenarioAnalysis struct {
	BullMarket      float64 `json:"bull_market"`     // +20% market return
	BearMarket      float64 `json:"bear_market"`     // -20% market return
	NormalMarket    float64 `json:"normal_market"`   // 0% market return
	HighVolatility  float64 `json:"high_volatility"` // 2x current volatility
	StressTest      float64 `json:"stress_test"`     // 2008 style crisis
	BlackSwan       float64 `json:"black_swan"`      // Extreme tail event
}

// ValueAtRisk 在险价值
type ValueAtRisk struct {
	OneDay     float64 `json:"one_day"`
	FiveDays   float64 `json:"five_days"`
	TenDays    float64 `json:"ten_days"`
	OneMonth   float64 `json:"one_month"`
	ThreeMonths float64 `json:"three_months"`
	Confidence float64 `json:"confidence"` // 95%, 99%
}

// PortfolioAnalysisRequest 投资组合分析请求
type PortfolioAnalysisRequest struct {
	PortfolioID      string    `json:"portfolio_id"`
	UserID          string    `json:"user_id"`
	AnalysisType    string    `json:"analysis_type"`  // performance, risk, allocation, rebalancing
	BenchmarkCode   string    `json:"benchmark_code"`  // 对标代码
	StartDate       time.Time `json:"start_date"`
	EndDate         time.Time `json:"end_date"`
	IncludeInactive bool      `json:"include_inactive"`
	AnalysisScope   []string  `json:"analysis_scope"`  // holdings, performance, risk, allocation
	Parameters      map[string]interface{} `json:"parameters"`
}

// PortfolioAnalysisResult 投资组合分析结果
type PortfolioAnalysisResult struct {
	PortfolioID        string                    `json:"portfolio_id"`
	AnalysisType       string                    `json:"analysis_type"`
	AnalysisTime       time.Time                 `json:"analysis_time"`
	BenchmarkCode      string                    `json:"benchmark_code"`
	Performance       *PortfolioPerformance       `json:"performance"`
	RiskAnalysis      *RiskAnalysis             `json:"risk_analysis"`
	Allocation        *AssetAllocation          `json:"allocation"`
	Rebalancing       *RebalancingSuggestion   `json:"rebalancing"`
	Recommendations   []*PortfolioRecommendation `json:"recommendations"`
	Metadata          map[string]interface{}    `json:"metadata"`
	Confidence        float64                  `json:"confidence"`
	DataQuality       float64                  `json:"data_quality"`
}

// PortfolioRecommendation 投资组合建议
type PortfolioRecommendation struct {
	Type         string    `json:"type"`         // buy, sell, hold, rebalance, risk_adjust
	Priority     string    `json:"priority"`     // high, medium, low
	Title        string    `json:"title"`
	Description  string    `json:"description"`
	ActionItems  []*ActionItem `json:"action_items"`
	ExpectedImpact float64   `json:"expected_impact"`
	RiskLevel    string    `json:"risk_level"`
	TimeHorizon  string    `json:"time_horizon"`
	Confidence   float64   `json:"confidence"`
	ValidUntil   time.Time `json:"valid_until"`
	Tags         []string  `json:"tags"`
}

// ActionItem 行动项
type ActionItem struct {
	StockCode    string  `json:"stock_code"`
	StockName    string  `json:"stock_name"`
	Action       string  `json:"action"`      // buy, sell, reduce, increase
	Quantity     float64 `json:"quantity"`
	Weight       float64 `json:"weight"`
	Reason       string  `json:"reason"`
	ExpectedPnL  float64 `json:"expected_pnl"`
	RiskImpact   string  `json:"risk_impact"`
}

// PortfolioOptimizer 投资组合优化器
type PortfolioOptimizer struct {
	ID              string    `json:"id"`
	Name            string    `json:"name"`
	Description     string    `json:"description"`
	OptimizationType string    `json:"optimization_type"` // mean_variance, equal_weight, risk_parity, max_sharpe
	Constraints     *OptimizationConstraints `json:"constraints"`
	Objectives      []string  `json:"objectives"`     // maximize_return, minimize_risk, maximize_sharpe
	CurrentWeights  map[string]float64 `json:"current_weights"`
	OptimalWeights  map[string]float64 `json:"optimal_weights"`
	ExpectedReturn   float64   `json:"expected_return"`
	ExpectedRisk    float64   `json:"expected_risk"`
	SharpeRatio     float64   `json:"sharpe_ratio"`
	OptimizationDate time.Time `json:"optimization_date"`
	CreatedAt       time.Time `json:"created_at"`
}

// OptimizationConstraints 优化约束
type OptimizationConstraints struct {
	MaxWeight       float64   `json:"max_weight"`        // 单个股票最大权重
	MinWeight       float64   `json:"min_weight"`        // 单个股票最小权重
	MaxPositions    int       `json:"max_positions"`     // 最大持仓数量
	SectorLimits    map[string]float64 `json:"sector_limits"`  // 行业限制
	BetaTarget      float64   `json:"beta_target"`       // 目标Beta
	TurnoverLimit   float64   `json:"turnover_limit"`    // 换手率限制
	TransactionCosts float64   `json:"transaction_costs"` // 交易成本
	TaxRate        float64   `json:"tax_rate"`         // 税率
}

// BacktestPortfolio 组合回测
type BacktestPortfolio struct {
	PortfolioID      string    `json:"portfolio_id"`
	BenchmarkCode    string    `json:"benchmark_code"`
	StartDate       time.Time `json:"start_date"`
	EndDate         time.Time `json:"end_date"`
	InitialValue    float64   `json:"initial_value"`
	EndingValue     float64   `json:"ending_value"`
	TotalReturn     float64   `json:"total_return"`
	AnnualizedReturn float64   `json:"annualized_return"`
	BenchmarkReturn float64   `json:"benchmark_return"`
	Alpha          float64   `json:"alpha"`
	Beta           float64   `json:"beta"`
	SharpeRatio     float64   `json:"sharpe_ratio"`
	MaxDrawdown     float64   `json:"max_drawdown"`
	WinningPeriods  int       `json:"winning_periods"`
	LosingPeriods   int       `json:"losing_periods"`
	WinRate         float64   `json:"win_rate"`
	DailyReturns    []float64 `json:"daily_returns"`
	RiskMetrics     *RiskMetrics `json:"risk_metrics"`
	CreatedAt       time.Time `json:"created_at"`
}

// PortfolioAlert 投资组合预警
type PortfolioAlert struct {
	ID              string    `json:"id"`
	PortfolioID     string    `json:"portfolio_id"`
	UserID          string    `json:"user_id"`
	AlertType       string    `json:"alert_type"`    // risk, performance, allocation, news
	Severity        string    `json:"severity"`      // low, medium, high, critical
	Title           string    `json:"title"`
	Message         string    `json:"message"`
	TriggerValue    float64   `json:"trigger_value"`
	ThresholdValue  float64   `json:"threshold_value"`
	Condition       string    `json:"condition"`     // above, below, percentage_change
	IsActive       bool      `json:"is_active"`
	IsRead          bool      `json:"is_read"`
	CreatedAt       time.Time `json:"created_at"`
	ReadAt          time.Time `json:"read_at"`
	ExpiresAt       time.Time `json:"expires_at"`
}