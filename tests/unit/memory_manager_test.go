package unit

import (
	"testing"
	"time"

	"smart-stock-insider/internal/utils"
)

// TestMemoryManager_AllocateRelease 测试内存分配和释放
func TestMemoryManager_AllocateRelease(t *testing.T) {
	config := &utils.MemoryConfig{
		MaxMemoryMB:    64,  // 64MB
		GCThreshold:    0.8,
		MonitorInterval: 1 * time.Second,
	}

	mm := utils.NewMemoryManager(config)
	defer mm.Close()

	// 分配内存
	mem, err := mm.Allocate("test", 1024) // 1KB
	if err != nil {
		t.Fatalf("内存分配失败: %v", err)
	}

	// 验证内存分配
	if mem == nil {
		t.Error("分配的内存为空")
	}

	if len(mem.Data()) != 1024 {
		t.Errorf("期望内存大小 1024，实际 %d", len(mem.Data()))
	}

	// 检查内存使用情况
	stats := mm.GetMemoryUsage()
	if stats.CurrentUsage != 1024 {
		t.Errorf("期望当前内存使用 1024，实际 %d", stats.CurrentUsage)
	}

	// 释放内存
	mem.Release()

	// 检查内存释放
	stats = mm.GetMemoryUsage()
	if stats.CurrentUsage != 0 {
		t.Errorf("期望当前内存使用 0，实际 %d", stats.CurrentUsage)
	}
}

// TestMemoryManager_MemoryLimit 测试内存限制
func TestMemoryManager_MemoryLimit(t *testing.T) {
	config := &utils.MemoryConfig{
		MaxMemoryMB:    1,   // 1MB
		GCThreshold:    0.8,
		MonitorInterval: 1 * time.Second,
	}

	mm := utils.NewMemoryManager(config)
	defer mm.Close()

	// 分配接近限制的内存
	mem1, err := mm.Allocate("test1", 800*1024) // 800KB
	if err != nil {
		t.Fatalf("内存分配失败: %v", err)
	}

	// 尝试分配超出限制的内存
	mem2, err := mm.Allocate("test2", 300*1024) // 300KB，会超出1MB限制
	if err == nil {
		t.Error("应该因为内存不足而分配失败")
	}

	if mem2 != nil {
		t.Error("超出限制的分配应该返回nil")
	}

	// 释放第一个分配
	mem1.Release()

	// 现在应该可以分配第二个
	mem2, err = mm.Allocate("test2", 300*1024)
	if err != nil {
		t.Errorf("释放内存后分配应该成功: %v", err)
	}

	if mem2 == nil {
		t.Error("有效的内存分配不应该返回nil")
	}
}

// TestMemoryManager_GCThreshold 测试GC阈值
func TestMemoryManager_GCThreshold(t *testing.T) {
	config := &utils.MemoryConfig{
		MaxMemoryMB:    1,   // 1MB
		GCThreshold:    0.5, // 50%时触发GC
		MonitorInterval: 100 * time.Millisecond,
	}

	mm := utils.NewMemoryManager(config)
	defer mm.Close()

	// 分配内存到接近GC阈值
	mem, err := mm.Allocate("gc_test", 600*1024) // 600KB，超过50%
	if err != nil {
		t.Fatalf("内存分配失败: %v", err)
	}

	// 等待GC触发（由于监控间隔）
	time.Sleep(150 * time.Millisecond)

	// 检查GC执行情况
	stats := mm.GetMemoryUsage()
	if stats.GCCount == 0 {
		t.Error("GC应该被触发")
	}

	// 释放内存
	mem.Release()
}

// TestMemoryManager_CleanExpired 测试清理过期内存
func TestMemoryManager_CleanExpired(t *testing.T) {
	config := &utils.MemoryConfig{
		MaxMemoryMB:    64,
		GCThreshold:    0.8,
		MonitorInterval: 1 * time.Second,
	}

	mm := utils.NewMemoryManager(config)
	defer mm.Close()

	// 分配内存
	mem1, _ := mm.Allocate("expire_test1", 1024)
	mem2, _ := mm.Allocate("expire_test2", 1024)

	// 更新其中一个的访问时间
	time.Sleep(10 * time.Millisecond)
	mem1.UpdateAccessTime()

	// 清理超过5ms未访问的内存
	mm.CleanExpired(5 * time.Millisecond)

	// 检查分配信息
	allocs := mm.GetAllocationsInfo()

	// expire_test2应该被清理
	if _, exists := allocs["expire_test2"]; exists {
		t.Error("expire_test2应该被清理")
	}

	// expire_test1应该还存在（因为刚访问过）
	if _, exists := allocs["expire_test1"]; !exists {
		t.Error("expire_test1应该还存在")
	}

	// 释放剩余内存
	mem1.Release()
}

// TestMemoryManager_PeakUsage 测试峰值内存使用
func TestMemoryManager_PeakUsage(t *testing.T) {
	config := &utils.MemoryConfig{
		MaxMemoryMB:    64,
		GCThreshold:    0.8,
		MonitorInterval: 1 * time.Second,
	}

	mm := utils.NewMemoryManager(config)
	defer mm.Close()

	// 分配内存
	mem1, _ := mm.Allocate("peak1", 1024)
	mem2, _ := mm.Allocate("peak2", 2048)
	mem3, _ := mm.Allocate("peak3", 4096)

	// 检查峰值
	peak := mm.PeakUsage()
	expectedPeak := uint64(1024 + 2048 + 4096)

	if peak != expectedPeak {
		t.Errorf("期望峰值内存 %d，实际 %d", expectedPeak, peak)
	}

	// 释放部分内存
	mem2.Release()

	// 峰值应该保持不变
	peak = mm.PeakUsage()
	if peak != expectedPeak {
		t.Error("峰值内存不应该减少")
	}

	// 释放所有内存
	mem1.Release()
	mem3.Release()
}

// TestMemoryManager_Stats 测试内存统计
func TestMemoryManager_Stats(t *testing.T) {
	config := &utils.MemoryConfig{
		MaxMemoryMB:    64,
		GCThreshold:    0.8,
		MonitorInterval: 1 * time.Second,
	}

	mm := utils.NewMemoryManager(config)
	defer mm.Close()

	// 分配内存
	mem1, _ := mm.Allocate("stats1", 1024)
	mem2, _ := mm.Allocate("stats2", 2048)

	// 获取统计信息
	stats := mm.GetMemoryUsage()

	// 验证统计信息
	if stats.TotalAllocations != 2 {
		t.Errorf("期望总分配次数 2，实际 %d", stats.TotalAllocations)
	}

	if stats.CurrentUsage != 3072 {
		t.Errorf("期望当前使用 3072，实际 %d", stats.CurrentUsage)
	}

	// 释放一个分配
	mem2.Release()

	// 再次检查统计
	stats = mm.GetMemoryUsage()
	if stats.TotalFreed != 2048 {
		t.Errorf("期望总释放 2048，实际 %d", stats.TotalFreed)
	}

	if stats.CurrentUsage != 1024 {
		t.Errorf("期望当前使用 1024，实际 %d", stats.CurrentUsage)
	}

	// 释放剩余内存
	mem1.Release()
}

// TestMemoryManager_ConcurrentAccess 测试并发访问
func TestMemoryManager_ConcurrentAccess(t *testing.T) {
	config := &utils.MemoryConfig{
		MaxMemoryMB:    128,
		GCThreshold:    0.8,
		MonitorInterval: 1 * time.Second,
	}

	mm := utils.NewMemoryManager(config)
	defer mm.Close()

	// 并发分配和释放
	done := make(chan bool, 10)

	for i := 0; i < 10; i++ {
		go func(id int) {
			defer func() { done <- true }()

			for j := 0; j < 10; j++ {
				// 分配
				tag := fmt.Sprintf("concurrent_%d_%d", id, j)
				mem, err := mm.Allocate(tag, 1024)
				if err != nil {
					// 内存不足是正常的，继续
					continue
				}

				// 随机延迟
				time.Sleep(time.Duration(j) * time.Millisecond)

				// 释放
				mem.Release()
			}
		}(i)
	}

	// 等待所有goroutine完成
	for i := 0; i < 10; i++ {
		<-done
	}

	// 检查没有内存泄漏
	stats := mm.GetMemoryUsage()
	if stats.CurrentUsage > 1024*100 { // 允许少量剩余
		t.Errorf("内存可能泄漏，当前使用 %d", stats.CurrentUsage)
	}
}

// BenchmarkMemoryManager_Allocate 基准测试：内存分配
func BenchmarkMemoryManager_Allocate(b *testing.B) {
	config := &utils.MemoryConfig{
		MaxMemoryMB:    1024,
		GCThreshold:    0.9,
		MonitorInterval: 1 * time.Second,
	}

	mm := utils.NewMemoryManager(config)
	defer mm.Close()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		tag := fmt.Sprintf("bench_%d", i)
		mem, err := mm.Allocate(tag, 1024)
		if err == nil && mem != nil {
			// 立即释放以避免内存耗尽
			mem.Release()
		}
	}
}