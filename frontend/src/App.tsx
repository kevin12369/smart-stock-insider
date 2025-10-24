import React, { useEffect, useState } from 'react'
import { Layout, Typography, Button, Space, message, ConfigProvider, Menu } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import 'dayjs/locale/zh-cn'
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation } from 'react-router-dom'
import {
  DashboardOutlined,
  PieChartOutlined,
  NotificationOutlined,
  SettingOutlined,
  MenuUnfoldOutlined,
  MenuFoldOutlined
} from '@ant-design/icons'
import { createLazyComponent, preloadCriticalRoutes } from './utils/lazyLoad'
import './styles/index.css'

// 懒加载组件
const Dashboard = createLazyComponent(() => import('./pages/Dashboard'))
const EnhancedDashboard = createLazyComponent(() => import('./pages/EnhancedDashboard'), true) // 预加载
const PortfolioManager = createLazyComponent(() => import('./pages/PortfolioManager'))
const PortfolioAnalysis = createLazyComponent(() => import('./pages/PortfolioAnalysis'))
const NewsHub = createLazyComponent(() => import('./pages/NewsHub'))
const PushNotification = createLazyComponent(() => import('./pages/PushNotification'))

const { Header, Content, Sider } = Layout
const { Title } = Typography

// 菜单项配置
const menuItems = [
  {
    key: '/dashboard',
    icon: <DashboardOutlined />,
    label: '仪表盘'
  },
  {
    key: '/enhanced-dashboard',
    icon: <DashboardOutlined />,
    label: '智能控制台'
  },
  {
    key: '/portfolio',
    icon: <PieChartOutlined />,
    label: '投资组合'
  },
  {
    key: '/portfolio-analysis',
    icon: <PieChartOutlined />,
    label: '组合分析'
  },
  {
    key: '/news',
    icon: <NotificationOutlined />,
    label: '新闻中心'
  },
  {
    key: '/push',
    icon: <NotificationOutlined />,
    label: '推送通知'
  },
  {
    key: '/settings',
    icon: <SettingOutlined />,
    label: '系统设置'
  }
]

// 内部组件：Main App Content
const MainContent: React.FC = () => {
  const [loading, setLoading] = useState(true)
  const [appInfo, setAppInfo] = useState({ name: '智股通', version: '1.0.0' })

  useEffect(() => {
    const initApp = async () => {
      try {
        // 预加载关键路由
        preloadCriticalRoutes()

        // 这里可以调用后端API获取应用信息
        setAppInfo({ name: '智股通', version: '1.0.0' })
        message.success('欢迎使用智股通 - 智能量化投研平台')
      } catch (error) {
        console.error('Failed to initialize app:', error)
        message.error('应用初始化失败')
      } finally {
        setLoading(false)
      }
    }

    initApp()
  }, [])

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        fontSize: '18px',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '24px', marginBottom: '16px' }}>智股通</div>
          <div>正在启动应用...</div>
        </div>
      </div>
    )
  }

  return (
    <Layout style={{ height: '100vh' }}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/enhanced-dashboard" element={<EnhancedDashboard />} />
        <Route path="/portfolio" element={<PortfolioManager />} />
        <Route path="/portfolio-analysis" element={<PortfolioAnalysis />} />
        <Route path="/news" element={<NewsHub />} />
        <Route path="/push" element={<PushNotification />} />
        <Route path="/" element={<EnhancedDashboard />} />
      </Routes>
    </Layout>
  )
}

// 布局组件
const AppLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key)
  }

  return (
    <Layout style={{ height: '100vh' }}>
      <Header style={{
        background: '#fff',
        padding: '0 24px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
            style={{ marginRight: '16px' }}
          />
          <Title level={3} style={{ margin: 0, color: '#1890ff' }}>
            智股通 - 智能量化投研平台
          </Title>
        </div>
        <Space>
          <span>v1.0.0</span>
          <Button type="primary" size="small">
            设置
          </Button>
        </Space>
      </Header>

      <Layout>
        <Sider
          trigger={null}
          collapsible
          collapsed={collapsed}
          style={{
            background: '#fff',
            borderRight: '1px solid #f0f0f0'
          }}
          width={200}
        >
          <Menu
            mode="inline"
            selectedKeys={[location.pathname]}
            items={menuItems}
            onClick={handleMenuClick}
            style={{ height: '100%', borderRight: 0 }}
          />
        </Sider>

        <Content style={{ padding: 0, background: '#f5f5f5', overflow: 'auto' }}>
          <MainContent />
        </Content>
      </Layout>
    </Layout>
  )
}

// 主App组件
const App: React.FC = () => {
  return (
    <ConfigProvider locale={zhCN}>
      <Router>
        <AppLayout />
      </Router>
    </ConfigProvider>
  )
}

export default App