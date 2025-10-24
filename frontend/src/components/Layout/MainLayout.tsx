import React from 'react'
import { Layout } from 'antd'
import { Outlet } from 'react-router-dom'

const { Content } = Layout

const MainLayout: React.FC = () => {
  return (
    <Layout style={{ height: '100vh' }}>
      <Content style={{ padding: '24px', overflow: 'auto' }}>
        <Outlet />
      </Content>
    </Layout>
  )
}

export default MainLayout