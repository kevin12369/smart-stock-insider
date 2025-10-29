import React, { useState, useEffect, useRef } from 'react';
import {
  Modal,
  Card,
  Input,
  Button,
  Select,
  Space,
  Avatar,
  Typography,
  Divider,
  Tag,
  Tooltip,
  Switch,
  Rate,
  message,
  Spin,
  Empty,
  List,
  Dropdown,
  MenuProps
} from 'antd';
import {
  RobotOutlined,
  UserOutlined,
  SendOutlined,
  ClearOutlined,
  ExportOutlined,
  SettingOutlined,
  StarOutlined,
  HistoryOutlined,
  BulbOutlined,
  LoadingOutlined
} from '@ant-design/icons';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { api } from '@/services/api';
import { formatDateTime } from '@/utils/format';

const { TextArea } = Input;
const { Text, Title, Paragraph } = Typography;
const { Option } = Select;

// 分析师角色映射
const ANALYST_ROLES = {
  technical_analyst: {
    name: '技术分析师',
    icon: '📈',
    color: '#1890ff',
    description: '专业技术分析，基于技术指标和价格走势'
  },
  fundamental_analyst: {
    name: '基本面分析师',
    icon: '💼',
    color: '#52c41a',
    description: '基本面分析，关注公司财务和行业状况'
  },
  news_analyst: {
    name: '新闻分析师',
    icon: '📰',
    color: '#fa8c16',
    description: '新闻分析，基于市场情绪和政策变化'
  },
  risk_analyst: {
    name: '风控分析师',
    icon: '🛡️',
    color: '#f5222d',
    description: '风控分析，专注风险评估和控制策略'
  }
};

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  role?: string;
  symbol?: string;
  question?: string;
  confidence?: number;
  suggestions?: string[];
  reasoning?: string;
  timestamp: Date;
  loading?: boolean;
}

interface AIAnalysisDialogProps {
  visible: boolean;
  onClose: () => void;
  defaultSymbol?: string;
  defaultRole?: string;
}

const AIAnalysisDialog: React.FC<AIAnalysisDialogProps> = ({
  visible,
  onClose,
  defaultSymbol = '',
  defaultRole = 'technical_analyst'
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [selectedSymbol, setSelectedSymbol] = useState(defaultSymbol);
  const [selectedRole, setSelectedRole] = useState(defaultRole);
  const [isStreaming, setIsStreaming] = useState(false);
  const [useStream, setUseStream] = useState(true);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const [currentStreamingMessage, setCurrentStreamingMessage] = useState('');

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const queryClient = useQueryClient();

  // 获取分析建议
  const { data: suggestions = [], isLoading: suggestionsLoading } = useQuery({
    queryKey: ['ai-suggestions', selectedSymbol, selectedRole],
    queryFn: async () => {
      if (!selectedSymbol) return [];
      const response = await api.get(`/api/ai/suggestions/${selectedSymbol}`, {
        params: { role: selectedRole }
      });
      return response.data.suggestions || [];
    },
    enabled: !!selectedSymbol && showSuggestions,
  });

  // AI分析请求
  const analysisMutation = useMutation({
    mutationFn: async ({ question, symbol, role }: {
      question: string;
      symbol: string;
      role: string;
    }) => {
      const response = await api.post('/api/ai/analyze', {
        symbol,
        question,
        role,
        use_cache: true
      });
      return response.data;
    },
    onSuccess: (data) => {
      const assistantMessage: Message = {
        id: Date.now().toString(),
        type: 'assistant',
        content: data.answer,
        role: data.role,
        symbol: data.symbol,
        question: data.question,
        confidence: data.confidence,
        suggestions: data.suggestions,
        reasoning: data.reasoning,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, assistantMessage]);
    },
    onError: (error: any) => {
      message.error(`分析失败: ${error.response?.data?.message || error.message}`);
      const errorMessage: Message = {
        id: Date.now().toString(),
        type: 'assistant',
        content: '抱歉，分析过程中出现了错误，请稍后重试。',
        timestamp: new Date(),
        loading: false
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  });

  // 滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, currentStreamingMessage]);

  // 发送消息
  const handleSend = async () => {
    if (!inputValue.trim() || !selectedSymbol) {
      message.warning('请输入股票代码和分析问题');
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');

    if (useStream) {
      await handleStreamAnalysis(inputValue);
    } else {
      // 添加加载消息
      const loadingMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: '',
        timestamp: new Date(),
        loading: true
      };
      setMessages(prev => [...prev, loadingMessage]);

      analysisMutation.mutate({
        question: inputValue,
        symbol: selectedSymbol,
        role: selectedRole
      });
    }
  };

  // 流式分析
  const handleStreamAnalysis = async (question: string) => {
    setIsStreaming(true);
    setCurrentStreamingMessage('');

    try {
      abortControllerRef.current = new AbortController();

      const response = await fetch('/api/ai/analyze/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symbol: selectedSymbol,
          question,
          role: selectedRole,
          additional_context: {}
        }),
        signal: abortControllerRef.current.signal
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (reader) {
        let fullContent = '';
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              if (data === '[DONE]') {
                // 流式完成，创建最终消息
                const assistantMessage: Message = {
                  id: Date.now().toString(),
                  type: 'assistant',
                  content: fullContent,
                  role: selectedRole,
                  symbol: selectedSymbol,
                  question,
                  timestamp: new Date()
                };
                setMessages(prev => [...prev.slice(0, -1), assistantMessage]);
                setCurrentStreamingMessage('');
                setIsStreaming(false);
                return;
              }

              if (data.startsWith('ERROR:')) {
                const errorMsg = data.slice(6);
                message.error(`分析失败: ${errorMsg}`);
                setIsStreaming(false);
                return;
              }

              fullContent += data;
              setCurrentStreamingMessage(data);
            }
          }
        }
      }
    } catch (error: any) {
      if (error.name === 'AbortError') {
        message.info('分析已停止');
      } else {
        message.error(`流式分析失败: ${error.message}`);
      }
      setIsStreaming(false);
      setCurrentStreamingMessage('');
    }
  };

  // 停止流式分析
  const handleStopStreaming = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setIsStreaming(false);
    setCurrentStreamingMessage('');
  };

  // 使用建议
  const handleUseSuggestion = (suggestion: string) => {
    setInputValue(suggestion);
  };

  // 清空对话
  const handleClearMessages = () => {
    setMessages([]);
    setCurrentStreamingMessage('');
  };

  // 导出对话
  const handleExportConversation = () => {
    const content = messages.map(msg => {
      const role = msg.type === 'user' ? '用户' : ANALYST_ROLES[msg.role as keyof typeof ANALYST_ROLES]?.name || 'AI助手';
      const timestamp = formatDateTime(msg.timestamp);
      return `[${timestamp}] ${role}:\n${msg.content}\n`;
    }).join('\n---\n\n');

    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `AI分析对话_${selectedSymbol}_${Date.now()}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };

  // 渲染消息
  const renderMessage = (msg: Message) => {
    const isUser = msg.type === 'user';
    const roleInfo = !isUser && msg.role ? ANALYST_ROLES[msg.role as keyof typeof ANALYST_ROLES] : null;

    return (
      <div key={msg.id} className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
        <div className={`flex max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
          <Avatar
            className={isUser ? 'ml-2' : 'mr-2'}
            style={{ backgroundColor: isUser ? '#1890ff' : roleInfo?.color }}
            icon={isUser ? <UserOutlined /> : <RobotOutlined />}
          >
            {!isUser && roleInfo?.icon}
          </Avatar>

          <Card
            size="small"
            className={isUser ? 'ml-2' : 'mr-2'}
            style={{
              backgroundColor: isUser ? '#e6f7ff' : '#f5f5f5',
              border: isUser ? '1px solid #91d5ff' : '1px solid #d9d9d9'
            }}
          >
            {!isUser && roleInfo && (
              <div className="flex items-center justify-between mb-2">
                <Space>
                  <span className="text-base">{roleInfo.icon}</span>
                  <Text strong>{roleInfo.name}</Text>
                  {msg.confidence && (
                    <Tooltip title="置信度">
                      <Tag color="blue">{(msg.confidence * 100).toFixed(0)}%</Tag>
                    </Tooltip>
                  )}
                </Space>
                <Text type="secondary" className="text-xs">
                  {formatDateTime(msg.timestamp)}
                </Text>
              </div>
            )}

            {msg.loading ? (
              <div className="flex items-center space-x-2 py-2">
                <Spin size="small" />
                <Text type="secondary">正在分析中...</Text>
              </div>
            ) : (
              <div>
                <Paragraph className="mb-2">{msg.content}</Paragraph>

                {msg.reasoning && (
                  <details className="mt-2">
                    <summary className="cursor-pointer text-sm text-blue-600">
                      查看分析逻辑
                    </summary>
                    <Text className="text-sm text-gray-600 mt-1">
                      {msg.reasoning}
                    </Text>
                  </details>
                )}

                {msg.suggestions && msg.suggestions.length > 0 && (
                  <div className="mt-3">
                    <Text strong className="text-sm">建议：</Text>
                    <ul className="mt-1 ml-4 text-sm">
                      {msg.suggestions.map((suggestion, index) => (
                        <li key={index}>{suggestion}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </Card>
        </div>
      </div>
    );
  };

  // 角色选择菜单
  const roleMenuItems: MenuProps['items'] = Object.entries(ANALYST_ROLES).map(([key, value]) => ({
    key,
    label: (
      <div className="flex items-center space-x-2">
        <span>{value.icon}</span>
        <span>{value.name}</span>
      </div>
    ),
    onClick: () => setSelectedRole(key)
  }));

  return (
    <Modal
      title={
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <RobotOutlined />
            <span>AI投资分析师</span>
          </div>
          <Space>
            <Tooltip title="清空对话">
              <Button
                type="text"
                size="small"
                icon={<ClearOutlined />}
                onClick={handleClearMessages}
              />
            </Tooltip>
            <Tooltip title="导出对话">
              <Button
                type="text"
                size="small"
                icon={<ExportOutlined />}
                onClick={handleExportConversation}
              />
            </Tooltip>
            <Tooltip title="设置">
              <Button
                type="text"
                size="small"
                icon={<SettingOutlined />}
              />
            </Tooltip>
          </Space>
        </div>
      }
      open={visible}
      onCancel={onClose}
      width={900}
      height={700}
      footer={null}
      destroyOnClose
    >
      <div className="flex flex-col h-[600px]">
        {/* 工具栏 */}
        <div className="flex items-center justify-between p-4 border-b">
          <Space>
            <Input
              placeholder="股票代码"
              value={selectedSymbol}
              onChange={(e) => setSelectedSymbol(e.target.value.toUpperCase())}
              style={{ width: 120 }}
              maxLength={6}
            />
            <Dropdown menu={{ items: roleMenuItems }} placement="bottomLeft">
              <Button>
                <Space>
                  {ANALYST_ROLES[selectedRole as keyof typeof ANALYST_ROLES]?.icon}
                  {ANALYST_ROLES[selectedRole as keyof typeof ANALYST_ROLES]?.name}
                </Space>
              </Button>
            </Dropdown>
            <Tooltip title="流式响应">
              <Switch
                checked={useStream}
                onChange={setUseStream}
                size="small"
                checkedChildren="流式"
                unCheckedChildren="普通"
              />
            </Tooltip>
            <Tooltip title="显示建议">
              <Switch
                checked={showSuggestions}
                onChange={setShowSuggestions}
                size="small"
                checkedChildren="建议"
                unCheckedChildren="隐藏"
              />
            </Tooltip>
          </Space>

          {isStreaming && (
            <Button
              danger
              size="small"
              icon={<LoadingOutlined />}
              onClick={handleStopStreaming}
            >
              停止分析
            </Button>
          )}
        </div>

        <div className="flex flex-1 overflow-hidden">
          {/* 建议面板 */}
          {showSuggestions && suggestions.length > 0 && (
            <div className="w-64 border-r p-4 overflow-y-auto">
              <div className="flex items-center space-x-2 mb-3">
                <BulbOutlined className="text-yellow-500" />
                <Text strong>分析建议</Text>
              </div>
              {suggestionsLoading ? (
                <Spin size="small" />
              ) : (
                <Space direction="vertical" size="small" className="w-full">
                  {suggestions.map((suggestion: string, index: number) => (
                    <Button
                      key={index}
                      size="small"
                      block
                      className="text-left h-auto py-2 px-3 text-xs"
                      onClick={() => handleUseSuggestion(suggestion)}
                    >
                      {suggestion}
                    </Button>
                  ))}
                </Space>
              )}
            </div>
          )}

          {/* 对话区域 */}
          <div className="flex-1 flex flex-col">
            <div className="flex-1 overflow-y-auto p-4">
              {messages.length === 0 && !currentStreamingMessage ? (
                <Empty
                  image={Empty.PRESENTED_IMAGE_SIMPLE}
                  description="开始与AI分析师对话"
                  className="mt-20"
                />
              ) : (
                <>
                  {messages.map(renderMessage)}
                  {currentStreamingMessage && (
                    <div className="flex justify-start mb-4">
                      <div className="flex max-w-[80%]">
                        <Avatar
                          className="mr-2"
                          style={{ backgroundColor: ANALYST_ROLES[selectedRole as keyof typeof ANALYST_ROLES]?.color }}
                          icon={<RobotOutlined />}
                        >
                          {ANALYST_ROLES[selectedRole as keyof typeof ANALYST_ROLES]?.icon}
                        </Avatar>
                        <Card size="small" className="mr-2" style={{ backgroundColor: '#f5f5f5' }}>
                          <div className="flex items-center space-x-2">
                            <Spin size="small" />
                            <Text>{currentStreamingMessage}</Text>
                          </div>
                        </Card>
                      </div>
                    </div>
                  )}
                </>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* 输入区域 */}
            <div className="border-t p-4">
              <div className="flex items-end space-x-2">
                <TextArea
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="请输入您的投资分析问题..."
                  autoSize={{ minRows: 1, maxRows: 4 }}
                  onPressEnter={(e) => {
                    if (!e.shiftKey) {
                      e.preventDefault();
                      handleSend();
                    }
                  }}
                  disabled={isStreaming}
                />
                <Button
                  type="primary"
                  icon={<SendOutlined />}
                  onClick={handleSend}
                  disabled={!inputValue.trim() || !selectedSymbol || isStreaming}
                  loading={analysisMutation.isLoading || isStreaming}
                >
                  发送
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Modal>
  );
};

export default AIAnalysisDialog;