import React, { useState } from 'react'
import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { Layout, Menu, Button, Avatar, Typography, theme } from 'antd'
import {
  DashboardOutlined,
  BarChartOutlined,
  RobotOutlined,
  SettingOutlined,
  UserOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined
} from '@ant-design/icons'

// 页面组件 - 使用实际存在的组件
import Dashboard from './pages/Dashboard'
import AIAnalysis from './pages/AIAnalysis'

const { Header, Sider, Content } = Layout
const { Title } = Typography

// 菜单配置
const menuItems = [
  {
    key: '/dashboard',
    icon: <DashboardOutlined />,
    label: '仪表板',
  },
  {
    key: '/ai-analysis',
    icon: <RobotOutlined />,
    label: 'AI分析',
  },
]

const App: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false)
  const location = useLocation()
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken()

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        style={{
          background: colorBgContainer,
          borderRight: '1px solid #f0f0f0'
        }}
      >
        <div style={{
          height: 64,
          padding: '16px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: collapsed ? 'center' : 'flex-start'
        }}>
          <RobotOutlined style={{ fontSize: '24px', color: '#1890ff' }} />
          {!collapsed && (
            <Title level={4} style={{ margin: '0 0 0 8px', color: '#1890ff' }}>
              智股通
            </Title>
          )}
        </div>
        <Menu
          theme="light"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          style={{ borderRight: 0 }}
        />
      </Sider>

      <Layout>
        <Header
          style={{
            padding: '0 16px',
            background: colorBgContainer,
            borderBottom: '1px solid #f0f0f0',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}
        >
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
            style={{
              fontSize: '16px',
              width: 64,
              height: 64,
            }}
          />

          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <Avatar icon={<UserOutlined />} />
          </div>
        </Header>

        <Content
          style={{
            margin: '16px',
            padding: 24,
            background: colorBgContainer,
            borderRadius: borderRadiusLG,
            minHeight: 280,
            overflow: 'auto'
          }}
        >
          <Routes>
            {/* 默认重定向到仪表板 */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />

            {/* 主要功能页面 */}
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/ai-analysis" element={<AIAnalysis />} />

            {/* 404页面 */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  )
}

export default App