/**
 * 自选股状态管理
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { api } from '@/services/api';

interface StockItem {
  id: number;
  symbol: string;
  name: string;
  market: string;
  sector: string;
  current_price?: number;
  change_amount?: number;
  change_percent?: number;
}

interface WatchlistState {
  // 状态
  watchlist: StockItem[];
  isLoading: boolean;
  error: string | null;

  // 操作
  loadWatchlist: () => Promise<void>;
  addToWatchlist: (symbolOrStock: string | StockItem) => Promise<void>;
  removeFromWatchlist: (symbol: string) => Promise<void>;
  clearWatchlist: () => void;
  updateStockData: (symbol: string, data: Partial<StockItem>) => void;
  setError: (error: string | null) => void;
  setLoading: (loading: boolean) => void;
}

export const useWatchlistStore = create<WatchlistState>()(
  persist(
    (set, get) => ({
      // 初始状态
      watchlist: [],
      isLoading: false,
      error: null,

      // 加载自选股列表
      loadWatchlist: async () => {
        try {
          set({ isLoading: true, error: null });

          // 这里可以从本地存储或API加载
          // 暂时使用本地存储的数据
          const stored = localStorage.getItem('watchlist');
          if (stored) {
            const watchlist = JSON.parse(stored);
            set({ watchlist, isLoading: false });
          } else {
            set({ watchlist: [], isLoading: false });
          }
        } catch (error) {
          console.error('加载自选股失败:', error);
          set({ error: '加载自选股失败', isLoading: false });
        }
      },

      // 添加到自选股
      addToWatchlist: async (symbolOrStock) => {
        try {
          set({ isLoading: true, error: null });

          const { watchlist } = get();
          let stockToAdd: StockItem;

          if (typeof symbolOrStock === 'string') {
            // 如果传入的是股票代码，需要获取详细信息
            try {
              const response = await api.get(`/api/stocks/${symbolOrStock}/info`);
              stockToAdd = response.data;
            } catch (error) {
              console.error('获取股票信息失败:', error);
              set({ error: '获取股票信息失败', isLoading: false });
              return;
            }
          } else {
            // 如果传入的是股票对象
            stockToAdd = symbolOrStock;
          }

          // 检查是否已存在
          const exists = watchlist.some(stock => stock.symbol === stockToAdd.symbol);
          if (exists) {
            set({ error: '该股票已在自选股中', isLoading: false });
            return;
          }

          // 添加到列表
          const newWatchlist = [...watchlist, stockToAdd];
          set({ watchlist: newWatchlist, isLoading: false });

          // 保存到本地存储
          localStorage.setItem('watchlist', JSON.stringify(newWatchlist));

          console.log('添加到自选股成功:', stockToAdd.symbol);
        } catch (error) {
          console.error('添加自选股失败:', error);
          set({ error: '添加自选股失败', isLoading: false });
        }
      },

      // 从自选股移除
      removeFromWatchlist: async (symbol) => {
        try {
          const { watchlist } = get();
          const newWatchlist = watchlist.filter(stock => stock.symbol !== symbol);

          set({ watchlist: newWatchlist });

          // 保存到本地存储
          localStorage.setItem('watchlist', JSON.stringify(newWatchlist));

          console.log('从自选股移除成功:', symbol);
        } catch (error) {
          console.error('移除自选股失败:', error);
          set({ error: '移除自选股失败' });
        }
      },

      // 清空自选股
      clearWatchlist: () => {
        set({ watchlist: [] });
        localStorage.removeItem('watchlist');
      },

      // 更新股票数据
      updateStockData: (symbol, data) => {
        const { watchlist } = get();
        const newWatchlist = watchlist.map(stock =>
          stock.symbol === symbol ? { ...stock, ...data } : stock
        );
        set({ watchlist: newWatchlist });
      },

      // 设置错误状态
      setError: (error) => {
        set({ error });
      },

      // 设置加载状态
      setLoading: (isLoading) => {
        set({ isLoading });
      },
    }),
    {
      name: 'watchlist-storage',
      partialize: (state) => ({
        watchlist: state.watchlist,
      }),
    }
  )
);

// 选择器函数
export const useWatchlist = () => useWatchlistStore((state) => state.watchlist);
export const useWatchlistLoading = () => useWatchlistStore((state) => state.isLoading);
export const useWatchlistError = () => useWatchlistStore((state) => state.error);

// 自选股相关的工具函数
export const watchlistUtils = {
  // 检查是否在自选股中
  isInWatchlist: (symbol: string) => {
    const watchlist = useWatchlistStore.getState().watchlist;
    return watchlist.some(stock => stock.symbol === symbol);
  },

  // 获取自选股符号列表
  getWatchlistSymbols: () => {
    const watchlist = useWatchlistStore.getState().watchlist;
    return watchlist.map(stock => stock.symbol);
  },

  // 获取涨跌统计
  getStats: () => {
    const watchlist = useWatchlistStore.getState().watchlist;
    const total = watchlist.length;
    const up = watchlist.filter(stock => (stock.change_percent || 0) > 0).length;
    const down = watchlist.filter(stock => (stock.change_percent || 0) < 0).length;
    const flat = total - up - down;

    return {
      total,
      up,
      down,
      flat,
      upPercent: total > 0 ? (up / total * 100).toFixed(1) : '0',
      downPercent: total > 0 ? (down / total * 100).toFixed(1) : '0',
    };
  },

  // 按涨跌幅排序
  sortByChange: (order: 'desc' | 'asc' = 'desc') => {
    const watchlist = useWatchlistStore.getState().watchlist;
    const sorted = [...watchlist].sort((a, b) => {
      const changeA = a.change_percent || 0;
      const changeB = b.change_percent || 0;
      return order === 'desc' ? changeB - changeA : changeA - changeB;
    });
    return sorted;
  },

  // 按成交量排序
  sortByVolume: (order: 'desc' | 'asc' = 'desc') => {
    const watchlist = useWatchlistStore.getState().watchlist;
    const sorted = [...watchlist].sort((a, b) => {
      const volumeA = a.volume || 0;
      const volumeB = b.volume || 0;
      return order === 'desc' ? volumeB - volumeA : volumeA - volumeB;
    });
    return sorted;
  },

  // 搜索自选股
  search: (keyword: string) => {
    const watchlist = useWatchlistStore.getState().watchlist;
    if (!keyword.trim()) return watchlist;

    const searchLower = keyword.toLowerCase();
    return watchlist.filter(stock =>
      stock.symbol.toLowerCase().includes(searchLower) ||
      stock.name.toLowerCase().includes(searchLower)
    );
  },
};