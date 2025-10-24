package utils

import (
	"context"
	"runtime"
	"sync"
	"time"
)

// MemoryManager 内存管理器
type MemoryManager struct {
	mutex            sync.RWMutex
	maxMemoryUsage   uint64        // 最大内存使用量（字节）
	currentUsage     uint64        // 当前内存使用量
	allocations      map[string]*AllocationInfo // 内存分配记录
	gcThreshold      float64       // GC触发阈值
	lastGCTime       time.Time      // 上次GC时间
	stats            *MemoryStats
	monitorTicker    *time.Ticker
	ctx              context.Context
	cancel           context.CancelFunc
}

// AllocationInfo 分配信息
type AllocationInfo struct {
	Tag        string    // 分配标签
	Size       uint64    // 分配大小
	AllocTime  time.Time // 分配时间
	AccessTime time.Time // 最后访问时间
}

// MemoryStats 内存统计
type MemoryStats struct {
	TotalAllocations uint64    // 总分配次数
	TotalFreed      uint64    // 总释放次数
	PeakUsage      uint64    // 峰值内存使用
	CurrentUsage    uint64    // 当前内存使用量
	GCCount        uint64    // GC执行次数
	LastGCAt       time.Time // 上次GC时间
	mutex          sync.RWMutex
}

// MemoryConfig 内存配置
type MemoryConfig struct {
	MaxMemoryMB    uint64  // 最大内存使用量（MB）
	GCThreshold    float64  // GC触发阈值（0-1）
	MonitorInterval time.Duration // 监控间隔
}

// DefaultMemoryConfig 默认内存配置
func DefaultMemoryConfig() *MemoryConfig {
	return &MemoryConfig{
		MaxMemoryMB:    512,  // 512MB
		GCThreshold:    0.8,  // 80%时触发GC
		MonitorInterval: 30 * time.Second,
	}
}

// NewMemoryManager 创建内存管理器
func NewMemoryManager(config *MemoryConfig) *MemoryManager {
	if config == nil {
		config = DefaultMemoryConfig()
	}

	ctx, cancel := context.WithCancel(context.Background())

	mm := &MemoryManager{
		maxMemoryUsage:   config.MaxMemoryMB * 1024 * 1024,
		gcThreshold:      config.GCThreshold,
		allocations:      make(map[string]*AllocationInfo),
		stats:            &MemoryStats{},
		monitorTicker:    time.NewTicker(config.MonitorInterval),
		ctx:              ctx,
		cancel:           cancel,
	}

	// 启动内存监控
	go mm.monitorMemory()

	return mm
}

// Allocate 分配内存
func (mm *MemoryManager) Allocate(tag string, size uint64) (interface{}, error) {
	mm.mutex.Lock()
	defer mm.mutex.Unlock()

	// 检查内存限制
	if mm.currentUsage+size > mm.maxMemoryUsage {
		// 尝试触发GC释放内存
		mm.forceGC()

		// 再次检查
		if mm.currentUsage+size > mm.maxMemoryUsage {
			return nil, &MemoryError{
				Type:    "OutOfMemory",
				Message: "内存不足，无法分配",
				Current: mm.currentUsage,
				Max:     mm.maxMemoryUsage,
			}
		}
	}

	// 记录分配信息
	mm.allocations[tag] = &AllocationInfo{
		Tag:        tag,
		Size:       size,
		AllocTime:  time.Now(),
		AccessTime: time.Now(),
	}

	mm.currentUsage += size
	mm.stats.recordAllocation(size)

	return &ManagedMemory{
		manager: mm,
		tag:     tag,
		size:    size,
		data:     make([]byte, size), // 实际内存分配
	}, nil
}

// Release 释放内存
func (mm *MemoryManager) Release(tag string) {
	mm.mutex.Lock()
	defer mm.mutex.Unlock()

	alloc, exists := mm.allocations[tag]
	if !exists {
		return
	}

	delete(mm.allocations, tag)
	mm.currentUsage -= alloc.Size
	mm.stats.recordFree(alloc.Size)
}

// GetMemoryUsage 获取当前内存使用情况
func (mm *MemoryManager) GetMemoryUsage() MemoryStats {
	mm.mutex.RLock()
	defer mm.mutex.RUnlock()

	// 获取系统内存信息
	var m runtime.MemStats
	runtime.ReadMemStats(&m)

	stats := *mm.stats
	stats.CurrentUsage = mm.currentUsage
	stats.PeakUsage = mm.PeakUsage()

	return stats
}

// GetAllocationsInfo 获取分配信息
func (mm *MemoryManager) GetAllocationsInfo() map[string]AllocationInfo {
	mm.mutex.RLock()
	defer mm.mutex.RUnlock()

	result := make(map[string]AllocationInfo)
	for tag, alloc := range mm.allocations {
		result[tag] = *alloc
	}

	return result
}

// forceGC 强制垃圾回收
func (mm *MemoryManager) forceGC() {
	runtime.GC()
	mm.lastGCTime = time.Now()
	mm.stats.recordGC()
}

// shouldGC 判断是否应该执行GC
func (mm *MemoryManager) shouldGC() bool {
	if mm.currentUsage == 0 {
		return false
	}

	return float64(mm.currentUsage)/float64(mm.maxMemoryUsage) > mm.gcThreshold
}

// monitorMemory 监控内存使用
func (mm *MemoryManager) monitorMemory() {
	for {
		select {
		case <-mm.ctx.Done():
			return
		case <-mm.monitorTicker.C:
			if mm.shouldGC() {
				mm.forceGC()
			}

			// 记录内存使用情况
			mm.logMemoryUsage()
		}
	}
}

// logMemoryUsage 记录内存使用情况
func (mm *MemoryManager) logMemoryUsage() {
	var m runtime.MemStats
	runtime.ReadMemStats(&m)

	// 这里可以添加日志记录或监控上报
	_ = m
}

// PeakUsage 获取峰值内存使用
func (mm *MemoryManager) PeakUsage() uint64 {
	mm.mutex.RLock()
	defer mm.mutex.RUnlock()

	return mm.stats.PeakUsage
}

// CleanExpired 清理过期分配（超过指定时间未访问）
func (mm *MemoryManager) CleanExpired(maxAge time.Duration) {
	mm.mutex.Lock()
	defer mm.mutex.Unlock()

	now := time.Now()
	for tag, alloc := range mm.allocations {
		if now.Sub(alloc.AccessTime) > maxAge {
			delete(mm.allocations, tag)
			mm.currentUsage -= alloc.Size
			mm.stats.recordFree(alloc.Size)
		}
	}
}

// Close 关闭内存管理器
func (mm *MemoryManager) Close() {
	mm.cancel()
	if mm.monitorTicker != nil {
		mm.monitorTicker.Stop()
	}
	mm.mutex.Lock()
	mm.allocations = make(map[string]*AllocationInfo)
	mm.mutex.Unlock()
	mm.forceGC()
}

// ManagedMemory 受管理的内存
type ManagedMemory struct {
	manager *MemoryManager
	tag     string
	size    uint64
	data    []byte
}

// Data 获取数据
func (mm *ManagedMemory) Data() []byte {
	return mm.data
}

// UpdateAccessTime 更新访问时间
func (mm *ManagedMemory) UpdateAccessTime() {
	if alloc, exists := mm.manager.allocations[mm.tag]; exists {
		alloc.AccessTime = time.Now()
	}
}

// Release 释放内存
func (mm *ManagedMemory) Release() {
	mm.manager.Release(mm.tag)
}

// MemoryError 内存错误
type MemoryError struct {
	Type    string
	Message string
	Current uint64
	Max     uint64
}

func (e *MemoryError) Error() string {
	return e.Message
}

// 记录统计信息的方法
func (s *MemoryStats) recordAllocation(size uint64) {
	s.mutex.Lock()
	defer s.mutex.Unlock()

	s.TotalAllocations++
	s.CurrentUsage += size
	if s.CurrentUsage > s.PeakUsage {
		s.PeakUsage = s.CurrentUsage
	}
}

func (s *MemoryStats) recordFree(size uint64) {
	s.mutex.Lock()
	defer s.mutex.Unlock()

	s.TotalFreed++
	s.CurrentUsage -= size
}

func (s *MemoryStats) recordGC() {
	s.mutex.Lock()
	defer s.mutex.Unlock()

	s.GCCount++
	s.LastGCAt = time.Now()
}

// GetSystemMemoryInfo 获取系统内存信息
func GetSystemMemoryInfo() MemoryInfo {
	var m runtime.MemStats
	runtime.ReadMemStats(&m)

	return MemoryInfo{
		Alloc:      m.Alloc,
		TotalAlloc: m.TotalAlloc,
		Sys:        m.Sys,
		NumGC:      m.NumGC,
		NumGoroutine: runtime.NumGoroutine(),
	}
}

// MemoryInfo 内存信息
type MemoryInfo struct {
	Alloc        uint64
	TotalAlloc   uint64
	Sys          uint64
	NumGC        uint32
	NumGoroutine int
}

// 全局内存管理器实例
var GlobalMemoryManager *MemoryManager

// InitMemoryManager 初始化全局内存管理器
func InitMemoryManager(config *MemoryConfig) {
	GlobalMemoryManager = NewMemoryManager(config)
}

// GetGlobalMemoryManager 获取全局内存管理器
func GetGlobalMemoryManager() *MemoryManager {
	return GlobalMemoryManager
}