package integration

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"smart-stock-insider/main" // 假设主包中有路由设置
)

// TestAPIServer_HealthCheck 测试API服务器健康检查
func TestAPIServer_HealthCheck(t *testing.T) {
	// 启动测试服务器
	server := httptest.NewServer(main.SetupRouter())
	defer server.Close()

	// 发送健康检查请求
	resp, err := http.Get(server.URL + "/api/health")
	if err != nil {
		t.Fatalf("请求失败: %v", err)
	}
	defer resp.Body.Close()

	// 验证响应状态码
	if resp.StatusCode != http.StatusOK {
		t.Errorf("期望状态码 %d，实际 %d", http.StatusOK, resp.StatusCode)
	}

	// 解析响应
	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		t.Fatalf("解析响应失败: %v", err)
	}

	// 验证响应内容
	if result["success"] != true {
		t.Error("健康检查应该返回成功")
	}

	if result["data"] == nil {
		t.Error("健康检查应该返回数据")
	}
}

// TestAPIServer_GetStocks 测试获取股票列表
func TestAPIServer_GetStocks(t *testing.T) {
	server := httptest.NewServer(main.SetupRouter())
	defer server.Close()

	// 发送获取股票列表请求
	resp, err := http.Get(server.URL + "/api/stocks?limit=10&offset=0")
	if err != nil {
		t.Fatalf("请求失败: %v", err)
	}
	defer resp.Body.Close()

	// 验证响应状态码
	if resp.StatusCode != http.StatusOK {
		t.Errorf("期望状态码 %d，实际 %d", http.StatusOK, resp.StatusCode)
	}

	// 解析响应
	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		t.Fatalf("解析响应失败: %v", err)
	}

	// 验证响应结构
	if result["success"] != true {
		t.Error("应该返回成功状态")
	}

	data, ok := result["data"].(map[string]interface{})
	if !ok {
		t.Error("data字段应该存在")
	}

	stocks, ok := data["stocks"].([]interface{})
	if !ok {
		t.Error("stocks字段应该存在且为数组")
	}

	if len(stocks) > 10 {
		t.Error("股票数量应该不超过限制")
	}
}

// TestAPIServer_GetTechnicalSignals 测试获取技术信号
func TestAPIServer_GetTechnicalSignals(t *testing.T) {
	server := httptest.NewServer(main.SetupRouter())
	defer server.Close()

	// 发送获取技术信号请求
	resp, err := http.Get(server.URL + "/api/stocks/000001/signals")
	if err != nil {
		t.Fatalf("请求失败: %v", err)
	}
	defer resp.Body.Close()

	// 验证响应状态码
	if resp.StatusCode != http.StatusOK {
		t.Errorf("期望状态码 %d，实际 %d", http.StatusOK, resp.StatusCode)
	}

	// 解析响应
	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		t.Fatalf("解析响应失败: %v", err)
	}

	// 验证响应结构
	if result["success"] != true {
		t.Error("应该返回成功状态")
	}

	data, ok := result["data"].(map[string]interface{})
	if !ok {
		t.Error("data字段应该存在")
	}

	signals, ok := data["signals"].([]interface{})
	if !ok {
		t.Error("signals字段应该存在且为数组")
	}

	// 验证信号结构
	if len(signals) > 0 {
		signal, ok := signals[0].(map[string]interface{})
		if !ok {
			t.Error("信号应该是对象格式")
		}

		// 检查必要字段
		requiredFields := []string{"id", "code", "signal_type", "strength", "confidence"}
		for _, field := range requiredFields {
			if _, exists := signal[field]; !exists {
				t.Errorf("信号缺少必要字段: %s", field)
			}
		}
	}
}

// TestAPIServer_CreatePortfolio 测试创建投资组合
func TestAPIServer_CreatePortfolio(t *testing.T) {
	server := httptest.NewServer(main.SetupRouter())
	defer server.Close()

	// 准备请求数据
	requestData := map[string]interface{}{
		"name":        "测试组合",
		"description": "这是一个测试投资组合",
		"total_value": 1000000,
		"risk_level":  "moderate",
	}

	jsonData, _ := json.Marshal(requestData)

	// 发送POST请求
	resp, err := http.Post(
		server.URL+"/api/portfolios",
		"application/json",
		bytes.NewBuffer(jsonData),
	)
	if err != nil {
		t.Fatalf("请求失败: %v", err)
	}
	defer resp.Body.Close()

	// 验证响应状态码
	if resp.StatusCode != http.StatusCreated && resp.StatusCode != http.StatusOK {
		t.Errorf("期望状态码 %d 或 %d，实际 %d", http.StatusCreated, http.StatusOK, resp.StatusCode)
	}

	// 解析响应
	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		t.Fatalf("解析响应失败: %v", err)
	}

	// 验证响应结构
	if result["success"] != true {
		t.Error("应该返回成功状态")
	}

	data, ok := result["data"].(map[string]interface{})
	if !ok {
		t.Error("data字段应该存在")
	}

	// 检查返回的投资组合ID
	if data["id"] == nil {
		t.Error("应该返回投资组合ID")
	}
}

// TestAPIServer_GetNews 测试获取新闻
func TestAPIServer_GetNews(t *testing.T) {
	server := httptest.NewServer(main.SetupRouter())
	defer server.Close()

	// 发送获取新闻请求
	resp, err := http.Get(server.URL + "/api/news?limit=10&category=财经")
	if err != nil {
		t.Fatalf("请求失败: %v", err)
	}
	defer resp.Body.Close()

	// 验证响应状态码
	if resp.StatusCode != http.StatusOK {
		t.Errorf("期望状态码 %d，实际 %d", http.StatusOK, resp.StatusCode)
	}

	// 解析响应
	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		t.Fatalf("解析响应失败: %v", err)
	}

	// 验证响应结构
	if result["success"] != true {
		t.Error("应该返回成功状态")
	}

	data, ok := result["data"].(map[string]interface{})
	if !ok {
		t.Error("data字段应该存在")
	}

	news, ok := data["news"].([]interface{})
	if !ok {
		t.Error("news字段应该存在且为数组")
	}

	// 验证新闻结构
	if len(news) > 0 {
		newsItem, ok := news[0].(map[string]interface{})
		if !ok {
			t.Error("新闻项应该是对象格式")
		}

		// 检查必要字段
		requiredFields := []string{"id", "title", "source", "publish_time", "category"}
		for _, field := range requiredFields {
			if _, exists := newsItem[field]; !exists {
				t.Errorf("新闻项缺少必要字段: %s", field)
			}
		}
	}
}

// TestAPIServer_ErrorHandling 测试错误处理
func TestAPIServer_ErrorHandling(t *testing.T) {
	server := httptest.NewServer(main.SetupRouter())
	defer server.Close()

	testCases := []struct {
		url      string
		expected int
	}{
		{"/api/nonexistent", http.StatusNotFound},
		{"/api/stocks/invalid/signals", http.StatusBadRequest},
		{"/api/news?category=invalid", http.StatusBadRequest},
	}

	for _, tc := range testCases {
		resp, err := http.Get(server.URL + tc.url)
		if err != nil {
			t.Fatalf("请求失败: %v", err)
		}
		defer resp.Body.Close()

		if resp.StatusCode != tc.expected {
			t.Errorf("URL %s: 期望状态码 %d，实际 %d", tc.url, tc.expected, resp.StatusCode)
		}

		// 解析错误响应
		var result map[string]interface{}
		if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
			t.Fatalf("解析响应失败: %v", err)
		}

		if result["success"] != false {
			t.Errorf("错误响应的success字段应该为false，URL: %s", tc.url)
		}
	}
}

// TestAPIServer_ConcurrentRequests 测试并发请求
func TestAPIServer_ConcurrentRequests(t *testing.T) {
	server := httptest.NewServer(main.SetupRouter())
	defer server.Close()

	// 并发请求数量
	concurrentRequests := 50
	results := make(chan error, concurrentRequests)

	// 启动多个并发请求
	for i := 0; i < concurrentRequests; i++ {
		go func() {
			ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
			defer cancel()

			req, err := http.NewRequestWithContext(ctx, "GET", server.URL+"/api/health", nil)
			if err != nil {
				results <- err
				return
			}

			resp, err := http.DefaultClient.Do(req)
			if err != nil {
				results <- err
				return
			}
			defer resp.Body.Close()

			if resp.StatusCode != http.StatusOK {
				results <- fmt.Errorf("状态码错误: %d", resp.StatusCode)
				return
			}

			results <- nil
		}()
	}

	// 收集结果
	for i := 0; i < concurrentRequests; i++ {
		err := <-results
		if err != nil {
			t.Errorf("并发请求失败: %v", err)
		}
	}
}

// TestAPIServer_RequestTimeout 测试请求超时
func TestAPIServer_RequestTimeout(t *testing.T) {
	server := httptest.NewServer(main.SetupRouter())
	defer server.Close()

	// 创建超时上下文
	ctx, cancel := context.WithTimeout(context.Background(), 1*time.Millisecond)
	defer cancel()

	req, err := http.NewRequestWithContext(ctx, "GET", server.URL+"/api/stocks", nil)
	if err != nil {
		t.Fatalf("创建请求失败: %v", err)
	}

	// 发送请求（应该超时）
	resp, err := http.DefaultClient.Do(req)
	if err == nil {
		defer resp.Body.Close()
		t.Error("请求应该因为超时而失败")
	}

	if !isTimeoutError(err) {
		t.Errorf("期望超时错误，实际: %v", err)
	}
}

// isTimeoutError 检查是否为超时错误
func isTimeoutError(err error) bool {
	if err == nil {
		return false
	}

	if netErr, ok := err.(net.Error); ok && netErr.Timeout() {
		return true
	}

	return false
}

// TestAPIServer_CORS 测试CORS头
func TestAPIServer_CORS(t *testing.T) {
	server := httptest.NewServer(main.SetupRouter())
	defer server.Close()

	// 发送OPTIONS请求
	req, _ := http.NewRequest("OPTIONS", server.URL+"/api/stocks", nil)
	req.Header.Set("Origin", "http://localhost:3000")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		t.Fatalf("请求失败: %v", err)
	}
	defer resp.Body.Close()

	// 检查CORS头
	if resp.Header.Get("Access-Control-Allow-Origin") == "" {
		t.Error("应该设置Access-Control-Allow-Origin头")
	}

	if resp.Header.Get("Access-Control-Allow-Methods") == "" {
		t.Error("应该设置Access-Control-Allow-Methods头")
	}

	if resp.Header.Get("Access-Control-Allow-Headers") == "" {
		t.Error("应该设置Access-Control-Allow-Headers头")
	}
}