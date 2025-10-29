/**
 * 实时新闻通知组件
 * 显示重要新闻推送和市场提醒
 */

import React, { useState, useEffect, useRef } from 'react';
import { Card, List, Typography, Tag, Button, Space, Badge, Drawer, notification, Avatar, Tooltip } from 'antd';
import {
  BellOutlined,
  MessageOutlined,
  WarningOutlined,
  InfoCircleOutlined,
  CloseOutlined,
  CheckOutlined,
  DeleteOutlined,
  SettingOutlined
} from '@ant-design/icons';
import { websocketManager, WEBSOCKET_CONNECTIONS, ConnectionStatus } from '@/services/websocket';
import { formatRelativeTime } from '@/utils/format';

const { Text, Title } = Typography;

interface NewsAlert {
  id: string;
  title: string;
  summary: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  categories: string[];
  mentioned_stocks: string[];
  impact_score: number;
  sentiment: string;
  created_at: string;
  trigger: string;
  read?: boolean;
}

interface NewsNotificationProps {
  maxVisible?: number;
  showBadge?: boolean;
  enableSound?: boolean;
  position?: 'topRight' | 'topLeft' | 'bottomRight' | 'bottomLeft';
}

const NewsNotification: React.FC<NewsNotificationProps> = ({
  maxVisible = 5,
  showBadge = true,
  enableSound = true,
  position = 'topRight'
}) => {
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>(ConnectionStatus.DISCONNECTED);
  const [alerts, setAlerts] = useState<NewsAlert[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [settingsVisible, setSettingsVisible] = useState(false);

  const unsubscribersRef = useRef<(() => void)[]>([]);
  const audioContextRef = useRef<AudioContext | null>(null);

  useEffect(() => {
    connectWebSocket();
    return () => {
      disconnectWebSocket();
    };
  }, []);

  useEffect(() => {
    setUnreadCount(alerts.filter(alert => !alert.read).length);
  }, [alerts]);

  const connectWebSocket = async () => {
    try {
      await websocketManager.connect(WEBSOCKET_CONNECTIONS.NEWS_PUSH, {
        url: '/api/realtime/news',
        token: localStorage.getItem('token') || undefined
      });

      setConnectionStatus(ConnectionStatus.CONNECTED);

      // 订阅新闻提醒
      const unsubscribeAlert = websocketManager.subscribeByType(
        WEBSOCKET_CONNECTIONS.NEWS_PUSH,
        'news_alert',
        handleNewsAlert
      );

      const unsubscribeBatch = websocketManager.subscribeByType(
        WEBSOCKET_CONNECTIONS.NEWS_PUSH,
        'news_batch',
        handleNewsBatch
      );

      const unsubscribeCustom = websocketManager.subscribeByType(
        WEBSOCKET_CONNECTIONS.NEWS_PUSH,
        'custom_notification',
        handleCustomNotification
      );

      unsubscribersRef.current = [unsubscribeAlert, unsubscribeBatch, unsubscribeCustom];

    } catch (error) {
      console.error('连接新闻推送WebSocket失败:', error);
      setConnectionStatus(ConnectionStatus.ERROR);
    }
  };

  const disconnectWebSocket = () => {
    unsubscribersRef.current.forEach(unsubscribe => unsubscribe());
    websocketManager.disconnect(WEBSOCKET_CONNECTIONS.NEWS_PUSH);
    setConnectionStatus(ConnectionStatus.DISCONNECTED);
  };

  const handleNewsAlert = (alertData: NewsAlert) => {
    const alert = { ...alertData, read: false };

    setAlerts(prev => [alert, ...prev].slice(0, 100)); // 最多保留100条

    // 显示通知
    showNotification(alert);

    // 播放提示音
    if (enableSound && alert.priority !== 'low') {
      playNotificationSound(alert.priority);
    }
  };

  const handleNewsBatch = (data: any) => {
    const newAlerts = data.alerts.map((alert: NewsAlert) => ({ ...alert, read: false }));

    setAlerts(prev => [...newAlerts, ...prev].slice(0, 100));

    // 批量通知
    if (newAlerts.length > 0) {
      notification.info({
        message: '新闻更新',
        description: `收到 ${newAlerts.length} 条新闻更新`,
        placement: position,
        duration: 4
      });

      if (enableSound) {
        playNotificationSound('medium');
      }
    }
  };

  const handleCustomNotification = (data: any) => {
    const alert = data.alert;
    setAlerts(prev => [alert, ...prev].slice(0, 100));

    showNotification(alert);

    if (enableSound) {
      playNotificationSound('high');
    }
  };

  const showNotification = (alert: NewsAlert) => {
    const icon = getPriorityIcon(alert.priority);
    const color = getPriorityColor(alert.priority);

    notification.open({
      message: (
        <div className="flex items-center space-x-2">
          {icon}
          <span className="font-semibold">{alert.title}</span>
        </div>
      ),
      description: (
        <div>
          <div className="text-sm mb-1">{alert.summary}</div>
          <div className="flex items-center space-x-2 text-xs text-gray-500">
            <span>{formatRelativeTime(alert.created_at)}</span>
            {alert.categories.length > 0 && (
              <Tag color="blue" size="small">{alert.categories[0]}</Tag>
            )}
          </div>
        </div>
      ),
      icon,
      placement: position,
      duration: alert.priority === 'urgent' ? 0 : 6, // 紧急通知不自动关闭
      style: { borderLeft: `4px solid ${color}` }
    });
  };

  const playNotificationSound = (priority: string) => {
    try {
      if (!audioContextRef.current) {
        audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      }

      const context = audioContextRef.current;
      const oscillator = context.createOscillator();
      const gainNode = context.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(context.destination);

      // 根据优先级设置不同的音调
      const frequencies = {
        low: 800,
        medium: 1000,
        high: 1200,
        urgent: 1500
      };

      oscillator.frequency.value = frequencies[priority as keyof typeof frequencies] || 1000;
      oscillator.type = 'sine';

      gainNode.gain.setValueAtTime(0.1, context.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.01, context.currentTime + 0.3);

      oscillator.start(context.currentTime);
      oscillator.stop(context.currentTime + 0.3);

    } catch (error) {
      console.error('播放通知音失败:', error);
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return <WarningOutlined className="text-red-500" />;
      case 'high':
        return <InfoCircleOutlined className="text-orange-500" />;
      case 'medium':
        return <MessageOutlined className="text-blue-500" />;
      default:
        return <BellOutlined className="text-gray-500" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return '#ff4d4f';
      case 'high': return '#fa8c16';
      case 'medium': return '#1890ff';
      default: return '#d9d9d9';
    }
  };

  const getPriorityTag = (priority: string) => {
    const colors = {
      urgent: 'red',
      high: 'orange',
      medium: 'blue',
      low: 'default'
    };

    const labels = {
      urgent: '紧急',
      high: '重要',
      medium: '一般',
      low: '普通'
    };

    return (
      <Tag color={colors[priority as keyof typeof colors]} size="small">
        {labels[priority as keyof typeof labels]}
      </Tag>
    );
  };

  const markAsRead = (alertId: string) => {
    setAlerts(prev =>
      prev.map(alert =>
        alert.id === alertId ? { ...alert, read: true } : alert
      )
    );
  };

  const markAllAsRead = () => {
    setAlerts(prev => prev.map(alert => ({ ...alert, read: true })));
  };

  const deleteAlert = (alertId: string) => {
    setAlerts(prev => prev.filter(alert => alert.id !== alertId));
  };

  const clearAllAlerts = () => {
    setAlerts([]);
  };

  const renderAlertItem = (alert: NewsAlert) => (
    <List.Item
      key={alert.id}
      className={`cursor-pointer hover:bg-gray-50 ${!alert.read ? 'bg-blue-50' : ''}`}
      actions={[
        !alert.read && (
          <Tooltip title="标记为已读">
            <Button
              type="text"
              size="small"
              icon={<CheckOutlined />}
              onClick={() => markAsRead(alert.id)}
            />
          </Tooltip>
        ),
        <Tooltip title="删除">
          <Button
            type="text"
            size="small"
            icon={<DeleteOutlined />}
            onClick={() => deleteAlert(alert.id)}
          />
        </Tooltip>
      ]}
    >
      <List.Item.Meta
        avatar={
          <Avatar
            style={{ backgroundColor: getPriorityColor(alert.priority) }}
            icon={getPriorityIcon(alert.priority)}
            size="small"
          />
        }
        title={
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 flex-1">
              <Text strong={!alert.read} className="text-sm">
                {alert.title}
              </Text>
              {getPriorityTag(alert.priority)}
            </div>
            <Text type="secondary" className="text-xs">
              {formatRelativeTime(alert.created_at)}
            </Text>
          </div>
        }
        description={
          <div>
            <div className="text-sm text-gray-600 mb-1">{alert.summary}</div>
            <div className="flex items-center space-x-2">
              {alert.categories.map((category, index) => (
                <Tag key={index} color="blue" size="small">
                  {category}
                </Tag>
              ))}
              {alert.mentioned_stocks.length > 0 && (
                <Tag color="orange" size="small">
                  相关股票: {alert.mentioned_stocks.join(', ')}
                </Tag>
              )}
            </div>
          </div>
        }
      />
    </List.Item>
  );

  return (
    <>
      {/* 通知铃铛按钮 */}
      <div className="relative">
        <Button
          type="text"
          icon={<BellOutlined />}
          onClick={() => setDrawerVisible(true)}
          className="relative"
        >
          {showBadge && unreadCount > 0 && (
            <Badge
              count={unreadCount}
              size="small"
              style={{ position: 'absolute', top: -4, right: -4 }}
            />
          )}
        </Button>

        {/* 连接状态指示器 */}
        <div
          className={`absolute -bottom-1 -right-1 w-2 h-2 rounded-full ${
            connectionStatus === ConnectionStatus.CONNECTED ? 'bg-green-500' : 'bg-red-500'
          }`}
        />
      </div>

      {/* 通知抽屉 */}
      <Drawer
        title={
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <BellOutlined />
              <span>新闻通知</span>
              {unreadCount > 0 && (
                <Badge count={unreadCount} color="blue" />
              )}
            </div>
            <Space>
              {unreadCount > 0 && (
                <Button
                  type="text"
                  size="small"
                  onClick={markAllAsRead}
                >
                  全部已读
                </Button>
              )}
              {alerts.length > 0 && (
                <Button
                  type="text"
                  size="small"
                  onClick={clearAllAlerts}
                >
                  清空
                </Button>
              )}
              <Tooltip title="设置">
                <Button
                  type="text"
                  size="small"
                  icon={<SettingOutlined />}
                  onClick={() => setSettingsVisible(true)}
                />
              </Tooltip>
            </Space>
          </div>
        }
        placement="right"
        width={400}
        open={drawerVisible}
        onClose={() => setDrawerVisible(false)}
      >
        {alerts.length > 0 ? (
          <List
            dataSource={alerts.slice(0, maxVisible)}
            renderItem={renderAlertItem}
            size="small"
          />
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500">
            <div className="text-center">
              <BellOutlined className="text-4xl mb-4 opacity-50" />
              <div>暂无通知</div>
              {connectionStatus !== ConnectionStatus.CONNECTED && (
                <Button
                  type="link"
                  size="small"
                  onClick={connectWebSocket}
                  className="mt-2"
                >
                  重新连接
                </Button>
              )}
            </div>
          </div>
        )}
      </Drawer>

      {/* 设置弹窗 */}
      <Drawer
        title="通知设置"
        placement="right"
        width={300}
        open={settingsVisible}
        onClose={() => setSettingsVisible(false)}
      >
        <div className="space-y-4">
          <div>
            <Title level={5}>连接状态</Title>
            <Tag color={connectionStatus === ConnectionStatus.CONNECTED ? 'green' : 'red'}>
              {connectionStatus === ConnectionStatus.CONNECTED ? '已连接' : '未连接'}
            </Tag>
          </div>

          <div>
            <Title level={5}>通知设置</Title>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span>显示数量</span>
                <Text>{maxVisible}</Text>
              </div>
              <div className="flex items-center justify-between">
                <span>显示角标</span>
                <Text>{showBadge ? '是' : '否'}</Text>
              </div>
              <div className="flex items-center justify-between">
                <span>提示音</span>
                <Text>{enableSound ? '开启' : '关闭'}</Text>
              </div>
            </div>
          </div>

          <div>
            <Title level={5}>统计信息</Title>
            <div className="space-y-1 text-sm">
              <div>总通知数: {alerts.length}</div>
              <div>未读数: {unreadCount}</div>
            </div>
          </div>
        </div>
      </Drawer>
    </>
  );
};

export default NewsNotification;