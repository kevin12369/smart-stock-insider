package services

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"sync"
	"time"

	"smart-stock-insider/internal/models"
)

// PushProvider 推送提供商
type PushProvider struct {
	ID         string                 `json:"id"`
	Name       string                 `json:"name"`
	Type       string                 `json:"type"`
	Enabled    bool                   `json:"enabled"`
	Config     map[string]interface{} `json:"config"`
	Priority   int                    `json:"priority"`
	RateLimit  int                    `json:"rate_limit"`
}

// PushTemplate 推送模板
type PushTemplate struct {
	ID       string `json:"id"`
	Name     string `json:"name"`
	Content  string `json:"content"`
	Type     string `json:"type"`
}

// PushRule 推送规则
type PushRule struct {
	ID          string         `json:"id"`
	Name        string         `json:"name"`
	Enabled     bool           `json:"enabled"`
	Triggers    []RuleTrigger  `json:"triggers"`
	Conditions  []RuleCondition `json:"conditions"`
	Actions     []RuleAction   `json:"actions"`
}

// RuleTrigger 规则触发器
type RuleTrigger struct {
	Type     string `json:"type"`
	Value    string `json:"value"`
	Operator string `json:"operator"`
}

// RuleCondition 规则条件
type RuleCondition struct {
	Field    string      `json:"field"`
	Operator string      `json:"operator"`
	Value    interface{} `json:"value"`
}

// RuleAction 规则动作
type RuleAction struct {
	Type     string `json:"type"`
	Provider string `json:"provider"`
	Template string `json:"template"`
}

// NewsPushService 新闻推送服务
type NewsPushService struct {
	dataService      *DataService
	db              *sql.DB
	connections     map[string]*models.WebSocketConnection
	subscriptions   map[string]*models.PushSubscription
	templates       map[string]*models.PushTemplate
	rules           map[string]*models.PushRule
	campaigns       map[string]*models.PushCampaign
	providers       map[string]*models.PushProvider
	queue           *PushQueue
	analytics       *models.PushAnalytics
	mutex           sync.RWMutex
	logger          *log.Logger
	httpClient      *http.Client
}

// PushQueue 推送队列管理
type PushQueue struct {
	messages    []*models.PushMessage
	processing  map[string]bool
	failed      []*models.PushMessage
	mutex       sync.Mutex
}

// NewNewsPushService 创建新闻推送服务
func NewNewsPushService(dataService *DataService) *NewsPushService {
	return &NewsPushService{
		dataService:    dataService,
		db:             dataService.GetDB(),
		connections:    make(map[string]*models.WebSocketConnection),
		subscriptions: make(map[string]*models.PushSubscription),
		templates:      make(map[string]*models.PushTemplate),
		rules:          make(map[string]*models.PushRule),
		campaigns:      make(map[string]*models.PushCampaign),
		providers:      make(map[string]*models.PushProvider),
		queue:          &PushQueue{
			messages:   make([]*models.PushMessage, 0),
			processing: make(map[string]bool),
			failed:     make([]*models.PushMessage, 0),
		},
		analytics:      &models.PushAnalytics{},
		mutex:          sync.RWMutex{},
		logger:         log.Default(),
		httpClient: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

// StartPushService 启动推送服务
func (nps *NewsPushService) StartPushService() error {
	log.Printf("启动新闻推送服务")

	// 初始化推送配置
	if err := nps.initPushProviders(); err != nil {
		return fmt.Errorf("初始化推送提供商失败: %v", err)
	}

	// 加载推送模板
	if err := nps.loadPushTemplates(); err != nil {
		return fmt.Errorf("加载推送模板失败: %v", err)
	}

	// 加载推送规则
	if err := nps.loadPushRules(); err != nil {
		return fmt.Errorf("加载推送规则失败: %v", err)
	}

	// 初始化默认配置
	if err := nps.initDefaultConfig(); err != nil {
		return fmt.Errorf("初始化默认配置失败: %v", err)
	}

	// 启动队列处理器
	go nps.processPushQueue()

	// 启动定时任务
	go nps.schedulePeriodicTasks()

	// 启动WebSocket连接管理
	go nps.manageWebSocketConnections()

	log.Printf("新闻推送服务启动成功")
	return nil
}

// initPushProviders 初始化推送提供商
func (nps *NewsPushService) initPushProviders() error {
	providers := []*PushProvider{
		{
			ID:       "websocket",
			Name:     "WebSocket",
			Type:     "websocket",
			Config:    map[string]interface{}{},
			Enabled:  true,
			Priority: 1,
			RateLimit: 0, // 无限制
		},
		{
			ID:       "sse",
			Name:     "Server-Sent Events",
			Type:     "sse",
			Config:    map[string]interface{}{},
			Enabled:  true,
			Priority: 2,
			RateLimit: 1000, // 每分钟1000个事件
		},
		{
			ID:       "apns",
			Name:     "Apple Push Notification Service",
			Type:     "push_notification",
			Config: map[string]interface{}{
				"team_id": "your-team-id",
				"key_id": "your-key-id",
			},
			Enabled:  false, // 需要配置
			Priority: 3,
			RateLimit: 100,  // 每分钟100个推送
		},
		{
			ID:       "fcm",
			Name:     "Firebase Cloud Messaging",
			Type:     "push_notification",
			Config:    "{\n				\"server_key\": \"your-server-key\"\n			}",
			Enabled:  false, // 需要配置
			Priority: 3,
			RateLimit: 100,  // 每分钟100个推送
		},
	}

	for _, provider := range providers {
		nps.providers[provider.ID] = provider
	}

	return nil
}

// loadPushTemplates 加载推送模板
func (nps *NewsPushService) loadPushTemplates() error {
	templates := []*PushTemplate{
		{
			ID:       "news_breakout",
			Name:     "新闻突发",
			Type:     "news",
			Category: "urgent",
			Title:    "📰 紧急通知：{{.StockName}}",
			Content:  "{{.Title}}\\n\\n{{.Summary}}\\n\\n点击查看详情",
			Summary:  "{{.StockCode}}: {{.Title}}",
			IsActive: true,
		},
		{
			ID:       "price_alert",
			Name:     "价格预警",
			Type:     "alert",
			Category: "finance",
			Title:    "💰 {{.StockName}} 价格预警",
			Content:  "当前价格：¥{{.CurrentPrice}}\\n目标价格：¥{{.TargetPrice}}\\n变动：{{.ChangePct}}%",
			Summary:  "{{.StockCode}} 价格变动 {{.ChangePct}}%",
			IsActive: true,
		},
		{
			ID:       "technical_signal",
			Name:     "技术信号",
			Type:     "analysis",
			Category: "analysis",
			Title:    "📈 {{.StockName}} 技术分析信号",
			Content:  "{{.SignalName}}\\n价格：¥{{.Price}}\\n建议：{{.Recommendation}}",
			Summary:  "{{.StockCode}} {{.SignalName}} 信号",
			IsActive: true,
		},
		{
			ID:       "portfolio_update",
			Name:     "投资组合更新",
			Type:     "portfolio_update",
			Category: "portfolio",
			Title:    "💼 投资组合更新",
			Content:  "{{.PortfolioName}}\\n总收益：{{.TotalReturn}}%\\n建议进行再平衡",
			Summary:  "投资组合 {{.PortfolioName}} 更新",
			IsActive: true,
		},
		{
			ID:       "market_analysis",
			Name:     "市场分析",
			Type:     "analysis",
			Category: "analysis",
			Title:    "📊 每日市场分析",
			Content:  "今日市场表现:\\n上涨：{{.UpCount}}家\\n下跌：{{.DownCount}}家\\n平盘：{{.FlatCount}}家",
			Summary:  "每日市场分析报告",
			IsActive: true,
		},
	}

	for _, template := range templates {
		nps.templates[template.ID] = template
	}

	return nil
}

// loadPushRules 加载推送规则
func (nps *NewsPushService) loadPushRules() error {
	rules := []*PushRule{
		{
			ID:          "high_impact_news",
			Name:        "高影响力新闻",
			Description: "监测高影响力新闻并立即推送",
			Trigger: &RuleTrigger{
				Type: "news",
				Parameters: map[string]interface{}{
					"min_sentiment_score": 0.8,
					"min_relevance":     0.9,
				"categories":        []string{"major", "breaking"},
				"sources":          []string{"xinhua", "caixin"},
				},
			},
			Condition: &RuleCondition{
				Operator: "and",
				Rules: []*RuleCondition{
					{
						Operator: "greater_than",
						Field:    "sentiment_score",
						Value:    0.8,
					},
					{
						Operator: "greater_than",
						Field:    "relevance",
						Value:    0.9,
					},
					{
						Operator: "contains",
						Field:    "category",
						Value:    "major",
					},
				},
			},
			Action: &RuleAction{
				Type:       "send_message",
				Template:  "news_breakout",
				Parameters: map[string]interface{}{
					"priority": "high",
					"delay":     0,
				},
			},
			IsActive:  true,
			Priority:  1,
		},
		{
			ID:          "price_movement_alert",
			Name:        "价格变动预警",
			Description: "股价达到设定涨跌幅时推送",
			Trigger: &RuleTrigger{
				Type: "price",
				Parameters: map[string]interface{}{
					"change_threshold": 0.05, // 5%
					"min_volume":      1000000,
				},
			},
			Condition: &RuleCondition{
				Operator: "greater_than",
				Field:    "abs_change_pct",
				Value:    0.05,
			},
			Action: &RuleAction{
				Type:       "send_message",
				Template:  "price_alert",
				Parameters: map[string]interface{}{
					"priority": "medium",
					"delay":     5,
				},
			},
			IsActive:  true,
			Priority: 2,
		},
		{
			ID:          "portfolio_rebalance",
			Name:        "投资组合再平衡",
			Description: "投资组合偏离目标配置时推送",
			Trigger: &RuleTrigger{
				Type: "portfolio",
				Parameters: map[string]interface{}{
					"deviation_threshold": 0.1, // 10%
					"min_portfolio_value": 100000,
				},
			},
			Condition: &RuleCondition{
				Operator: "greater_than",
				Field:    "max_deviation",
				Value:    0.1,
			},
			Action: &RuleAction{
				Type:       "send_message",
				Template:  "portfolio_update",
				Parameters: map[string]interface{}{
					"priority": "low",
					"delay":     0,
				},
			},
			IsActive:  true,
			Priority: 3,
		},
		{
			ID:          "daily_summary",
			Name:        "每日收盘总结",
			Description: "每个交易日结束后推送市场总结",
			Trigger: &RuleTrigger{
				Type: "time",
				Parameters: map[string]interface{}{
					"trigger_time": "15:30", // 15:30
					"trigger_days": []int{1, 2, 3, 4, 5}, // 工作日
				},
			},
			Action: &RuleAction{
				Type:       "send_message",
				Template:  "market_analysis",
				Parameters: map[string]interface{}{
					"priority": "low",
					"delay":     0,
				},
			},
			IsActive:  true,
			Priority: 4,
		},
	}

	for _, rule := range rules {
		nps.rules[rule.ID] = rule
	}

	return nil
}

// initDefaultConfig 初始化默认配置
func (nps *NewsPushService) initDefaultConfig() error {
	// 创建默认推送规则
	defaultRules := []string{"high_impact_news", "price_movement_alert"}

	for _, ruleID := range defaultRules {
		if rule, exists := nps.rules[ruleID]; exists {
			rule.IsActive = true
		}
	}

	// 创建默认推送模板
	defaultTemplates := []string{"news_breakout", "price_alert", "technical_signal"}

	for _, templateID := range defaultTemplates {
		if template, exists := nps.templates[templateID]; exists {
			template.IsActive = true
		}
	}

	return nil
}

// SendPushMessage 发送推送消息
func (nps *NewsPushService) SendPushMessage(message *models.PushMessage) (*models.PushDelivery, error) {
	nps.mutex.Lock()
	defer nps.mutex.Unlock()

	// 生成消息ID
	if message.ID == "" {
		message.ID = fmt.Sprintf("msg_%d", time.Now().UnixNano())
	}

	// 设置创建时间
	now := time.Now()
	message.CreatedAt = now
	message.UpdatedAt = now

	// 添加到队列
	nps.queue.messages = append(nps.queue.messages, message)

	// 异步处理推送
	go nps.processMessage(message)

	// 创建送达记录
	delivery := &models.PushDelivery{
		ID:         fmt.Sprintf("delivery_%s", message.ID),
		MessageID:  message.ID,
		Status:     "pending",
		Attempts:   0,
		LastAttempt: now,
		CreatedAt:  now,
	}

	return delivery, nps.saveDeliveryRecord(delivery)
}

// SendToUser 发送消息给指定用户
func (nps *NewsPushService) SendToUser(userID string, message *models.PushMessage) error {
	if message.Target == nil {
		message.Target = &models.PushTarget{
			UserIDs: []string{userID},
		}
	}

	_, err := nps.SendPushMessage(message)
	return err
}

// SendToPortfolio 发送消息给投资组合用户
func (nps *NewsPushService) SendToPortfolio(portfolioID string, message *models.PushMessage) error {
	// 获取投资组合用户ID
	userIDs, err := nps.getPortfolioUsers(portfolioID)
	if err != nil {
		return fmt.Errorf("获取投资组合用户失败: %v", err)
	}

	if message.Target == nil {
		message.Target = &models.PushTarget{
			PortfolioIDs: []string{portfolioID},
			UserIDs:      userIDs,
		}
	}

	_, err = nps.SendPushMessage(message)
	return err
}

// SendToStockCode 发送消息给关注特定股票的用户
func (nps *NewsPushService) SendToStockCode(stockCode string, message *models.PushMessage) error {
	// 获取关注股票的用户
	userIDs, err := nps.getStockCodeUsers(stockCode)
	if err != nil {
		return fmt.Errorf("获取股票关注用户失败: %v", err)
	}

	if message.Target == nil {
		message.Target = &models.PushTarget{
			StockCodes: []string{stockCode},
			UserIDs:    userIDs,
		}
	}

	_, err = nps.SendPushMessage(message)
	return err
}

// processMessage 处理单个推送消息
func (nps *NewsPushService) processMessage(message *models.PushMessage) error {
	// 检查消息是否过期
	if message.ExpiresAt != nil && time.Now().After(*message.ExpiresAt) {
		return fmt.Errorf("消息已过期")
	}

	// 检查是否需要延迟推送
	if message.ScheduleAt != nil && time.Now().Before(*message.ScheduleAt) {
		// 加入延迟队列
		go func() {
			time.Sleep(time.Until(*message.ScheduleAt))
			nps.executePush(message)
		}()
		return nil
	}

	return nps.executePush(message)
}

// executePush 执行推送
func (nps *NewsPushService) executePush(message *models.PushMessage) error {
	// 选择推送提供商
	providers := nps.selectPushProviders(message.Target)

	var lastError error
	successCount := 0

	for _, providerID := range providers {
		provider, exists := nps.providers[providerID]
		if !exists || !provider.Enabled {
			continue
		}

		var err error
		switch provider.Type {
		case "websocket":
			err = nps.sendWebSocketPush(message, provider)
		case "sse":
			err = nps.sendSSEPush(message, provider)
		case "push_notification":
			err = nps.sendNotificationPush(message, provider)
		default:
			err = fmt.Errorf("不支持的推送类型: %s", provider.Type)
		}

		if err != nil {
			lastError = err
			nps.logger.Error("推送失败 %s: %v", provider.Name, err)
		} else {
			successCount++
		}
	}

	// 记录推送结果
	nps.recordPushResult(message, successCount, lastError)

	if successCount == 0 && lastError != nil {
		return lastError
	}

	return nil
}

// selectPushProviders 选择推送提供商
func (nps *NewsPushService) selectPushProviders(target *models.PushTarget) []string {
	// 按优先级排序的提供商
	var availableProviders []string
	for id, provider := range nps.providers {
		if provider.Enabled {
			availableProviders = append(availableProviders, id)
		}
	}

	// 根据目标类型选择合适的提供商
	if target != nil && len(target.DeviceType) > 0 {
		// 使用指定的设备类型
		return target.DeviceType
	}

	// 默认选择优先级最高的提供商
	if len(availableProviders) > 0 {
		return []string{availableProviders[0]}
	}

	return availableProviders
}

// sendWebSocketPush 发送WebSocket推送
func (nps *NewsPushService) sendWebSocketPush(message *models.PushMessage, provider *models.PushProvider) error {
	nps.mutex.RLock()
	defer nps.mutex.RUnlock()

	// 检查目标用户的连接状态
	if message.Target != nil && len(message.Target.UserIDs) > 0 {
		successCount := 0
		for _, userID := range message.Target.UserIDs {
			if conn, exists := nps.connections[userID]; exists && conn.IsActive {
				// 发送WebSocket消息
				data, _ := json.Marshal(map[string]interface{}{
					"type":    message.Type,
					"title":   message.Title,
					"content": message.Content,
					"data":    message.Data,
					"timestamp": time.Now().Unix(),
				})

				err := nps.sendWebSocketData(conn, data)
				if err != nil {
					nps.logger.Error("WebSocket发送失败: %v", err)
					continue
				}

				successCount++
			}
		}

		log.Printf("WebSocket推送成功，送达用户数: %d", successCount)
	}

	return nil
}

// sendSSEPush 发送Server-Sent Events推送
func (nps *NewsPushService) sendSSEPush(message *models.PushMessage, provider *models.PushProvider) error {
	// SSE推送实现
	log.Printf("发送SSE推送: %s", message.Title)
	return nil
}

// sendNotificationPush 发送推送通知
func (nps *NewsPushService) sendNotificationPush(message *models.PushMessage, provider *models.PushProvider) error {
	// APNs/FCM推送实现
	log.Printf("发送推送通知: %s", message.Title)
	return nil
}

// sendWebSocketData 发送WebSocket数据
func (nps *NewsPushService) sendWebSocketData(conn *models.WebSocketConnection, data []byte) error {
	// 这里需要根据实际的WebSocket库实现
	// 示例代码，实际需要调整
	conn.LastSeenAt = time.Now()

	// 模拟发送
	nps.logger.Debug("WebSocket发送数据给用户 %s", conn.UserID)
	return nil
}

// processPushQueue 处理推送队列
func (nps *NewsPushService) processPushQueue() {
	ticker := time.NewTicker(1 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			nps.queue.mutex.Lock()
			if len(nps.queue.messages) > 0 {
				// 批量处理队列中的消息
				batch := nps.queue.messages[:minInt(10, len(nps.queue.messages))]
				nps.queue.messages = nps.queue.messages[len(batch):]

				// 异步处理批次
				go nps.processBatch(batch)

				log.Printf("处理推送队列，批次大小: %d", len(batch))
			}
			nps.queue.mutex.Unlock()
		}
	}
}

// processBatch 批量处理消息
func (nps *NewsPushService) processBatch(messages []*models.PushMessage) {
	for _, message := range messages {
		if err := nps.processMessage(message); err != nil {
			nps.logger.Error("消息处理失败: %v", err)
			// 加入失败队列
			nps.queue.mutex.Lock()
			nps.queue.failed = append(nps.queue.failed, message)
			nps.queue.mutex.Unlock()
		}
	}
}

// schedulePeriodicTasks 调度周期性任务
func (nps *NewsPushService) schedulePeriodicTasks() {
	// 每日市场总结推送
	marketSummaryTicker := time.NewTicker(24 * time.Hour)
	defer marketSummaryTicker.Stop()

	for {
		select {
		case <-marketSummaryTicker.C:
			nps.sendDailyMarketSummary()
		}
	}
}

// sendDailyMarketSummary 发送每日市场总结
func (nps *NewsPushService) sendDailyMarketSummary() {
	// 获取市场数据
	marketData := nps.getMarketSummary()

	// 简化处理：使用默认数据
	upCount := 100
	downCount := 80
	flatCount := 20

	message := &models.PushMessage{
		ID:       fmt.Sprintf("daily_summary_%d", time.Now().Unix()),
		Type:     "analysis",
		Title:    "📊 每日市场分析报告",
		Content:  fmt.Sprintf("今日A股表现：\\n📈 上涨 %d 家\\n📉 下跌 %d 家\\n➡️ 平盘 %d 家", upCount, downCount, flatCount),
		Category: "analysis",
		Priority: "low",
		Data:     marketData,
		Target: &models.PushTarget{
			DeviceType: []string{"web", "mobile"},
			Online:     true,
		},
	}

	nps.SendPushMessage(message)
}

// getMarketSummary 获取市场总结数据
func (nps *NewsPushService) getMarketSummary() map[string]interface{} {
	// 模拟市场数据
	return map[string]interface{}{
		"up_count":   120,
		"down_count":  80,
		"flat_count":  20,
		"avg_change": 0.015,
		"top_gainers": []string{"000001", "000002", "000003"},
		"top_losers":  []string{"000999", "000998", "000997"},
		"volume_ratio": 1.2,
	}
}

// recordPushResult 记录推送结果
func (nps *NewsPushService) recordPushResult(message *models.PushMessage, successCount int, err error) {
	// 更新推送统计
	nps.analytics.TotalMessages++
	if successCount > 0 {
		nps.analytics.SuccessRate = float64(successCount) / float64(len(nps.providers))
	}

	// 记录推送日志
	log.Printf("推送完成 - 消息ID: %s, 成功数: %d, 错误: %v",
		message.ID, successCount, err)
}

// getPortfolioUsers 获取投资组合用户
func (nps *NewsPushService) getPortfolioUsers(portfolioID string) ([]string, error) {
	// 查询数据库获取投资组合用户
	query := `
		SELECT DISTINCT user_id
		FROM portfolio_users
		WHERE portfolio_id = ? AND is_active = 1
	`

	rows, err := nps.db.Query(query, portfolioID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var userIDs []string
	for rows.Next() {
		var userID string
		if err := rows.Scan(&userID); err != nil {
			continue
		}
		userIDs = append(userIDs, userID)
	}

	return userIDs, nil
}

// getStockCodeUsers 获取关注特定股票的用户
func (nps *NewsPushService) getStockCodeUsers(stockCode string) ([]string, error) {
	// 查询数据库获取关注股票的用户
	query := `
		SELECT DISTINCT user_id
		FROM user_stock_watchlist
		WHERE stock_code = ? AND is_active = 1
	`

	rows, err := nps.db.Query(query, stockCode)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var userIDs []string
	for rows.Next() {
		var userID string
		if err := rows.Scan(&userID); err != nil {
			continue
		}
		userIDs = append(userIDs, userID)
	}

	return userIDs, nil
}

// saveDeliveryRecord 保存送达记录
func (nps *NewsPushService) saveDeliveryRecord(delivery *models.PushDelivery) error {
	query := `
		INSERT INTO push_deliveries
		(id, message_id, user_id, device_type, status, attempts, last_attempt, error_code, error_msg, delivered_at, read_at, clicked_at, created_at)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
	`

	_, err := nps.db.Exec(query, delivery.ID, delivery.MessageID, delivery.UserID,
		delivery.DeviceType, delivery.Status, delivery.Attempts, delivery.LastAttempt,
		delivery.ErrorCode, delivery.ErrorMsg, delivery.DeliveredAt, delivery.ReadAt, delivery.ClickedAt)

	return err
}

// GetPushAnalytics 获取推送分析数据
func (nps *NewsPushService) GetPushAnalytics(days int) (*models.PushAnalytics, error) {
	// 实现推送分析统计
	return &models.PushAnalytics{
		Date:                time.Now().AddDate(0, 0, -days),
		TotalMessages:       nps.analytics.TotalMessages,
		SuccessRate:         nps.analytics.SuccessRate,
		ErrorRate:          nps.analytics.ErrorRate,
		ActiveConnections:   len(nps.connections),
	}, nil
}

// GetActiveConnections 获取活跃连接数
func (nps *NewsPushService) GetActiveConnections() int {
	nps.mutex.RLock()
	defer nps.mutex.RUnlock()

	activeCount := 0
	for _, conn := range nps.connections {
		if conn.IsActive {
			activeCount++
		}
	}

	return activeCount
}

// manageWebSocketConnections 管理WebSocket连接
func (nps *NewsPushService) manageWebSocketConnections() {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			nps.cleanupInactiveConnections()
		}
	}
}

// cleanupInactiveConnections 清理非活跃连接
func (nps *NewsPushService) cleanupInactiveConnections() {
	nps.mutex.Lock()
	defer nps.mutex.Unlock()

	now := time.Now()
	inactiveThreshold := 5 * time.Minute

	for userID, conn := range nps.connections {
		if !conn.IsActive || now.Sub(conn.LastSeenAt) > inactiveThreshold {
			delete(nps.connections, userID)
			log.Printf("清理非活跃连接: %s", userID)
		}
	}
}

// 辅助函数
func minInt(a, b int) int {
	if a < b {
		return a
	}
	return b
}