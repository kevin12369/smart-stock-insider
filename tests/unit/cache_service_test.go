package unit

import (
	"context"
	"testing"
	"time"

	"smart-stock-insider/internal/services"
)

// TestCacheService_SetGet 测试缓存的设置和获取
func TestCacheService_SetGet(t *testing.T) {
	cache := services.NewCacheService(10, 5*time.Second)
	defer cache.Close()

	// 测试设置和获取
	cache.Set("test_key", "test_value")
	value, found := cache.Get("test_key")

	if !found {
		t.Error("缓存项未找到")
	}

	if value != "test_value" {
		t.Errorf("期望值 'test_value'，实际值 '%v'", value)
	}
}

// TestCacheService_Expiration 测试缓存过期
func TestCacheService_Expiration(t *testing.T) {
	cache := services.NewCacheService(10, 100*time.Millisecond)
	defer cache.Close()

	// 设置缓存项
	cache.Set("expire_test", "expire_value")

	// 立即获取应该成功
	value, found := cache.Get("expire_test")
	if !found {
		t.Error("缓存项应该存在")
	}
	if value != "expire_value" {
		t.Errorf("期望值 'expire_value'，实际值 '%v'", value)
	}

	// 等待过期
	time.Sleep(150 * time.Millisecond)

	// 再次获取应该失败
	_, found = cache.Get("expire_test")
	if found {
		t.Error("缓存项应该已过期")
	}
}

// TestCacheService_Delete 测试删除缓存项
func TestCacheService_Delete(t *testing.T) {
	cache := services.NewCacheService(10, 5*time.Second)
	defer cache.Close()

	// 设置缓存项
	cache.Set("delete_test", "delete_value")

	// 验证存在
	_, found := cache.Get("delete_test")
	if !found {
		t.Error("缓存项应该存在")
	}

	// 删除
	deleted := cache.Delete("delete_test")
	if !deleted {
		t.Error("删除操作应该成功")
	}

	// 验证已删除
	_, found = cache.Get("delete_test")
	if found {
		t.Error("缓存项应该已被删除")
	}
}

// TestCacheService_MaxSize 测试最大容量限制
func TestCacheService_MaxSize(t *testing.T) {
	cache := services.NewCacheService(2, 5*time.Second) // 最大2项
	defer cache.Close()

	// 添加3个缓存项，应该驱逐最旧的
	cache.Set("key1", "value1")
	cache.Set("key2", "value2")
	cache.Set("key3", "value3") // 应该驱逐key1

	// key1应该被驱逐
	_, found := cache.Get("key1")
	if found {
		t.Error("key1应该被驱逐")
	}

	// key2和key3应该存在
	_, found = cache.Get("key2")
	if !found {
		t.Error("key2应该存在")
	}

	_, found = cache.Get("key3")
	if !found {
		t.Error("key3应该存在")
	}
}

// TestCacheService_GetWithTTL 测试获取缓存和TTL
func TestCacheService_GetWithTTL(t *testing.T) {
	cache := services.NewCacheService(10, 1*time.Second)
	defer cache.Close()

	// 设置缓存项
	cache.Set("ttl_test", "ttl_value")

	// 获取缓存和TTL
	value, ttl, found := cache.GetWithTTL("ttl_test")
	if !found {
		t.Error("缓存项应该存在")
	}
	if value != "ttl_value" {
		t.Errorf("期望值 'ttl_value'，实际值 '%v'", value)
	}
	if ttl <= 0 {
		t.Error("TTL应该大于0")
	}

	// 等待过期
	time.Sleep(1100 * time.Millisecond)

	// 再次获取应该失败
	value, ttl, found = cache.GetWithTTL("ttl_test")
	if found {
		t.Error("缓存项应该已过期")
	}
	if ttl > 0 {
		t.Error("过期项的TTL应该为0")
	}
}

// TestCacheService_GetStats 测试缓存统计
func TestCacheService_GetStats(t *testing.T) {
	cache := services.NewCacheService(10, 5*time.Second)
	defer cache.Close()

	// 执行一些操作
	cache.Set("stat_test1", "value1")
	cache.Get("stat_test1")     // hit
	cache.Get("nonexistent")   // miss
	cache.Set("stat_test2", "value2")
	cache.Delete("stat_test2")

	stats := cache.GetStats()

	// 验证统计信息
	if stats.Hits != 1 {
		t.Errorf("期望命中数 1，实际 %d", stats.Hits)
	}
	if stats.Misses != 1 {
		t.Errorf("期望未命中数 1，实际 %d", stats.Misses)
	}
	if stats.Sets != 2 {
		t.Errorf("期望设置数 2，实际 %d", stats.Sets)
	}
	if stats.Deletes != 1 {
		t.Errorf("期望删除数 1，实际 %d", stats.Deletes)
	}
	if stats.Size != 1 {
		t.Errorf("期望当前大小 1，实际 %d", stats.Size)
	}
}

// TestCacheService_Clear 测试清空缓存
func TestCacheService_Clear(t *testing.T) {
	cache := services.NewCacheService(10, 5*time.Second)
	defer cache.Close()

	// 添加一些缓存项
	cache.Set("clear_test1", "value1")
	cache.Set("clear_test2", "value2")
	cache.Set("clear_test3", "value3")

	// 验证存在
	_, found := cache.Get("clear_test1")
	if !found {
		t.Error("缓存项应该存在")
	}

	// 清空缓存
	cache.Clear()

	// 验证所有缓存项都被清除
	items := []string{"clear_test1", "clear_test2", "clear_test3"}
	for _, key := range items {
		_, found := cache.Get(key)
		if found {
			t.Errorf("缓存项 %s 应该被清除", key)
		}
	}

	stats := cache.GetStats()
	if stats.Size != 0 {
		t.Errorf("缓存大小应该为0，实际 %d", stats.Size)
	}
}

// TestCacheService_ConcurrentAccess 测试并发访问
func TestCacheService_ConcurrentAccess(t *testing.T) {
	cache := services.NewCacheService(100, 5*time.Second)
	defer cache.Close()

	// 使用通道协调多个goroutine
	done := make(chan bool, 10)

	// 启动多个goroutine进行并发操作
	for i := 0; i < 10; i++ {
		go func(id int) {
			for j := 0; j < 100; j++ {
				key := fmt.Sprintf("key_%d_%d", id, j)
				value := fmt.Sprintf("value_%d_%d", id, j)

				// 设置
				cache.Set(key, value)

				// 获取
				cache.Get(key)

				// 偶尔删除
				if j%10 == 0 {
					cache.Delete(key)
				}
			}
			done <- true
		}(i)
	}

	// 等待所有goroutine完成
	for i := 0; i < 10; i++ {
		<-done
	}

	// 验证缓存没有崩溃
	stats := cache.GetStats()
	if stats.Hits < 0 || stats.Misses < 0 {
		t.Error("缓存统计信息异常")
	}
}

// BenchmarkCacheService_Set 基准测试：设置缓存
func BenchmarkCacheService_Set(b *testing.B) {
	cache := services.NewCacheService(10000, 5*time.Second)
	defer cache.Close()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		key := fmt.Sprintf("bench_key_%d", i)
		value := fmt.Sprintf("bench_value_%d", i)
		cache.Set(key, value)
	}
}

// BenchmarkCacheService_Get 基准测试：获取缓存
func BenchmarkCacheService_Get(b *testing.B) {
	cache := services.NewCacheService(10000, 5*time.Second)
	defer cache.Close()

	// 预填充缓存
	for i := 0; i < 1000; i++ {
		key := fmt.Sprintf("bench_key_%d", i)
		value := fmt.Sprintf("bench_value_%d", i)
		cache.Set(key, value)
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		key := fmt.Sprintf("bench_key_%d", i%1000)
		cache.Get(key)
	}
}