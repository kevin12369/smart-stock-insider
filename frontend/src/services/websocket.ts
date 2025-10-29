/**
 * WebSocket客户端管理器
 * 处理WebSocket连接、消息处理、重连机制
 */

import { message } from 'antd';

export interface ConnectionConfig {
  url: string;
  token?: string;
  reconnectAttempts?: number;
  reconnectInterval?: number;
  heartbeatInterval?: number;
}

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
}

export enum ConnectionStatus {
  DISCONNECTED = 'disconnected',
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  RECONNECTING = 'reconnecting',
  ERROR = 'error'
}

class WebSocketManager {
  private connections = new Map<string, WebSocket>();
  private configs = new Map<string, ConnectionConfig>();
  private statuses: Record<string, ConnectionStatus> = {};
  private messageHandlers = new Map<string, Set<(message: WebSocketMessage) => void>>();
  private reconnectAttempts = new Map<string, number>();
  private heartbeatIntervals = new Map<string, NodeJS.Timeout>();
  private reconnectTimeouts = new Map<string, NodeJS.Timeout>();

  constructor() {
    // 页面卸载时清理所有连接
    if (typeof window !== 'undefined') {
      window.addEventListener('beforeunload', () => {
        this.disconnectAll();
      });
    }
  }

  /**
   * 连接WebSocket
   */
  connect(connectionId: string, config: ConnectionConfig): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        // 如果已连接，先断开
        if (this.connections.has(connectionId)) {
          this.disconnect(connectionId);
        }

        // 保存配置
        this.configs.set(connectionId, {
          reconnectAttempts: 5,
          reconnectInterval: 3000,
          heartbeatInterval: 30000,
          ...config
        });

        // 设置状态为连接中
        this.statuses[connectionId] = ConnectionStatus.CONNECTING;
        this.reconnectAttempts.set(connectionId, 0);

        // 创建WebSocket连接
        const wsUrl = this.buildWebSocketUrl(config);
        const ws = new WebSocket(wsUrl);

        // 连接成功
        ws.onopen = () => {
          console.log(`WebSocket连接成功: ${connectionId}`);
          this.statuses[connectionId] = ConnectionStatus.CONNECTED;
          this.connections.set(connectionId, ws);
          this.reconnectAttempts.set(connectionId, 0);

          // 启动心跳
          this.startHeartbeat(connectionId);

          // 发送认证信息
          if (config.token) {
            this.send(connectionId, {
              type: 'auth',
              data: { token: config.token }
            });
          }

          resolve();
        };

        // 接收消息
        ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(connectionId, message);
          } catch (error) {
            console.error(`解析WebSocket消息失败: ${error}`, event.data);
          }
        };

        // 连接关闭
        ws.onclose = (event) => {
          console.log(`WebSocket连接关闭: ${connectionId}`, event.code, event.reason);
          this.connections.delete(connectionId);
          this.statuses[connectionId] = ConnectionStatus.DISCONNECTED;
          this.stopHeartbeat(connectionId);

          // 自动重连
          if (!event.wasClean && this.shouldReconnect(connectionId)) {
            this.scheduleReconnect(connectionId);
          }
        };

        // 连接错误
        ws.onerror = (error) => {
          console.error(`WebSocket连接错误: ${connectionId}`, error);
          this.statuses[connectionId] = ConnectionStatus.ERROR;
          reject(error);
        };

      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * 断开连接
   */
  disconnect(connectionId: string): void {
    try {
      const ws = this.connections.get(connectionId);
      if (ws) {
        ws.close(1000, '用户主动断开');
        this.connections.delete(connectionId);
      }

      this.statuses[connectionId] = ConnectionStatus.DISCONNECTED;
      this.stopHeartbeat(connectionId);
      this.clearReconnectTimeout(connectionId);

      console.log(`WebSocket连接已断开: ${connectionId}`);
    } catch (error) {
      console.error(`断开WebSocket连接失败: ${error}`);
    }
  }

  /**
   * 断开所有连接
   */
  disconnectAll(): void {
    for (const connectionId of this.connections.keys()) {
      this.disconnect(connectionId);
    }
  }

  /**
   * 发送消息
   */
  send(connectionId: string, data: any): boolean {
    try {
      const ws = this.connections.get(connectionId);
      if (!ws || ws.readyState !== WebSocket.OPEN) {
        console.warn(`WebSocket未连接: ${connectionId}`);
        return false;
      }

      const message = {
        ...data,
        timestamp: new Date().toISOString()
      };

      ws.send(JSON.stringify(message));
      return true;
    } catch (error) {
      console.error(`发送WebSocket消息失败: ${error}`);
      return false;
    }
  }

  /**
   * 订阅消息
   */
  subscribe(connectionId: string, handler: (message: WebSocketMessage) => void): () => void {
    if (!this.messageHandlers.has(connectionId)) {
      this.messageHandlers.set(connectionId, new Set());
    }

    this.messageHandlers.get(connectionId)!.add(handler);

    // 返回取消订阅函数
    return () => {
      const handlers = this.messageHandlers.get(connectionId);
      if (handlers) {
        handlers.delete(handler);
        if (handlers.size === 0) {
          this.messageHandlers.delete(connectionId);
        }
      }
    };
  }

  /**
   * 订阅特定类型的消息
   */
  subscribeByType<T = any>(
    connectionId: string,
    messageType: string,
    handler: (data: T) => void
  ): () => void {
    const wrappedHandler = (message: WebSocketMessage) => {
      if (message.type === messageType) {
        handler(message.data);
      }
    };

    return this.subscribe(connectionId, wrappedHandler);
  }

  /**
   * 获取连接状态
   */
  getStatus(connectionId: string): ConnectionStatus {
    return this.statuses[connectionId] || ConnectionStatus.DISCONNECTED;
  }

  /**
   * 检查连接是否活跃
   */
  isConnected(connectionId: string): boolean {
    return this.getStatus(connectionId) === ConnectionStatus.CONNECTED;
  }

  /**
   * 构建WebSocket URL
   */
  private buildWebSocketUrl(config: ConnectionConfig): string {
    const { url, token } = config;

    // 如果URL已经是完整的WebSocket URL，直接返回
    if (url.startsWith('ws://') || url.startsWith('wss://')) {
      return url;
    }

    // 构建WebSocket URL
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;

    let wsUrl = `${protocol}//${host}${url.startsWith('/') ? '' : '/'}${url}`;

    // 添加token参数
    if (token) {
      wsUrl += `?token=${token}`;
    }

    return wsUrl;
  }

  /**
   * 处理接收到的消息
   */
  private handleMessage(connectionId: string, message: WebSocketMessage): void {
    try {
      // 处理心跳消息
      if (message.type === 'ping') {
        this.send(connectionId, { type: 'pong', data: { timestamp: new Date().toISOString() } });
        return;
      }

      if (message.type === 'pong') {
        return; // 忽略pong响应
      }

      // 处理错误消息
      if (message.type === 'error') {
        console.error(`WebSocket错误消息: ${message.data.error}`);
        message.error(message.data.error);
        return;
      }

      // 调用注册的消息处理器
      const handlers = this.messageHandlers.get(connectionId);
      if (handlers) {
        handlers.forEach(handler => {
          try {
            handler(message);
          } catch (error) {
            console.error(`WebSocket消息处理器错误: ${error}`);
          }
        });
      }

    } catch (error) {
      console.error(`处理WebSocket消息失败: ${error}`);
    }
  }

  /**
   * 启动心跳
   */
  private startHeartbeat(connectionId: string): void {
    const config = this.configs.get(connectionId);
    if (!config) return;

    const interval = setInterval(() => {
      if (this.isConnected(connectionId)) {
        this.send(connectionId, { type: 'ping' });
      } else {
        this.stopHeartbeat(connectionId);
      }
    }, config.heartbeatInterval);

    this.heartbeatIntervals.set(connectionId, interval);
  }

  /**
   * 停止心跳
   */
  private stopHeartbeat(connectionId: string): void {
    const interval = this.heartbeatIntervals.get(connectionId);
    if (interval) {
      clearInterval(interval);
      this.heartbeatIntervals.delete(connectionId);
    }
  }

  /**
   * 判断是否应该重连
   */
  private shouldReconnect(connectionId: string): boolean {
    const config = this.configs.get(connectionId);
    const attempts = this.reconnectAttempts.get(connectionId) || 0;

    return config && attempts < (config.reconnectAttempts || 5);
  }

  /**
   * 安排重连
   */
  private scheduleReconnect(connectionId: string): void {
    const config = this.configs.get(connectionId);
    if (!config) return;

    this.statuses[connectionId] = ConnectionStatus.RECONNECTING;
    this.reconnectAttempts.set(connectionId, (this.reconnectAttempts.get(connectionId) || 0) + 1);

    const timeout = setTimeout(async () => {
      try {
        console.log(`尝试重连WebSocket: ${connectionId} (${this.reconnectAttempts.get(connectionId)})`);
        await this.connect(connectionId, config);
      } catch (error) {
        console.error(`WebSocket重连失败: ${error}`);
        if (this.shouldReconnect(connectionId)) {
          this.scheduleReconnect(connectionId);
        }
      }
    }, config.reconnectInterval);

    this.reconnectTimeouts.set(connectionId, timeout);
  }

  /**
   * 清除重连超时
   */
  private clearReconnectTimeout(connectionId: string): void {
    const timeout = this.reconnectTimeouts.get(connectionId);
    if (timeout) {
      clearTimeout(timeout);
      this.reconnectTimeouts.delete(connectionId);
    }
  }
}

// 创建全局WebSocket管理器实例
export const websocketManager = new WebSocketManager();

// 提供便捷的连接ID常量
export const WEBSOCKET_CONNECTIONS = {
  STOCK_DATA: 'stock_data',
  NEWS_PUSH: 'news_push',
  MARKET_ALERT: 'market_alert',
  SYSTEM_NOTIFICATION: 'system_notification'
} as const;

// ConnectionStatus已在上面定义并导出，无需重复导出