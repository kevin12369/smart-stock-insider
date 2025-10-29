import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AppState {
  // 应用状态
  initialized: boolean
  loading: boolean
  theme: 'light' | 'dark'
  language: 'zh-CN' | 'en-US'

  // 用户设置
  settings: {
    notifications: boolean
    autoRefresh: boolean
    refreshInterval: number
    apiKey?: string
  }

  // 应用信息
  appInfo: {
    name: string
    version: string
    description: string
  } | null

  // 系统信息
  systemInfo: {
    os: string
    arch: string
    memory: string
  } | null

  // Actions
  setInitialized: (initialized: boolean) => void
  setLoading: (loading: boolean) => void
  setTheme: (theme: 'light' | 'dark') => void
  setLanguage: (language: 'zh-CN' | 'en-US') => void
  updateSettings: (settings: Partial<AppState['settings']>) => void
  loadAppInfo: () => Promise<void>
  loadSystemInfo: () => Promise<void>
  reset: () => void
}

const initialState = {
  initialized: false,
  loading: false,
  theme: 'light' as const,
  language: 'zh-CN' as const,
  settings: {
    notifications: true,
    autoRefresh: true,
    refreshInterval: 30000, // 30秒
  },
  appInfo: null,
  systemInfo: null,
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      ...initialState,

      setInitialized: (initialized) => set({ initialized }),

      setLoading: (loading) => set({ loading }),

      setTheme: (theme) => set({ theme }),

      setLanguage: (language) => set({ language }),

      updateSettings: (newSettings) =>
        set((state) => ({
          settings: { ...state.settings, ...newSettings }
        })),

      loadAppInfo: async () => {
        try {
          set({ loading: true })
          // Web版本的应用信息
          const appInfo = {
            name: '智股通',
            version: '1.0.0',
            description: 'AI增强轻量化专业股票分析系统'
          }
          set({ appInfo })
        } catch (error) {
          console.error('Failed to load app info:', error)
        } finally {
          set({ loading: false })
        }
      },

      loadSystemInfo: async () => {
        try {
          set({ loading: true })
          // Web版本的系统信息
          const systemInfo = {
            os: navigator.platform || 'Web Platform',
            arch: 'Web Architecture',
            memory: 'Web Browser Memory'
          }
          set({ systemInfo })
        } catch (error) {
          console.error('Failed to load system info:', error)
        } finally {
          set({ loading: false })
        }
      },

      reset: () => set(initialState),
    }),
    {
      name: 'app-store',
      partialize: (state) => ({
        theme: state.theme,
        language: state.language,
        settings: state.settings,
      }),
    }
  )
)

// 选择器函数
export const useAppSettings = () => useAppStore((state) => state.settings)
export const useAppInfo = () => useAppStore((state) => state.appInfo)
export const useSystemInfo = () => useAppStore((state) => state.systemInfo)
export const useAppLoading = () => useAppStore((state) => state.loading)
export const useAppTheme = () => useAppStore((state) => state.theme)
export const useAppLanguage = () => useAppStore((state) => state.language)