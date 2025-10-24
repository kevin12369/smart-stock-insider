import React from 'react'
import { Menu, Layout } from 'antd'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  DashboardOutlined,
  PieChartOutlined,
  NotificationOutlined,
  SettingOutlined,
  BarChartOutlined,
  BellOutlined
} from '@ant-design/icons'

const { Sider } = Layout

interface NavigationMenuProps {
  collapsed: boolean
}

const NavigationMenu: React.FC<NavigationMenuProps> = ({ collapsed }) => {
  const navigate = useNavigate()
  const location = useLocation()

  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: '仪表盘'
    },
    {
      key: '/portfolio',
      icon: <PieChartOutlined />,
      label: '投资组合'
    },
    {
      key: '/portfolio-analysis',
      icon: <BarChartOutlined />,
      label: '组合分析'
    },
    {
      key: '/news',
      icon: <NotificationOutlined />,
      label: '新闻中心'
    },
    {
      key: '/push',
      icon: <BellOutlined />,
      label: '推送通知'
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: '系统设置'
    }
  ]

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key)
  }

  return (
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
  )
}

export default NavigationMenu