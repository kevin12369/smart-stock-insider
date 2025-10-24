import React from 'react'
import { Card, Typography } from 'antd'

const { Title, Paragraph } = Typography

const Settings: React.FC = () => {
  return (
    <div>
      <Title level={2}>设置</Title>
      <Card>
        <Paragraph>
          设置页面正在开发中...
        </Paragraph>
      </Card>
    </div>
  )
}

export default Settings