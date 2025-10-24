# 新闻推送功能文档

## 概述

智股通新闻推送功能提供实时、智能、个性化的消息推送服务，支持多种推送渠道和自定义推送策略，为用户提供及时的市场信息和投资建议。

## 核心特性

### 1. 多渠道推送支持

#### WebSocket实时推送
- **实时性**: 毫秒级延迟
- **双向通信**: 支持客户端与服务端交互
- **连接管理**: 自动检测连接状态
- **消息广播**: 支持群组消息推送
- **心跳机制**: 保持连接活跃状态

#### Server-Sent Events (SSE)
- **单向推送**: 从服务器到客户端的实时推送
- **事件流**: 支持多种事件类型
- **自动重连**: 断线后自动重连机制
- **兼容性**: 良好的浏览器支持

#### 推送通知
- **APNs**: Apple Push Notification Service集成
- **FCM**: Firebase Cloud Messaging集成
- **华为推送**: 华为HMS服务
- **小米推送**: 小米推送服务
- **OPPO推送**: OPPO推送服务
- **Vivo推送**: Vivo推送服务

### 2. 智能推送策略

#### 规则引擎
- **多维度触发器**: 新闻重要性、价格变动、时间事件、用户行为
- **条件逻辑**: 支持AND/OR/NOT组合
- **动作定义**: 发送消息、创建预警、更新订阅
- **优先级管理**: 高、中、低优先级分级
- **动态激活**: 基于时间和条件的自动启用/禁用

#### 模板系统
- **动态模板**: 支持变量替换和多语言
- **场景化模板**: 新闻突发、价格预警、技术信号、市场分析
- **A/B测试**: 支持推送效果测试和优化
- **个性化内容**: 基于用户偏好的个性化推送

### 3. 用户订阅管理

#### 细粒度控制
- **推送类型**: 新闻、预警、分析、投资组合更新
- **内容过滤**: 按分类、关键词、来源、重要性
- **频率控制**: 实时、每小时、每日、每周、从不
- **时段设置**: 支持勿扰时段设置
- **设备管理**: 支持多设备登录和同步

#### 偏好设置
- **勿扰模式**: 完全关闭或仅紧急消息
- **时段设置**: 工作时间勿扰
- **频率限制**: 每日最大推送数量限制
- **内容偏好**: 用户感兴趣的投资主题和技术指标

### 4. 分析与统计

#### 推送分析
- **送达率**: 实时监控各渠道推送成功率
- **阅读率**: 推送消息的阅读情况分析
- **点击率**: 推送内容的点击转化率分析
- **转化漏斗**: 从推送到点击的转化路径分析
- **设备统计**: 不同设备和系统的推送表现

#### 用户行为分析
- **活跃时段**: 分析用户最活跃的推送时段
- **内容偏好**: 分析用户最关注的推送内容
- **地域分布**: 分析不同地区用户的推送响应

## API接口

### 推送服务管理

#### 启动推送服务
```go
result := app.StartPushService()
```

**返回**:
```json
{
  "success": true,
  "message": "推送服务启动成功"
}
```

#### 发送推送消息
```go
result := app.SendNewsPush({
  "type": "news",
  "title": "📰 重要新闻",
  "content": "平安银行发布财报预告",
  "priority": "high",
  "target": {
    "user_ids": ["user_001", "user_002"],
    "stock_codes": ["000001", "000002"],
    "sectors": ["金融", "银行"]
  },
  "data": {
    "news_id": "news_123456",
    "importance": 0.9
    "urgency": "high"
  }
})
```

#### 用户订阅
```go
result := app.SubscribeNews({
  "user_id": "user_001",
  "device_type": "mobile",
  "device_token": "device_token_abc123",
  "subscriptions": ["news", "alerts", "analysis"],
  "enabled": true,
  "preferences": {
    "news": {
      "enabled": true,
      "categories": ["breaking", "major"],
      "frequency": "realtime",
      "max_per_day": 20
    }
  }
})
```

### 推送分析
```go
result := app.GetPushAnalytics(7) // 最近7天
```

**返回**:
```json
{
  "success": true,
  "data": {
    "total_messages": 1250,
    "success_rate": 0.92,
    "read_rate": 0.45,
    "click_rate": 0.12,
    "active_connections": 850,
    "device_breakdown": {
      "web": 400,
      "mobile": 300,
      "desktop": 150
    }
  }
}
```

### 连接状态
```go
result := app.GetActiveConnections()
```

**返回**:
```json
{
  "success": true,
  "data": 850
}
```

## 推送消息类型

### 新闻推送
- **突发新闻**: 高重要性新闻立即推送
- **市场分析**: 每日市场总结推送
- **个股快讯**: 用户关注股票的重要新闻推送
- **研究报告**: 深度分析报告推送

### 价格预警
- **涨跌幅预警**: 趨跌幅达到设定值时推送
- **价格突破预警**: 价格突破关键价位时推送
- **成交量异常**: 成交量异常变化时推送

### 投资组合更新
- **收益提醒**: 投资组合收益达到设定值时推送
- **再平衡提醒**: 投资组合需要再平衡时推送
- **风险预警**: 投资组合风险指标异常时推送

### 分析推送
- **技术信号**: 技术指标产生买卖信号时推送
- **基本面分析**: 基本面数据变化时推送
- **AI建议**: AI分析生成投资建议时推送

## 推送规则配置

### 新闻规则
```json
{
  "high_impact_news": {
    "trigger": {
      "type": "news",
      "conditions": {
        "relevance": ">= 0.8",
        "categories": ["breaking", "major"],
        "sources": ["xinhua", "caixin"]
      }
    },
    "action": {
      "type": "send_message",
      "template": "news_breakout",
      "priority": "high"
    }
  }
}
```

### 价格规则
```json
{
  "price_movement_alert": {
    "trigger": {
      "type": "price",
      "conditions": {
        "abs_change_pct": "> 0.05"
      }
    },
    "action": {
      "type": "send_message",
      "template": "price_alert",
      "priority": "medium"
    }
  }
}
```

### 时间规则
```json
{
  "daily_summary": {
    "trigger": {
      "type": "time",
      "conditions": {
        "trigger_time": "15:30",
        "trigger_days": [1, 2, 3, 4, 5]
      }
    },
    "action": {
      "type": "send_message",
      "template": "market_analysis",
      "priority": "low"
    }
  }
}
```

## 推送模板

### 新闻突发模板
```json
{
  "id": "news_breakout",
  "name": "新闻突发",
  "type": "news",
  "title": "📰 {{.StockName}} 重要通知",
  "content": "{{.Title}}\\n\\n{{.Summary}}\\n\\n点击查看详情",
  "summary": "{{.StockCode}}: {{.Title}}",
  "variables": ["StockName", "Title", "Summary", "StockCode"]
}
}
```

### 价格预警模板
```json
{
  "id": "price_alert",
  "name": "价格预警",
  "type": "alert",
  "title": "💰 {{.StockName}} 价格预警",
  "content": "当前价格：¥{{.CurrentPrice}}\\n目标价格：¥{{.TargetPrice}}\\n变动：{{.ChangePct}}%",
  "variables": ["StockName", "CurrentPrice", "TargetPrice", "ChangePct"]
}
```

### 技术信号模板
```json
{
  "id": "technical_signal",
  "name": "技术信号",
  "type": "analysis",
  "title": "📈 {{.StockName}} 技术分析信号",
  "content": "{{.SignalName}}\\n价格：¥{{.Price}}\\n建议：{{.Recommendation}}",
  "variables": ["StockName", "SignalName", "Price", "Recommendation"]
}
```

## 数据模型

### PushMessage (推送消息)
```json
{
  "id": "msg_20240101000001",
  "type": "news",
  "title": "重要新闻通知",
  "content": "消息内容",
  "summary": "消息摘要",
  "url": "https://example.com/news/123",
  "image_url": "https://example.com/image.jpg",
  "category": "breaking",
  "priority": "high",
  "tags": ["urgent", "market"],
  "data": {"custom_key": "custom_value"},
  "target": {
    "user_ids": ["user_001"],
    "stock_codes": ["000001"],
    "sectors": ["金融"]
  },
  "created_at": "2024-01-01T10:00:00Z",
  "delivered": false,
  "read": false,
  "clicked": false
}
```

### PushSubscription (推送订阅)
```json
{
  "id": "sub_001",
  "user_id": "user_001",
  "device_type": "mobile",
  "device_token": "abcd1234",
  "subscriptions": ["news", "alerts"],
  "preferences": {
    "news": {
      "enabled": true,
      "categories": ["breaking", "major", "analysis"],
      "frequency": "realtime"
    }
  },
  "is_active": true,
  "last_activity_at": "2024-01-01T10:00:00Z"
}
```

### PushAnalytics (推送分析)
```json
{
  "date": "2024-01-01",
  "total_messages": 1250,
  "news_messages": 800,
  "alert_messages": 300,
  "analysis_messages": 150,
  "portfolio_messages": 100,
  "success_rate": 0.92,
  "read_rate": 0.45,
  "click_rate": 0.12,
  "device_breakdown": {
    "web": 400,
    "mobile": 300,
    "desktop": 150
  }
}
```

## 技术实现

### WebSocket服务
```go
// 连接管理
type WebSocketManager struct {
    connections map[string]*WebSocketConnection
    mutex      sync.RWMutex
    broadcast  chan []byte
}

// 连接处理
func (wsm *WebSocketManager) HandleConnection(conn *websocket.Conn, userID string) {
    wsm.mutex.Lock()
    defer wsm.mutex.Unlock()

    connection := &WebSocketConnection{
        ID:          generateID(),
        UserID:      userID,
        Conn:         conn,
        ConnectedAt:  time.Now(),
        LastSeenAt:   time.Now(),
        IsActive:     true,
    }

    wsm.connections[userID] = connection

    // 发送欢迎消息
    welcome := map[string]interface{}{
        "type": "system",
        "message": "WebSocket连接成功",
    }
    data, _ := json.Marshal(welcome)
    conn.WriteMessage(data)
}

// 消息广播
func (wsm *WebSocketManager) Broadcast(message interface{}) error {
    wsm.mutex.RLock()
    defer wsm.mutex.Unlock()

    data, _ := json.Marshal(message)
    for _, conn := range wsm.connections {
        if conn.IsActive {
            conn.Conn.WriteMessage(data)
        }
    }

    return nil
}
```

### 推送队列处理
```go
// 批量处理
func processQueue() {
    ticker := time.NewTicker(1 * time.Second)
    defer ticker.Stop()

    for {
        case <-ticker.C:
            // 批量处理队列中的消息
            batch := getBatchFromQueue()
            go processBatch(batch)
    }
    }
}
```

## 使用示例

### 前端集成
```javascript
// WebSocket连接
const ws = new WebSocket('wss://api.example.com/push')

ws.onmessage = function(event) {
    const message = JSON.parse(event.data)
    handlePushMessage(message)
}

// 处理推送消息
function handlePushMessage(message) {
    if (message.type === 'alert') {
        showNotification(message.title, message.content)
        playNotificationSound()
    }

    if (message.type === 'news') {
        updateNewsFeed(message.content)
    }
}

// 订阅推送
function subscribePush() {
    const subscription = {
        user_id: currentUserId,
        device_type: getDeviceType(),
        subscriptions: ['news', 'alerts']
    }

    fetch('/api/push/subscribe', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(subscription)
    }).then(response => {
        if (response.ok) {
            console.log('订阅成功')
        }
    })
}
```

### 移动端APNs集成
```swift
// AppDelegate.swift
import UserNotifications

class AppDelegate: UIResponder, UNUserNotificationCenterDelegate {
    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        // 注册推送token
        UNUserNotificationCenter.current().requestAuthorization(options: [UNAuthorizationOption.alert, UNAuthorizationOption.sound, UNAuthorizationOption.carPlayAlert, UNAuthorizationOption.provisional]) { (granted, error) in
            if error != nil {
                print("推送授权失败: \(error.localizedDescription)")
            }
        }
        return true
    }

    // 处理推送消息
    func userNotificationCenter(_ center: UNUserNotificationCenter, willPresent notification: UNNotification, withCompletionHandler: nil) -> Bool {
        // 显示推送通知
        let userInfo = notification.request.content.userInfo

        // 记录推送事件
        logPushEvent(notification.identifier, 'delivered', userInfo)

        // 处理点击事件
        completionHandler?(nil)

        return true
    }
}
```

### FCM集成
```javascript
// 前端FCM配置
const firebaseConfig = {
  apiKey: "your-fcm-server-key",
  messagingSenderId: "your-sender-id",
  serviceAccount: "your-project-id"
}

// 发送FCM推送
async function sendFCMNotification(token, message) {
    const response = await fetch('https://fcm.googleapis.com/fcm/send', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            to: token,
            notification: {
                title: message.title,
                body: message.content,
                icon: message.icon,
                click_action: message.url
            },
            data: message.data
        })
    })
    }

    return response.ok
}
```

## 配置管理

### 推送配置文件
```json
{
  "push_config": {
    "enabled": true,
    "providers": {
      "websocket": {
        "enabled": true,
        "config": {},
        "rate_limit": 0
      },
      "sse": {
        "enabled": true,
        "config": {},
        "rate_limit": 1000
      },
      "apns": {
        "enabled": false,
        "config": {
          "team_id": "your-team-id",
          "key_id": "your-key-id"
        },
        "rate_limit": 100,
        "credentials_file": "apns_cert.p8"
      },
      "fcm": {
        "enabled": false,
        "config": {
          "server_key": "your-server-key"
        },
        "rate_limit": 100,
        "credentials_file": "fcm_service_account.json"
      }
    }
    },
    "rules": {
      "urgent_news": {
        "enabled": true,
        "conditions": {
          "relevance": ">= 0.8"
        },
        "priority": 1
      },
      "price_movement": {
        "enabled": true,
        "conditions": {
          "change_pct": "> 5%"
        },
        "priority": 2
      }
    }
  },
    "templates": {
      "news_breakout": {
        "enabled": true
      },
      "price_alert": {
        "enabled": true
      }
    }
    }
  },
    "analytics": {
      "retention_days": 7,
      "cleanup_interval": "24h"
    }
  }
  }
}
```

## 安全考虑

### 1. 数据安全
- **用户隐私**: 最小化收集用户数据
- **加密存储**: 敏感信息加密存储
- **权限控制**: 严格的访问权限管理
- **数据脱敏**: 个人信息脱敏处理

### 2. 推送安全
- **消息验证**: 严格的推送消息验证
- **防滥用**: 限制单用户推送频率
- **内容审核**: 推送内容自动审核
- **来源认证**: 验证推送来源合法性

### 3. 性能安全
- **频率限制**: 严格的推送频率限制
- **异步处理**: 所有推送操作异步执行
- **错误处理**: 完善的错误处理和降级机制
- **监控报警**: 异常情况自动报警

## 扩展规划

### 短期扩展
- **更多推送渠道**: 集成更多主流推送服务
- **AI个性化**: 基于用户行为的个性化推送
- **地理位置**: 基于位置的精准推送

### 中期扩展
- **富媒体推送**: 支持图片、视频、音频推送
- **交互式推送**: 支持快速回复和操作按钮
- **离线推送**: 支持应用未打开时的离线推送队列

### 长期规划
- **智能推送**: 基于机器学习的智能推送时机
- **跨平台统一**: 统一各平台的推送体验
- **推送效果优化**: A/B测试和效果优化平台

---

*最后更新: 2024年1月*