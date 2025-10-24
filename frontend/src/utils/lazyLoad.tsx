import React, { Suspense } from 'react'
import { Spin } from 'antd'

// 懒加载组件包装器
export const LazyWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <Suspense
    fallback={
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '200px',
        width: '100%'
      }}>
        <Spin size="large" />
      </div>
    }
  >
    {children}
  </Suspense>
)

// 预加载功能
export const preloadComponent = (importFunc: () => Promise<any>) => {
  // 在浏览器空闲时预加载组件
  if ('requestIdleCallback' in window) {
    requestIdleCallback(() => {
      importFunc()
    })
  } else {
    // 降级处理
    setTimeout(() => {
      importFunc()
    }, 100)
  }
}

// 关键路由预加载
export const preloadCriticalRoutes = () => {
  // 预加载关键路由
  const criticalRoutes = [
    () => import('../pages/PortfolioManager'),
    () => import('../pages/PortfolioAnalysis'),
    () => import('../pages/NewsHub'),
    () => import('../pages/PushNotification')
  ]

  criticalRoutes.forEach(route => {
    preloadComponent(route)
  })
}

// 组件延迟加载器
export const createLazyComponent = (importFunc: () => Promise<any>, preload = false) => {
  const LazyComponent = React.lazy(importFunc)

  if (preload) {
    preloadComponent(importFunc)
  }

  return (props: any) => (
    <LazyWrapper>
      <LazyComponent {...props} />
    </LazyWrapper>
  )
}

// 资源预加载
export const preloadAssets = (assets: string[]) => {
  assets.forEach(asset => {
    const link = document.createElement('link')
    link.rel = 'preload'
    link.href = asset
    link.as = asset.endsWith('.js') ? 'script' : 'style'
    document.head.appendChild(link)
  })
}

// 批量预加载图片
export const preloadImages = (imageUrls: string[]) => {
  imageUrls.forEach(url => {
    const img = new Image()
    img.src = url
  })
}

export default {
  LazyWrapper,
  preloadComponent,
  preloadCriticalRoutes,
  createLazyComponent,
  preloadAssets,
  preloadImages
}