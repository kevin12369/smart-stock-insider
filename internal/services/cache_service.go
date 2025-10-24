package services

import (
	"context"
	"encoding/json"
	"fmt"
	"sync"
	"time"
)

// CacheItem 缓存项
type CacheItem struct {
	Value      interface{}
	Expiration time.Time
	CreatedAt  time.Time
	HitCount   int64
}

// CacheService 缓存服务
type CacheService struct {
	cache      map[string]*CacheItem
	mutex      sync.RWMutex
	maxSize    int
	ttl        time.Duration
	cleanupTicker *time.Ticker
	stats      *CacheStats
}

// CacheStats 缓存统计
type CacheStats struct {
	Hits      int64
	Misses    int64
	Sets      int64
	Deletes   int64
	Size      int
	MaxSize   int
	HitRate   float64
	mutex     sync.RWMutex
}

// NewCacheService 创建新的缓存服务
func NewCacheService(maxSize int, defaultTTL time.Duration) *CacheService {
	cs := &CacheService{
		cache:   make(map[string]*CacheItem),
		maxSize: maxSize,
		ttl:     defaultTTL,
		stats:   &CacheStats{MaxSize: maxSize},
	}

	// 启动清理任务
	cs.cleanupTicker = time.NewTicker(1 * time.Minute)
	go cs.cleanup()

	return cs
}

// Set 设置缓存
func (cs *CacheService) Set(key string, value interface{}, ttl ...time.Duration) {
	cs.mutex.Lock()
	defer cs.mutex.Unlock()

	// 如果缓存已满，删除最旧的项
	if len(cs.cache) >= cs.maxSize {
		cs.evictOldest()
	}

	expiration := time.Now().Add(cs.ttl)
	if len(ttl) > 0 {
		expiration = time.Now().Add(ttl[0])
	}

	cs.cache[key] = &CacheItem{
		Value:      value,
		Expiration: expiration,
		CreatedAt:  time.Now(),
		HitCount:   0,
	}

	cs.stats.recordSet()
}

// Get 获取缓存
func (cs *CacheService) Get(key string) (interface{}, bool) {
	cs.mutex.RLock()
	defer cs.mutex.RUnlock()

	item, exists := cs.cache[key]
	if !exists {
		cs.stats.recordMiss()
		return nil, false
	}

	// 检查是否过期
	if time.Now().After(item.Expiration) {
		// 异步删除过期项
		go cs.Delete(key)
		cs.stats.recordMiss()
		return nil, false
	}

	item.HitCount++
	cs.stats.recordHit()
	return item.Value, true
}

// GetWithTTL 获取缓存并返回剩余TTL
func (cs *CacheService) GetWithTTL(key string) (interface{}, time.Duration, bool) {
	cs.mutex.RLock()
	defer cs.mutex.RUnlock()

	item, exists := cs.cache[key]
	if !exists {
		cs.stats.recordMiss()
		return nil, 0, false
	}

	if time.Now().After(item.Expiration) {
		go cs.Delete(key)
		cs.stats.recordMiss()
		return nil, 0, false
	}

	ttl := time.Until(item.Expiration)
	item.HitCount++
	cs.stats.recordHit()
	return item.Value, ttl, true
}

// Delete 删除缓存
func (cs *CacheService) Delete(key string) bool {
	cs.mutex.Lock()
	defer cs.mutex.Unlock()

	if _, exists := cs.cache[key]; exists {
		delete(cs.cache, key)
		cs.stats.recordDelete()
		return true
	}
	return false
}

// Clear 清空所有缓存
func (cs *CacheService) Clear() {
	cs.mutex.Lock()
	defer cs.mutex.Unlock()

	cs.cache = make(map[string]*CacheItem)
}

// GetStats 获取缓存统计信息
func (cs *CacheService) GetStats() CacheStats {
	cs.stats.mutex.RLock()
	defer cs.stats.mutex.RUnlock()

	cs.stats.Size = len(cs.cache)
	cs.stats.HitRate = float64(cs.stats.Hits) / float64(cs.stats.Hits+cs.stats.Misses)

	return *cs.stats
}

// cleanup 定期清理过期缓存
func (cs *CacheService) cleanup() {
	for range cs.cleanupTicker.C {
		now := time.Now()
		keysToDelete := make([]string, 0)

		cs.mutex.RLock()
		for key, item := range cs.cache {
			if now.After(item.Expiration) {
				keysToDelete = append(keysToDelete, key)
			}
		}
		cs.mutex.RUnlock()

		for _, key := range keysToDelete {
			cs.Delete(key)
		}
	}
}

// evictOldest 驱逐最旧的缓存项
func (cs *CacheService) evictOldest() {
	var oldestKey string
	var oldestTime time.Time

	for key, item := range cs.cache {
		if oldestKey == "" || item.CreatedAt.Before(oldestTime) {
			oldestKey = key
			oldestTime = item.CreatedAt
		}
	}

	if oldestKey != "" {
		delete(cs.cache, oldestKey)
	}
}

// Close 关闭缓存服务
func (cs *CacheService) Close() {
	if cs.cleanupTicker != nil {
		cs.cleanupTicker.Stop()
	}
	cs.Clear()
}

// 记录统计信息的方法
func (s *CacheStats) recordHit() {
	s.mutex.Lock()
	defer s.mutex.Unlock()
	s.Hits++
}

func (s *CacheStats) recordMiss() {
	s.mutex.Lock()
	defer s.mutex.Unlock()
	s.Misses++
}

func (s *CacheStats) recordSet() {
	s.mutex.Lock()
	defer s.mutex.Unlock()
	s.Sets++
}

func (s *CacheStats) recordDelete() {
	s.mutex.Lock()
	defer s.mutex.Unlock()
	s.Deletes++
}

// 获取热门缓存项
func (cs *CacheService) GetTopHits(n int) []CacheItemInfo {
	cs.mutex.RLock()
	defer cs.mutex.RUnlock()

	items := make([]CacheItemInfo, 0, len(cs.cache))
	for key, item := range cs.cache {
		items = append(items, CacheItemInfo{
			Key:      key,
			HitCount: item.HitCount,
			CreatedAt: item.CreatedAt,
			TTL:      time.Until(item.Expiration),
		})
	}

	// 按命中率排序
	for i := 0; i < len(items)-1; i++ {
		for j := i + 1; j < len(items); j++ {
			if items[i].HitCount < items[j].HitCount {
				items[i], items[j] = items[j], items[i]
			}
		}
	}

	if len(items) > n {
		items = items[:n]
	}

	return items
}

// CacheItemInfo 缓存项信息
type CacheItemInfo struct {
	Key       string
	HitCount  int64
	CreatedAt time.Time
	TTL       time.Duration
}

// MarshalJSON 实现JSON序列化
func (s *CacheStats) MarshalJSON() ([]byte, error) {
	s.mutex.RLock()
	defer s.mutex.RUnlock()

	return json.Marshal(map[string]interface{}{
		"hits":      s.Hits,
		"misses":    s.Misses,
		"sets":      s.Sets,
		"deletes":   s.Deletes,
		"size":      "unknown", // 简化处理
		"maxSize":   s.MaxSize,
		"hitRate":   float64(s.Hits) / float64(s.Hits+s.Misses),
	})
}

// 全局缓存服务实例
var (
	DefaultCache *CacheService
	APICache     *CacheService
)

// InitCaches 初始化缓存服务
func InitCaches() {
	DefaultCache = NewCacheService(1000, 10*time.Minute) // 默认缓存：1000项，10分钟TTL
	APICache = NewCacheService(500, 5*time.Minute)     // API缓存：500项，5分钟TTL
}