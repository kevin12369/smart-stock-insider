// API缓存管理
interface CacheItem<T = any> {
  data: T
  timestamp: number
  ttl: number
  key: string
}

interface CacheOptions {
  ttl?: number // 缓存时间（毫秒）
  staleWhileRevalidate?: boolean // 是否在重新验证时返回过期数据
  priority?: 'high' | 'medium' | 'low'
}

class APICache {
  private cache = new Map<string, CacheItem>()
  private maxSize = 100 // 最大缓存条目数
  private cleanupInterval: NodeJS.Timeout

  constructor() {
    // 定期清理过期缓存
    this.cleanupInterval = setInterval(() => {
      this.cleanup()
    }, 60000) // 每分钟清理一次
  }

  // 设置缓存
  set<T>(key: string, data: T, options: CacheOptions = {}): void {
    const ttl = options.ttl || 5 * 60 * 1000 // 默认5分钟
    const item: CacheItem<T> = {
      data,
      timestamp: Date.now(),
      ttl,
      key
    }

    // 如果缓存已满，删除最旧的条目
    if (this.cache.size >= this.maxSize) {
      const oldestKey = this.cache.keys().next().value
      if (oldestKey) {
        this.cache.delete(oldestKey)
      }
    }

    this.cache.set(key, item)
  }

  // 获取缓存
  get<T>(key: string, options: CacheOptions = {}): T | null {
    const item = this.cache.get(key) as CacheItem<T>

    if (!item) {
      return null
    }

    const now = Date.now()
    const isExpired = (now - item.timestamp) > item.ttl

    if (isExpired) {
      if (options.staleWhileRevalidate) {
        // 返回过期数据，同时后台更新
        return item.data
      } else {
        this.cache.delete(key)
        return null
      }
    }

    return item.data
  }

  // 检查是否存在且未过期
  has(key: string): boolean {
    const item = this.cache.get(key)
    if (!item) return false

    const isExpired = (Date.now() - item.timestamp) > item.ttl
    if (isExpired) {
      this.cache.delete(key)
      return false
    }

    return true
  }

  // 删除缓存
  delete(key: string): boolean {
    return this.cache.delete(key)
  }

  // 清空所有缓存
  clear(): void {
    this.cache.clear()
  }

  // 清理过期缓存
  private cleanup(): void {
    const now = Date.now()
    const keysToDelete: string[] = []

    for (const [key, item] of this.cache) {
      if ((now - item.timestamp) > item.ttl) {
        keysToDelete.push(key)
      }
    }

    keysToDelete.forEach(key => this.cache.delete(key))
  }

  // 获取缓存统计信息
  getStats() {
    return {
      size: this.cache.size,
      maxSize: this.maxSize,
      hitRate: this.hitCount / (this.hitCount + this.missCount) || 0,
      hitCount: this.hitCount,
      missCount: this.missCount
    }
  }

  private hitCount = 0
  private missCount = 0

  // 记录命中
  recordHit(): void {
    this.hitCount++
  }

  // 记录未命中
  recordMiss(): void {
    this.missCount++
  }

  // 销毁缓存实例
  destroy(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval)
    }
    this.cache.clear()
  }
}

// 创建全局缓存实例
export const apiCache = new APICache()

// 缓存装饰器
export function withCache<T extends any[], R>(
  fn: (...args: T) => Promise<R>,
  options: CacheOptions = {}
) {
  return async (...args: T): Promise<R> => {
    // 生成缓存键
    const key = `${fn.name}_${JSON.stringify(args)}`

    // 尝试从缓存获取
    const cached = apiCache.get<R>(key, options)
    if (cached !== null) {
      apiCache.recordHit()
      return cached
    }

    // 缓存未命中，调用原函数
    apiCache.recordMiss()
    const result = await fn(...args)

    // 缓存结果
    apiCache.set(key, result, options)

    return result
  }
}

import { useState, useEffect, useCallback } from 'react'

// 缓存Hook
export function useCachedAPICall<T>(
  key: string,
  apiCall: () => Promise<T>,
  options: CacheOptions = {}
) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        setError(null)

        // 尝试从缓存获取
        const cached = apiCache.get<T>(key, options)
        if (cached !== null) {
          setData(cached)
          setLoading(false)
          return
        }

        // 缓存未命中，调用API
        const result = await apiCall()
        setData(result)
        apiCache.set(key, result, options)
      } catch (err) {
        setError(err as Error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [key, apiCall])

  // 手动刷新缓存
  const refetch = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      apiCache.delete(key) // 删除旧缓存
      const result = await apiCall()
      setData(result)
      apiCache.set(key, result, options)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }, [key, apiCall])

  return { data, loading, error, refetch }
}

// 预取数据
export function prefetchData<T>(
  key: string,
  apiCall: () => Promise<T>,
  options: CacheOptions = {}
): void {
  if (!apiCache.has(key)) {
    apiCall().then(result => {
      apiCache.set(key, result, options)
    }).catch(() => {
      // 预取失败不影响主流程
    })
  }
}

export default apiCache