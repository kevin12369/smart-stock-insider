package performance

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"runtime"
	"sync"
	"testing"
	"time"

	"smart-stock-insider/main"
)

// LoadTestConfig 负载测试配置
type LoadTestConfig struct {
	ConcurrentUsers int
	Duration       time.Duration
	RampUpTime     time.Duration
	BaseURL        string
}

// TestResult 测试结果
type TestResult struct {
	TotalRequests     int64
	SuccessfulReqs   int64
	FailedReqs       int64
	AvgResponseTime  time.Duration
	MinResponseTime  time.Duration
	MaxResponseTime  time.Duration
	RequestsPerSec   float64
	ErrorRate        float64
	MemoryUsage      uint64
	GoroutinesCount  int
	Duration        time.Duration
}

// TestLoadPerformance_APIEndpoints 测试API端点的负载性能
func TestLoadPerformance_APIEndpoints(t *testing.T) {
	config := &LoadTestConfig{
		ConcurrentUsers: 50,
		Duration:       30 * time.Second,
		RampUpTime:     5 * time.Second,
		BaseURL:        "http://localhost:8080",
	}

	// 启动测试服务器
	server := httptest.NewServer(main.SetupRouter())
	defer server.Close()

	// 更新基础URL
	config.BaseURL = server.URL

	endpoints := []string{
		"/api/health",
		"/api/stocks?limit=20&offset=0",
		"/api/stocks/000001/signals",
		"/api/news?limit=10",
	}

	for _, endpoint := range endpoints {
		t.Run("Endpoint_"+endpoint, func(t *testing.T) {
			result := runLoadTest(t, config, endpoint)
			printTestResults(t, endpoint, result)

			// 性能断言
			validatePerformance(t, result)
		})
	}
}

// runLoadTest 执行负载测试
func runLoadTest(t *testing.T, config *LoadTestConfig, endpoint string) *TestResult {
	fmt.Printf("开始负载测试: %s (并发用户: %d, 持续时间: %v)\n",
		endpoint, config.ConcurrentUsers, config.Duration)

	result := &TestResult{
		MinResponseTime: time.Hour, // 初始化为很大的值
		StartTime:       time.Now(),
	}

	var (
		wg               sync.WaitGroup
		requestTimes      []time.Duration
		requestTimesMutex sync.Mutex
		successCount     int64
		failCount       int64
	)

	// 分阶段启动并发用户
	usersPerRamp := config.ConcurrentUsers / 5
	for phase := 0; phase < 5; phase++ {
		for i := 0; i < usersPerRamp; i++ {
			wg.Add(1)
			go func() {
				defer wg.Done()
				runUserRequests(config, endpoint, &requestTimes, &requestTimesMutex, &successCount, &failCount)
			}()
		}
		time.Sleep(config.RampUpTime / 5)
	}

	// 等待所有用户完成
	wg.Wait()

	// 计算统计结果
	result.TotalRequests = successCount + failCount
	result.SuccessfulReqs = successCount
	result.FailedReqs = failCount
	result.Duration = time.Since(result.StartTime)
	result.RequestsPerSec = float64(result.TotalRequests) / result.Duration.Seconds()
	result.ErrorRate = float64(failCount) / float64(result.TotalRequests)

	if len(requestTimes) > 0 {
		var totalTime time.Duration
		for _, t := range requestTimes {
			totalTime += t
			if t < result.MinResponseTime {
				result.MinResponseTime = t
			}
			if t > result.MaxResponseTime {
				result.MaxResponseTime = t
			}
		}
		result.AvgResponseTime = totalTime / time.Duration(len(requestTimes))
	}

	// 获取内存和goroutine信息
	var m runtime.MemStats
	runtime.ReadMemStats(&m)
	result.MemoryUsage = m.Alloc
	result.GoroutinesCount = runtime.NumGoroutine()

	return result
}

// runUserRequests 运行单个用户的请求
func runUserRequests(config *LoadTestConfig, endpoint string,
	requestTimes *[]time.Duration, mutex *sync.Mutex, successCount, failCount *int64) {

	client := &http.Client{
		Timeout: 10 * time.Second,
	}

	endTime := time.Now().Add(config.Duration)

	for time.Now().Before(endTime) {
		start := time.Now()

		resp, err := client.Get(config.BaseURL + endpoint)
		responseTime := time.Since(start)

		if err != nil {
			// 使用原子操作更新失败计数
			*failCount++
			continue
		}

		// 读取响应体（确保完整请求）
		ioutil.ReadAll(resp.Body)
		resp.Body.Close()

		if resp.StatusCode >= 200 && resp.StatusCode < 400 {
			*successCount++

			// 记录响应时间
			mutex.Lock()
			*requestTimes = append(*requestTimes, responseTime)
			mutex.Unlock()
		} else {
			*failCount++
		}

		// 请求间隔，避免过快
		time.Sleep(10 * time.Millisecond)
	}
}

// printTestResults 打印测试结果
func printTestResults(t *testing.T, endpoint string, result *TestResult) {
	fmt.Printf("\n=== 负载测试结果: %s ===\n", endpoint)
	fmt.Printf("总请求数:     %d\n", result.TotalRequests)
	fmt.Printf("成功请求数:   %d\n", result.SuccessfulReqs)
	fmt.Printf("失败请求数:   %d\n", result.FailedReqs)
	fmt.Printf("错误率:       %.2f%%\n", result.ErrorRate*100)
	fmt.Printf("平均响应时间: %v\n", result.AvgResponseTime)
	fmt.Printf("最小响应时间: %v\n", result.MinResponseTime)
	fmt.Printf("最大响应时间: %v\n", result.MaxResponseTime)
	fmt.Printf("每秒请求数:   %.2f\n", result.RequestsPerSec)
	fmt.Printf("内存使用:     %.2f MB\n", float64(result.MemoryUsage)/1024/1024)
	fmt.Printf("Goroutine数:  %d\n", result.GoroutinesCount)
	fmt.Printf("测试持续时间: %v\n", result.Duration)
	fmt.Println("========================")
}

// validatePerformance 验证性能指标
func validatePerformance(t *testing.T, result *TestResult) {
	// 基本性能要求
	if result.ErrorRate > 0.05 { // 错误率不超过5%
		t.Errorf("错误率过高: %.2f%% (期望 <= 5%%)", result.ErrorRate*100)
	}

	if result.AvgResponseTime > 2*time.Second { // 平均响应时间不超过2秒
		t.Errorf("平均响应时间过长: %v (期望 <= 2s)", result.AvgResponseTime)
	}

	if result.MaxResponseTime > 10*time.Second { // 最大响应时间不超过10秒
		t.Errorf("最大响应时间过长: %v (期望 <= 10s)", result.MaxResponseTime)
	}

	if result.RequestsPerSec < 10 { // 每秒请求数不低于10
		t.Errorf("吞吐量过低: %.2f req/s (期望 >= 10 req/s)", result.RequestsPerSec)
	}

	// 内存使用检查
	if result.MemoryUsage > 100*1024*1024 { // 内存使用不超过100MB
		t.Errorf("内存使用过高: %.2f MB (期望 <= 100 MB)",
			float64(result.MemoryUsage)/1024/1024)
	}
}

// BenchmarkAPI_HealthCheck 健康检查API基准测试
func BenchmarkAPI_HealthCheck(b *testing.B) {
	server := httptest.NewServer(main.SetupRouter())
	defer server.Close()

	client := &http.Client{Timeout: 5 * time.Second}

	b.ResetTimer()
	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			resp, err := client.Get(server.URL + "/api/health")
			if err != nil {
				b.Error(err)
				continue
			}
			ioutil.ReadAll(resp.Body)
			resp.Body.Close()
		}
	})
}

// BenchmarkAPI_GetStocks 获取股票列表API基准测试
func BenchmarkAPI_GetStocks(b *testing.B) {
	server := httptest.NewServer(main.SetupRouter())
	defer server.Close()

	client := &http.Client{Timeout: 5 * time.Second}

	b.ResetTimer()
	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			resp, err := client.Get(server.URL + "/api/stocks?limit=20")
			if err != nil {
				b.Error(err)
				continue
			}
			ioutil.ReadAll(resp.Body)
			resp.Body.Close()
		}
	})
}

// TestMemoryUsage_ExtendedOperation 测试扩展操作期间的内存使用
func TestMemoryUsage_ExtendedOperation(t *testing.T) {
	// 记录初始内存状态
	var initialMem, peakMem runtime.MemStats
	runtime.ReadMemStats(&initialMem)
	peakMem = initialMem

	// 模拟扩展操作（持续5分钟）
	duration := 5 * time.Minute
	ticker := time.NewTicker(10 * time.Second)
	defer ticker.Stop()

	ctx, cancel := context.WithTimeout(context.Background(), duration)
	defer cancel()

	operationCount := 0

	for {
		select {
		case <-ctx.Done():
			break
		case <-ticker.C:
			// 执行一些操作
			performMemoryIntensiveOperation()
			operationCount++

			// 检查内存使用
			var currentMem runtime.MemStats
			runtime.ReadMemStats(&currentMem)

			if currentMem.Alloc > peakMem.Alloc {
				peakMem = currentMem
			}

			t.Logf("操作 %d: 当前内存 %.2f MB, 峰值内存 %.2f MB",
				operationCount,
				float64(currentMem.Alloc)/1024/1024,
				float64(peakMem.Alloc)/1024/1024)
		}
	}

	// 验证内存泄漏
	runtime.GC() // 强制垃圾回收
	time.Sleep(1 * time.Second)

	var finalMem runtime.MemStats
	runtime.ReadMemStats(&finalMem)

	memoryIncrease := finalMem.Alloc - initialMem.Alloc
	memoryIncreaseMB := float64(memoryIncrease) / 1024 / 1024

	t.Logf("初始内存: %.2f MB", float64(initialMem.Alloc)/1024/1024)
	t.Logf("最终内存: %.2f MB", float64(finalMem.Alloc)/1024/1024)
	t.Logf("峰值内存: %.2f MB", float64(peakMem.Alloc)/1024/1024)
	t.Logf("内存增长: %.2f MB", memoryIncreaseMB)

	// 内存增长不应该超过50MB
	if memoryIncreaseMB > 50 {
		t.Errorf("检测到可能的内存泄漏，增长: %.2f MB", memoryIncreaseMB)
	}
}

// performMemoryIntensiveOperation 执行内存密集型操作
func performMemoryIntensiveOperation() {
	// 分配一些内存然后释放
	data := make([][]byte, 100)
	for i := range data {
		data[i] = make([]byte, 1024)
		// 填充一些数据
		for j := range data[i] {
			data[i][j] = byte(i + j)
		}
	}

	// 模拟处理
	time.Sleep(100 * time.Millisecond)

	// 释放内存（GC会处理）
	data = nil
}

// TestConcurrentDatabaseOperations 测试并发数据库操作性能
func TestConcurrentDatabaseOperations(t *testing.T) {
	// 这里需要实际的数据库连接
	// db := setupTestDatabase()
	// defer db.Close()

	concurrentOperations := 100
	operationsPerWorker := 50

	var wg sync.WaitGroup
	startTime := time.Now()

	// 启动多个worker进行并发数据库操作
	for i := 0; i < concurrentOperations; i++ {
		wg.Add(1)
		go func(workerID int) {
			defer wg.Done()

			for j := 0; j < operationsPerWorker; j++ {
				// 执行数据库操作（这里需要根据实际数据库操作实现）
				performDatabaseOperation(workerID, j)
			}
		}(i)
	}

	wg.Wait()
	duration := time.Since(startTime)

	totalOperations := concurrentOperations * operationsPerWorker
	opsPerSecond := float64(totalOperations) / duration.Seconds()

	t.Logf("并发数据库操作测试完成:")
	t.Logf("总操作数: %d", totalOperations)
	t.Logf("耗时: %v", duration)
	t.Logf("每秒操作数: %.2f", opsPerSecond)

	// 性能断言
	if opsPerSecond < 1000 {
		t.Errorf("数据库操作性能过低: %.2f ops/s (期望 >= 1000 ops/s)", opsPerSecond)
	}
}

// performDatabaseOperation 执行数据库操作
func performDatabaseOperation(workerID, operationID int) {
	// 这里需要实现具体的数据库操作
	// 例如：查询、插入、更新等
	// 为了演示，这里只是模拟延迟
	time.Sleep(time.Microsecond * time.Duration(100+workerID*10))
}