package services

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

// AIAnalysisService AI分析服务
type AIAnalysisService struct {
	httpClient *http.Client
	baseURL    string
	apiKey     string
	logger     *Logger
}

// TechnicalAnalysisRequest 技术分析请求
type TechnicalAnalysisRequest struct {
	StockCode     string  `json:"stock_code"`
	Timeframe     string  `json:"timeframe"`
	Indicators    []string `json:"indicators"`
	AnalysisType  string  `json:"analysis_type"`
	LookbackDays  int     `json:"lookback_days"`
}

// FundamentalAnalysisRequest 基本面分析请求
type FundamentalAnalysisRequest struct {
	StockCode string `json:"stock_code"`
	Depth     string `json:"depth"`
	IncludePeers bool `json:"include_peers"`
}

// NewsAnalysisRequest 消息面分析请求
type NewsAnalysisRequest struct {
	StockCode    string `json:"stock_code"`
	NewsSources  []string `json:"news_sources"`
	AnalysisDays int    `json:"analysis_days"`
}

// PortfolioAnalysisRequest 投资组合分析请求
type PortfolioAnalysisRequest struct {
	StockCodes    []string `json:"stock_codes"`
	Positions     []float64 `json:"positions"`
	AnalysisType  string   `json:"analysis_type"`
	RiskFreeRate  float64  `json:"risk_free_rate"`
}

// TechnicalAnalysisResult 技术分析结果
type TechnicalAnalysisResult struct {
	Success              bool              `json:"success"`
	AnalysisTime         string            `json:"analysis_time"`
	StockCode            string            `json:"stock_code"`
	Trend                string            `json:"trend"`
	TrendStrength        float64           `json:"trend_strength"`
	SupportLevels        []float64         `json:"support_levels"`
	ResistanceLevels     []float64         `json:"resistance_levels"`
	TechnicalSignals     []TechnicalSignal `json:"technical_signals"`
	Recommendation       string            `json:"recommendation"`
	Confidence           float64           `json:"confidence"`
	TechnicalScore       float64           `json:"technical_score"`
	MomentumScore        float64           `json:"momentum_score"`
	VolumeScore          float64           `json:"volume_score"`
	VolatilityScore      float64           `json:"volatility_score"`
	OverallScore         float64           `json:"overall_score"`
	RiskWarning          string            `json:"risk_warning"`
	KeyObservations      []string          `json:"key_observations"`
	NextPriceTarget      float64           `json:"next_price_target"`
	StopLossLevel        float64           `json:"stop_loss_level"`
	TimeHorizon          string            `json:"time_horizon"`
}

// TechnicalSignal 技术信号
type TechnicalSignal struct {
	Indicator   string    `json:"indicator"`
	Action      string    `json:"action"`
	Strength    float64   `json:"strength"`
	Price       float64   `json:"price"`
	Time        time.Time `json:"time"`
	Description string    `json:"description"`
}

// FundamentalAnalysisResult 基本面分析结果
type FundamentalAnalysisResult struct {
	Success           bool              `json:"success"`
	AnalysisTime      string            `json:"analysis_time"`
	StockCode         string            `json:"stock_code"`
	CompanyProfile    CompanyProfile    `json:"company_profile"`
	FinancialHealth   FinancialHealth   `json:"financial_health"`
	Valuation         Valuation         `json:"valuation"`
	Profitability     Profitability     `json:"profitability"`
	GrowthMetrics     GrowthMetrics     `json:"growth_metrics"`
	PeerComparison    []PeerComparison  `json:"peer_comparison"`
	Recommendation    string            `json:"recommendation"`
	Confidence        float64           `json:"confidence"`
	FundamentalScore  float64           `json:"fundamental_score"`
	ValuationScore    float64           `json:"valuation_score"`
	GrowthScore       float64           `json:"growth_score"`
	ProfitabilityScore float64          `json:"profitability_score"`
	OverallScore      float64           `json:"overall_score"`
	RiskFactors       []RiskFactor      `json:"risk_factors"`
	InvestmentThesis  string            `json:"investment_thesis"`
	KeyObservations   []string          `json:"key_observations"`
	FairValueRange    FairValueRange    `json:"fair_value_range"`
}

// CompanyProfile 公司概况
type CompanyProfile struct {
	Name           string `json:"name"`
	Industry       string `json:"industry"`
	Market         string `json:"market"`
	ListingDate    string `json:"listing_date"`
	TotalShares    int64  `json:"total_shares"`
	MarketCap      float64 `json:"market_cap"`
	Description    string `json:"description"`
	BusinessModel  string `json:"business_model"`
	CompetitiveAdvantages []string `json:"competitive_advantages"`
}

// FinancialHealth 财务健康度
type FinancialHealth struct {
	DebtRatio        float64 `json:"debt_ratio"`
	CurrentRatio     float64 `json:"current_ratio"`
	QuickRatio       float64 `json:"quick_ratio"`
	InterestCoverage float64 `json:"interest_coverage"`
	HealthScore      float64 `json:"health_score"`
	CreditRating     string  `json:"credit_rating"`
	LiquidityStatus  string  `json:"liquidity_status"`
	LeverageLevel    string  `json:"leverage_level"`
}

// Valuation 估值分析
type Valuation struct {
	PERatio      float64 `json:"pe_ratio"`
	PBRatio      float64 `json:"pb_ratio"`
	PSRatio      float64 `json:"ps_ratio"`
	EV_EBITDA    float64 `json:"ev_ebitda"`
	DividendYield float64 `json:"dividend_yield"`
	ValuationScore float64 `json:"valuation_score"`
	ValuationLevel string  `json:"valuation_level"`
	RelativeValuation string `json:"relative_valuation"`
}

// Profitability 盈利能力
type Profitability struct {
	ROE        float64 `json:"roe"`
	ROA        float64 `json:"roa"`
	ROIC       float64 `json:"roic"`
	GrossMargin float64 `json:"gross_margin"`
	NetMargin   float64 `json:"net_margin"`
	OperatingMargin float64 `json:"operating_margin"`
	ProfitabilityScore float64 `json:"profitability_score"`
	ProfitabilityLevel string `json:"profitability_level"`
}

// GrowthMetrics 成长指标
type GrowthMetrics struct {
	RevenueGrowth     float64 `json:"revenue_growth"`
	NetProfitGrowth   float64 `json:"net_profit_growth"`
	EPGrowth          float64 `json:"ep_growth"`
	BookValueGrowth   float64 `json:"book_value_growth"`
	GrowthScore       float64 `json:"growth_score"`
	GrowthTrend       string  `json:"growth_trend"`
	GrowthConsistency string `json:"growth_consistency"`
}

// PeerComparison 同业对比
type PeerComparison struct {
	StockCode    string  `json:"stock_code"`
	StockName    string  `json:"stock_name"`
	PERatio      float64 `json:"pe_ratio"`
	PBRatio      float64 `json:"pb_ratio"`
	ROE          float64 `json:"roe"`
	RevenueGrowth float64 `json:"revenue_growth"`
	MarketCap    float64 `json:"market_cap"`
	Score        float64 `json:"score"`
}

// RiskFactor 风险因素
type RiskFactor struct {
	Type        string  `json:"type"`
	Description string  `json:"description"`
	Level       string  `json:"level"`
	Impact      string  `json:"impact"`
	Probability float64 `json:"probability"`
}

// FairValueRange 合理价值区间
type FairValueRange struct {
	LowerBound   float64 `json:"lower_bound"`
	UpperBound   float64 `json:"upper_bound"`
	MidPoint     float64 `json:"mid_point"`
	Confidence   float64 `json:"confidence"`
	Methodology  string  `json:"methodology"`
}

// NewsAnalysisResult 消息面分析结果
type NewsAnalysisResult struct {
	Success           bool              `json:"success"`
	AnalysisTime      string            `json:"analysis_time"`
	StockCode         string            `json:"stock_code"`
	SentimentScore    float64           `json:"sentiment_score"`
	SentimentTrend    string            `json:"sentiment_trend"`
	NewsCount         int               `json:"news_count"`
	PositiveNews      int               `json:"positive_news"`
	NegativeNews      int               `json:"negative_news"`
	NeutralNews       int               `json:"neutral_news"`
	Keywords          []string          `json:"keywords"`
	NewsSummary       string            `json:"news_summary"`
	RiskEvents        []RiskEvent       `json:"risk_events"`
	Recommendation    string            `json:"recommendation"`
	Confidence        float64           `json:"confidence"`
	NewsScore         float64           `json:"news_score"`
	AttentionLevel    string            `json:"attention_level"`
	MediaCoverage     string            `json:"media_coverage"`
	MarketImpact      string            `json:"market_impact"`
	NextCatalysts     []string          `json:"next_catalysts"`
}

// RiskEvent 风险事件
type RiskEvent struct {
	Title       string    `json:"title"`
	Source      string    `json:"source"`
	Time        time.Time `json:"time"`
	Impact      string    `json:"impact"`
	Category    string    `json:"category"`
	Severity    string    `json:"severity"`
	Description string    `json:"description"`
}

// PortfolioAnalysisResult 投资组合分析结果
type PortfolioAnalysisResult struct {
	Success               bool                    `json:"success"`
	AnalysisTime          string                  `json:"analysis_time"`
	PortfolioMetrics      PortfolioMetrics        `json:"portfolio_metrics"`
	RiskMetrics           RiskMetrics             `json:"risk_metrics"`
	ReturnMetrics         ReturnMetrics           `json:"return_metrics"`
	CorrelationMatrix     [][]float64             `json:"correlation_matrix"`
	ContributionAnalysis  []ContributionAnalysis  `json:"contribution_analysis"`
	OptimizationSuggestions []OptimizationSuggestion `json:"optimization_suggestions"`
	RiskWarning           string                  `json:"risk_warning"`
	Recommendation        string                  `json:"recommendation"`
	Confidence            float64                 `json:"confidence"`
	DiversificationScore  float64                 `json:"diversification_score"`
	RiskAdjustedScore     float64                 `json:"risk_adjusted_score"`
	OverallScore          float64                 `json:"overall_score"`
	RebalancingSuggestion RebalancingSuggestion   `json:"rebalancing_suggestion"`
}

// PortfolioMetrics 投资组合指标
type PortfolioMetrics struct {
	TotalValue       float64   `json:"total_value"`
	StockCount       int       `json:"stock_count"`
	SectorAllocation map[string]float64 `json:"sector_allocation"`
	Concentration    float64   `json:"concentration"`
	Beta             float64   `json:"beta"`
	MarketValue      float64   `json:"market_value"`
	CostBasis        float64   `json:"cost_basis"`
	UnrealizedPnL    float64   `json:"unrealized_pnl"`
	UnrealizedPnLPct float64   `json:"unrealized_pnl_pct"`
}

// RiskMetrics 风险指标
type RiskMetrics struct {
	PortfolioVolatility float64   `json:"portfolio_volatility"`
	PortfolioBeta       float64   `json:"portfolio_beta"`
	ValueAtRisk         float64   `json:"value_at_risk"`
	ExpectedShortfall   float64   `json:"expected_shortfall"`
	MaxDrawdown         float64   `json:"max_drawdown"`
	SharpeRatio         float64   `json:"sharpe_ratio"`
	SortinoRatio        float64   `json:"sortino_ratio"`
	InformationRatio    float64   `json:"information_ratio"`
	TrackingError       float64   `json:"tracking_error"`
	RiskContribution    []float64 `json:"risk_contribution"`
}

// ReturnMetrics 收益指标
type ReturnMetrics struct {
	TotalReturn       float64 `json:"total_return"`
	AnnualizedReturn  float64 `json:"annualized_return"`
	MonthlyReturn     float64 `json:"monthly_return"`
	Alpha             float64 `json:"alpha"`
	Beta              float64 `json:"beta"`
	WinRate           float64 `json:"win_rate"`
	ProfitFactor      float64 `json:"profit_factor"`
	AvgWin            float64 `json:"avg_win"`
	AvgLoss           float64 `json:"avg_loss"`
	BestMonth         float64 `json:"best_month"`
	WorstMonth        float64 `json:"worst_month"`
}

// ContributionAnalysis 贡献度分析
type ContributionAnalysis struct {
	StockCode        string  `json:"stock_code"`
	StockName        string  `json:"stock_name"`
	Weight           float64 `json:"weight"`
	Return           float64 `json:"return"`
	Contribution     float64 `json:"contribution"`
	ContributionPct  float64 `json:"contribution_pct"`
	RiskContribution float64 `json:"risk_contribution"`
}

// OptimizationSuggestion 优化建议
type OptimizationSuggestion struct {
	Type        string  `json:"type"`
	Description string  `json:"description"`
	Action      string  `json:"action"`
	Impact      string  `json:"impact"`
	Priority    string  `json:"priority"`
}

// RebalancingSuggestion 再平衡建议
type RebalancingSuggestion struct {
	CurrentWeights   map[string]float64 `json:"current_weights"`
	TargetWeights    map[string]float64 `json:"target_weights"`
	RebalanceActions []RebalanceAction  `json:"rebalance_actions"`
	Reason           string             `json:"reason"`
	Timing           string             `json:"timing"`
}

// RebalanceAction 再平衡操作
type RebalanceAction struct {
	StockCode string  `json:"stock_code"`
	Action    string  `json:"action"`
	Quantity  int64   `json:"quantity"`
	Amount    float64 `json:"amount"`
	Reason    string  `json:"reason"`
}

// NewAIAnalysisService 创建AI分析服务
func NewAIAnalysisService(baseURL string, apiKey string) *AIAnalysisService {
	return &AIAnalysisService{
		httpClient: &http.Client{
			Timeout: 30 * time.Second,
		},
		baseURL: baseURL,
		apiKey:  apiKey,
		logger:  AppLogger,
	}
}

// TechnicalAnalysis 技术分析
func (s *AIAnalysisService) TechnicalAnalysis(ctx context.Context, req *TechnicalAnalysisRequest) (*TechnicalAnalysisResult, error) {
	s.logger.Info("开始技术分析: %s", req.StockCode)

	url := fmt.Sprintf("%s/api/ai/technical-analysis", s.baseURL)

	jsonData, err := json.Marshal(req)
	if err != nil {
		return nil, fmt.Errorf("序列化请求失败: %v", err)
	}

	httpReq, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("创建HTTP请求失败: %v", err)
	}

	httpReq.Header.Set("Content-Type", "application/json")
	if s.apiKey != "" {
		httpReq.Header.Set("Authorization", "Bearer "+s.apiKey)
	}

	resp, err := s.httpClient.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("请求AI服务失败: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("AI服务返回错误: %d, %s", resp.StatusCode, string(body))
	}

	var apiResponse struct {
		Success bool                   `json:"success"`
		Message string                 `json:"message"`
		Data    *TechnicalAnalysisResult `json:"data"`
		Error   string                 `json:"error"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&apiResponse); err != nil {
		return nil, fmt.Errorf("解析响应失败: %v", err)
	}

	if !apiResponse.Success {
		return nil, fmt.Errorf("AI分析失败: %s", apiResponse.Error)
	}

	s.logger.Info("技术分析完成: %s", req.StockCode)
	return apiResponse.Data, nil
}

// FundamentalAnalysis 基本面分析
func (s *AIAnalysisService) FundamentalAnalysis(ctx context.Context, req *FundamentalAnalysisRequest) (*FundamentalAnalysisResult, error) {
	s.logger.Info("开始基本面分析: %s", req.StockCode)

	url := fmt.Sprintf("%s/api/ai/fundamental-analysis", s.baseURL)

	jsonData, err := json.Marshal(req)
	if err != nil {
		return nil, fmt.Errorf("序列化请求失败: %v", err)
	}

	httpReq, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("创建HTTP请求失败: %v", err)
	}

	httpReq.Header.Set("Content-Type", "application/json")
	if s.apiKey != "" {
		httpReq.Header.Set("Authorization", "Bearer "+s.apiKey)
	}

	resp, err := s.httpClient.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("请求AI服务失败: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("AI服务返回错误: %d, %s", resp.StatusCode, string(body))
	}

	var apiResponse struct {
		Success bool                     `json:"success"`
		Message string                   `json:"message"`
		Data    *FundamentalAnalysisResult `json:"data"`
		Error   string                   `json:"error"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&apiResponse); err != nil {
		return nil, fmt.Errorf("解析响应失败: %v", err)
	}

	if !apiResponse.Success {
		return nil, fmt.Errorf("AI分析失败: %s", apiResponse.Error)
	}

	s.logger.Info("基本面分析完成: %s", req.StockCode)
	return apiResponse.Data, nil
}

// NewsAnalysis 消息面分析
func (s *AIAnalysisService) NewsAnalysis(ctx context.Context, req *NewsAnalysisRequest) (*NewsAnalysisResult, error) {
	s.logger.Info("开始消息面分析: %s", req.StockCode)

	url := fmt.Sprintf("%s/api/ai/news-analysis", s.baseURL)

	jsonData, err := json.Marshal(req)
	if err != nil {
		return nil, fmt.Errorf("序列化请求失败: %v", err)
	}

	httpReq, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("创建HTTP请求失败: %v", err)
	}

	httpReq.Header.Set("Content-Type", "application/json")
	if s.apiKey != "" {
		httpReq.Header.Set("Authorization", "Bearer "+s.apiKey)
	}

	resp, err := s.httpClient.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("请求AI服务失败: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("AI服务返回错误: %d, %s", resp.StatusCode, string(body))
	}

	var apiResponse struct {
		Success bool                `json:"success"`
		Message string              `json:"message"`
		Data    *NewsAnalysisResult `json:"data"`
		Error   string              `json:"error"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&apiResponse); err != nil {
		return nil, fmt.Errorf("解析响应失败: %v", err)
	}

	if !apiResponse.Success {
		return nil, fmt.Errorf("AI分析失败: %s", apiResponse.Error)
	}

	s.logger.Info("消息面分析完成: %s", req.StockCode)
	return apiResponse.Data, nil
}

// PortfolioAnalysis 投资组合分析
func (s *AIAnalysisService) PortfolioAnalysis(ctx context.Context, req *PortfolioAnalysisRequest) (*PortfolioAnalysisResult, error) {
	s.logger.Info("开始投资组合分析: %d只股票", len(req.StockCodes))

	url := fmt.Sprintf("%s/api/ai/portfolio-analysis", s.baseURL)

	jsonData, err := json.Marshal(req)
	if err != nil {
		return nil, fmt.Errorf("序列化请求失败: %v", err)
	}

	httpReq, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("创建HTTP请求失败: %v", err)
	}

	httpReq.Header.Set("Content-Type", "application/json")
	if s.apiKey != "" {
		httpReq.Header.Set("Authorization", "Bearer "+s.apiKey)
	}

	resp, err := s.httpClient.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("请求AI服务失败: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("AI服务返回错误: %d, %s", resp.StatusCode, string(body))
	}

	var apiResponse struct {
		Success bool                   `json:"success"`
		Message string                 `json:"message"`
		Data    *PortfolioAnalysisResult `json:"data"`
		Error   string                 `json:"error"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&apiResponse); err != nil {
		return nil, fmt.Errorf("解析响应失败: %v", err)
	}

	if !apiResponse.Success {
		return nil, fmt.Errorf("AI分析失败: %s", apiResponse.Error)
	}

	s.logger.Info("投资组合分析完成: %d只股票", len(req.StockCodes))
	return apiResponse.Data, nil
}

// GetAICapabilities 获取AI分析能力
func (s *AIAnalysisService) GetAICapabilities(ctx context.Context) (map[string]interface{}, error) {
	s.logger.Info("获取AI分析能力")

	url := fmt.Sprintf("%s/api/ai/capabilities", s.baseURL)

	httpReq, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		return nil, fmt.Errorf("创建HTTP请求失败: %v", err)
	}

	if s.apiKey != "" {
		httpReq.Header.Set("Authorization", "Bearer "+s.apiKey)
	}

	resp, err := s.httpClient.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("请求AI服务失败: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("AI服务返回错误: %d, %s", resp.StatusCode, string(body))
	}

	var apiResponse struct {
		Success bool                    `json:"success"`
		Message string                  `json:"message"`
		Data    map[string]interface{}  `json:"data"`
		Error   string                  `json:"error"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&apiResponse); err != nil {
		return nil, fmt.Errorf("解析响应失败: %v", err)
	}

	if !apiResponse.Success {
		return nil, fmt.Errorf("获取AI能力失败: %s", apiResponse.Error)
	}

	s.logger.Info("AI分析能力获取成功")
	return apiResponse.Data, nil
}