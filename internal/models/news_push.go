package models

import (
	"time"
)

// NewsPushService 新闻推送服务
type NewsPushService struct {
	ID            string     `json:"id"`
	Name          string     `json:"name"`
	Type          string     `json:"type"`         // websocket, sse, push_notification
	Enabled       bool       `json:"enabled"`
	Config        string     `json:"config"`      // JSON配置
	ConnectedUsers int        `json:"connected_users"`
	MessageCount  int64      `json:"message_count"`
	ErrorRate     float64    `json:"error_rate"`
	CreatedAt     time.Time  `json:"created_at"`
	UpdatedAt     time.Time  `json:"updated_at"`
}

// PushMessage 推送消息
type PushMessage struct {
	ID          string                 `json:"id"`
	Type        string                 `json:"type"`         // news, alert, analysis, portfolio_update
	Title       string                 `json:"title"`
	Content     string                 `json:"content"`
	Summary     string                 `json:"summary"`
	URL         string                 `json:"url"`
	ImageURL    string                 `json:"image_url"`
	Category    string                 `json:"category"`
	Priority    string                 `json:"priority"`    // high, medium, low
	Tags        []string               `json:"tags"`
	Data        map[string]interface{} `json:"data"`        // 额外数据
	Target      *PushTarget            `json:"target"`
	ScheduleAt  *time.Time             `json:"schedule_at"`  // 定时推送
	ExpiresAt   *time.Time             `json:"expires_at"`   // 消息过期时间
	CreatedAt   time.Time              `json:"created_at"`
	UpdatedAt   time.Time              `json:"updated_at"`
	Delivered   bool                   `json:"delivered"`    // 是否已送达
	Read        bool                   `json:"read"`         // 是否已读
	Clicked     bool                   `json:"clicked"`      // 是否已点击
	Dismissed   bool                   `json:"dismissed"`   // 是否已忽略
}

// PushTarget 推送目标
type PushTarget struct {
	UserIDs     []string `json:"user_ids"`
	PortfolioIDs []string `json:"portfolio_ids"`
	StockCodes  []string `json:"stock_codes"`
	Sectors     []string `json:"sectors"`
	Keywords    []string `json:"keywords"`
	DeviceType  []string `json:"device_type"`  // web, mobile, desktop
	Online      bool     `json:"online"`       // 只推送在线用户
	Location    *GeoTarget `json:"location"`
	CustomFilter string   `json:"custom_filter"`
}

// GeoTarget 地理位置目标
type GeoTarget struct {
	Country     []string `json:"country"`
	Province   []string `json:"province"`
	City       []string `json:"city"`
	Coordinates *CoordinateRange `json:"coordinates"`
}

// CoordinateRange 坐标范围
type CoordinateRange struct {
	LatMin float64 `json:"lat_min"`
	LatMax float64 `json:"lat_max"`
	LngMin float64 `json:"lng_min"`
	LngMax float64 `json:"lng_max"`
}

// PushSubscription 推送订阅
type PushSubscription struct {
	ID            string    `json:"id"`
	UserID        string    `json:"user_id"`
	DeviceType    string    `json:"device_type"`
	DeviceToken   string    `json:"device_token"`
	Endpoint      string    `json:"endpoint"`
	Keys          *Keys    `json:"keys"`
	Subscriptions  []string  `json:"subscriptions"`  // news, alerts, analysis
	Preferences   *Preferences `json:"preferences"`
	IsActive      bool      `json:"is_active"`
	CreatedAt      time.Time `json:"created_at"`
	UpdatedAt      time.Time `json:"updated_at"`
	LastActivityAt  time.Time `json:"last_activity_at"`
}

// Keys 推送密钥
type Keys struct {
	P256DH string `json:"p256dh"`
	Auth   string `json:"auth"`
}

// Preferences 推送偏好设置
type Preferences struct {
	News            *NewsPreferences        `json:"news"`
	Alerts          *AlertPreferences       `json:"alerts"`
	Analysis        *AnalysisPreferences    `json:"analysis"`
	Portfolio       *PortfolioPreferences  `json:"portfolio"`
	QuietHours      []int                  `json:"quiet_hours"`
	MaxMessagesPerDay int                   `json:"max_messages_per_day"`
	DoNotDisturb    bool                  `json:"do_not_disturb"`
}

// NewsPreferences 新闻偏好
type NewsPreferences struct {
	Enabled       bool     `json:"enabled"`
	Categories    []string `json:"categories"`
	Sources       []string `json:"sources"`
	Keywords      []string `json:"keywords"`
	StockCodes    []string `json:"stock_codes"`
	Frequency     string   `json:"frequency"`    // realtime, hourly, daily, weekly
	MaxPerDay     int      `json:"max_per_day"`
}

// AlertPreferences 预警偏好
type AlertPreferences struct {
	Enabled         bool              `json:"enabled"`
	PriceChange     bool              `json:"price_change"`
	VolumeChange    bool              `json:"volume_change"`
	NewsBreakout   bool              `json:"news_breakout"`
	TechnicalSignal bool              `json:"technical_signal"`
	RiskLevel      string            `json:"risk_level"`      // low, medium, high
	MinChangePct   float64           `json:"min_change_pct"`
}

// AnalysisPreferences 分析偏好
type AnalysisPreferences struct {
	Enabled       bool     `json:"enabled"`
	Completed     bool     `json:"completed"`
	NewRecommendations bool `json:"new_recommendations"`
	RiskAnalysis   bool     `json:"risk_analysis"`
	WeeklySummary bool     `json:"weekly_summary"`
	Frequency     string   `json:"frequency"`
}

// PortfolioPreferences 投资组合偏好
type PortfolioPreferences struct {
	Enabled           bool   `json:"enabled"`
	DailyUpdate       bool   `json:"daily_update"`
	PerformanceAlert   bool   `json:"performance_alert"`
	RebalanceAlert    bool   `json:"rebalance_alert"`
	RiskAlert        bool   `json:"risk_alert"`
	ThresholdChangePct float64 `json:"threshold_change_pct"`
}

// PushDelivery 推送送达状态
type PushDelivery struct {
	ID          string    `json:"id"`
	MessageID   string    `json:"message_id"`
	UserID      string    `json:"user_id"`
	DeviceType  string    `json:"device_type"`
	Status      string    `json:"status"`       // pending, sent, delivered, failed, expired
	Attempts    int       `json:"attempts"`
	LastAttempt time.Time `json:"last_attempt"`
	ErrorCode   string    `json:"error_code"`
	ErrorMsg    string    `json:"error_msg"`
	DeliveredAt time.Time `json:"delivered_at"`
	ReadAt      time.Time `json:"read_at"`
	ClickedAt   time.Time `json:"clicked_at"`
	CreatedAt   time.Time `json:"created_at"`
}

// PushAnalytics 推送分析
type PushAnalytics struct {
	ID                 string    `json:"id"`
	MessageID          string    `json:"message_id"`
	TotalSent          int       `json:"total_sent"`
	TotalDelivered      int       `json:"total_delivered"`
	TotalRead          int       `json:"total_read"`
	TotalClicked       int       `json:"total_clicked"`
	DeliveryRate       float64   `json:"delivery_rate"`
	ReadRate          float64   `json:"read_rate"`
	ClickRate         float64   `json:"click_rate"`
	AvgDeliveryTime    float64   `json:"avg_delivery_time"`
	AvgReadTime        float64   `json:"avg_read_time"`
	AvgClickTime       float64   `json:"avg_click_time"`
	DeviceBreakdown    map[string]int `json:"device_breakdown"`
	RegionBreakdown    map[string]int `json:"region_breakdown"`
	TimeBreakdown      map[string]int `json:"time_breakdown"`
	AnalyticsDate      time.Time  `json:"analytics_date"`
	CreatedAt         time.Time  `json:"created_at"`
}

// PushTemplate 推送模板
type PushTemplate struct {
	ID          string    `json:"id"`
	Name        string    `json:"name"`
	Type        string    `json:"type"`        // news, alert, analysis, portfolio
	Category    string    `json:"category"`
	Title       string    `json:"title"`
	Content     string    `json:"content"`
	Summary     string    `json:"summary"`
	ImageURL    string    `json:"image_url"`
	DeepLink    string    `json:"deep_link"`
	Variables   []string  `json:"variables"`   // 模板变量
	IsActive    bool      `json:"is_active"`
	CreatedAt   time.Time  `json:"created_at"`
	UpdatedAt   time.Time  `json:"updated_at"`
}

// PushRule 推送规则
type PushRule struct {
	ID          string        `json:"id"`
	Name        string        `json:"name"`
	Description string        `json:"description"`
	Trigger     *RuleTrigger  `json:"trigger"`
	Condition   *RuleCondition `json:"condition"`
	Action      *RuleAction    `json:"action"`
	IsActive    bool          `json:"is_active"`
	Priority    int           `json:"priority"`    // 1-10
	CreatedAt   time.Time      `json:"created_at"`
	UpdatedAt   time.Time      `json:"updated_at"`
}

// RuleTrigger 规则触发器
type RuleTrigger struct {
	Type       string    `json:"type"`        // news, price, volume, technical, time, portfolio
	Parameters  map[string]interface{} `json:"parameters"`
}

// RuleCondition 规则条件
type RuleCondition struct {
	Operator   string  `json:"operator"`    // equals, greater_than, less_than, contains, regex
	Field      string  `json:"field"`      // title, content, category, priority, price_change_pct, volume_change_pct
	Value      interface{} `json:"value"`
	LogicalOp  string  `json:"logical_op"` // and, or, not
}

// RuleAction 规则动作
type RuleAction struct {
	Type       string            `json:"type"`          // send_message, create_alert, update_subscription, trigger_webhook
	Template   string            `json:"template"`      // 模板ID或消息内容
	Parameters map[string]interface{} `json:"parameters"`
	Delay      int               `json:"delay"`        // 延迟秒数
	MaxCount   int               `json:"max_count"`    // 最大执行次数
}

// PushCampaign 推送活动
type PushCampaign struct {
	ID          string    `json:"id"`
	Name        string    `json:"name"`
	Description string    `json:"description"`
	Type        string    `json:"type"`        // announcement, marketing, alert
	Template    string    `json:"template"`
	Target      *PushTarget `json:"target"`
	Schedule    *Schedule    `json:"schedule"`
	Status      string    `json:"status"`      // draft, scheduled, running, completed, paused, cancelled
	StartTime   time.Time   `json:"start_time"`
	EndTime     time.Time   `json:"end_time"`
	Stats       *CampaignStats `json:"stats"`
	CreatedAt   time.Time   `json:"created_at"`
	UpdatedAt   time.Time   `json:"updated_at"`
}

// Schedule 调度配置
type Schedule struct {
	Type        string    `json:"type"`        // immediate, scheduled, recurring
	StartAt     time.Time `json:"start_at"`
	EndAt       *time.Time `json:"end_at"`
	Timezone    string    `json:"timezone"`
	Frequency   string    `json:"frequency"`   // daily, weekly, monthly
	DaysOfWeek  []int     `json:"days_of_week"` // 0-6, 0=Sunday
	TimeOfDay   string    `json:"time_of_day"`   // "09:00"
	MaxRuns     int       `json:"max_runs"`
}

// CampaignStats 活动统计
type CampaignStats struct {
	TotalSent      int     `json:"total_sent"`
	TotalDelivered int     `json:"total_delivered"`
	TotalRead      int     `json:"total_read"`
	TotalClicked   int     `json:"total_clicked"`
	DeliveryRate   float64 `json:"delivery_rate"`
	ReadRate       float64 `json:"read_rate"`
	ClickRate      float64 `json:"click_rate"`
	Cost           float64 `json:"cost"`
	ROI            float64 `json:"roi"`
}

// PushProvider 推送服务提供商
type PushProvider struct {
	ID          string    `json:"id"`
	Name        string    `json:"name"`
	Type        string    `json:"type"`       // websocket, sse, apns, fcm, huawei, xiaomi, oppo, vivo
	Config      string    `json:"config"`
	Enabled     bool      `json:"enabled"`
	Priority    int       `json:"priority"`
	RateLimit   int       `json:"rate_limit"`
	SuccessRate float64   `json:"success_rate"`
	ErrorRate   float64   `json:"error_rate"`
	CreatedAt   time.Time  `json:"created_at"`
	UpdatedAt   time.Time  `json:"updated_at"`
}

// PushQueue 推送队列
type PushQueue struct {
	ID          string    `json:"id"`
	MessageID   string    `json:"message_id"`
	UserID      string    `json:"user_id"`
	ProviderID  string    `json:"provider_id"`
	Priority    string    `json:"priority"`    // high, medium, low
	Attempts    int       `json:"attempts"`
	MaxAttempts int       `json:"max_attempts"`
	NextAttempt time.Time `json:"next_attempt"`
	Status      string    `json:"status"`       // pending, processing, completed, failed
	ErrorMsg    string    `json:"error_msg"`
	CreatedAt   time.Time `json:"created_at"`
	UpdatedAt   time.Time `json:"updated_at"`
}

// WebSocketConnection WebSocket连接
type WebSocketConnection struct {
	ID        string    `json:"id"`
	UserID    string    `json:"user_id"`
	Conn      interface{} `json:"conn"`
	DeviceType string    `json:"device_type"`
	UserAgent  string    `json:"user_agent"`
	IP        string    `json:"ip"`
	Location  string    `json:"location"`
	ConnectedAt time.Time `json:"connected_at"`
	LastSeenAt time.Time `json:"last_seen_at"`
	IsActive   bool      `json:"is_active"`
}

// PushStats 推送统计
type PushStats struct {
	Date                time.Time `json:"date"`
	TotalMessages       int       `json:"total_messages"`
	NewsMessages        int       `json:"news_messages"`
	AlertMessages       int       `json:"alert_messages"`
	AnalysisMessages    int       `json:"analysis_messages"`
	PortfolioMessages  int       `json:"portfolio_messages"`
	SuccessRate        float64   `json:"success_rate"`
	AvgDeliveryTime    float64   `json:"avg_delivery_time"`
	ActiveConnections  int       `json:"active_connections"`
	QueueLength        int       `json:"queue_length"`
	ErrorRate          float64   `json:"error_rate"`
	CreatedAt          time.Time `json:"created_at"`
}

// PushEvent 推送事件
type PushEvent struct {
	ID        string    `json:"id"`
	Type      string    `json:"type"`      // user_connect, user_disconnect, message_sent, message_delivered, message_read, message_clicked, error
	UserID    string    `json:"user_id"`
	MessageID string    `json:"message_id"`
	Data      map[string]interface{} `json:"data"`
	Timestamp time.Time `json:"timestamp"`
	Source    string    `json:"source"`
	Level     string    `json:"level"`     // info, warning, error, debug
}

// PushLog 推送日志
type PushLog struct {
	ID        string    `json:"id"`
	Level     string    `json:"level"`     // debug, info, warning, error, fatal
	Message   string    `json:"message"`
	Data      map[string]interface{} `json:"data"`
	UserID    string    `json:"user_id"`
	MessageID string    `json:"message_id"`
	ProviderID string    `json:"provider_id"`
	Timestamp time.Time `json:"timestamp"`
	TraceID   string    `json:"trace_id"`
}