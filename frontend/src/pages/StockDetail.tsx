import React from 'react'
import { Card, Typography } from 'antd'

const { Title, Paragraph } = Typography

const StockDetail: React.FC = () => {
  return (
    <div>
      <Title level={2}>股票详情</Title>
      <Card>
        <Paragraph>
          股票详情页面正在开发中...
        </Paragraph>
      </Card>
    </div>
  )
}

export default StockDetail