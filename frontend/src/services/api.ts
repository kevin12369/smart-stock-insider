// API服务 - 与Wails后端通信
export interface ApiResponse {
  success: boolean
  message: string
  data?: any
  error?: string
  time: string
}

export interface StockBasicInfo {
  code: string
  name: string
  industry?: string
  market?: string
  listing_date?: string
  created_at: string
}

export interface StockDailyData {
  id: number
  code: string
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
  amount: number
  change: number
  change_pct: number
  created_at: string
}

export interface SystemInfo {
  app_name: string
  app_version: string
  build_time: string
  database?: {
    path: string
    connected: boolean
    created_at: string
    stats?: Record<string, number>
  }
  database_size?: string
  status: string
  uptime: string
}

export interface TechnicalSignal {
  id: number
  code: string
  date: string
  signal_type: string
  signal_value: number
  strength: string
  description: string
  confidence: number
  created_at: string
}

export interface SignalConfig {
  id: number
  signal_type: string
  weight: number
  enabled: boolean
  description: string
  created_at: string
  updated_at: string
}

export interface SignalCombo {
  id: number
  name: string
  description: string
  signals: SignalConfig[]
  enabled: boolean
  created_at: string
  updated_at: string
}

export interface ComboResult {
  id: number
  combo_id: number
  combo_name: string
  code: string
  date: string
  score: number
  signal_count: number
  buy_signals: number
  sell_signals: number
  description: string
  created_at: string
}

class ApiService {
  // 模拟Wails调用，实际使用时替换为真实的Wails绑定
  private callBackend = async (method: string, ...args: any[]): Promise<any> => {
    // 这里是临时的模拟实现
    // 实际部署时会替换为真实的Wails调用

    console.log(`调用后端方法: ${method}`, args)

    // 模拟延迟
    await new Promise(resolve => setTimeout(resolve, 100))

    switch (method) {
      case 'GetSystemInfo':
        return {
          success: true,
          message: '获取系统信息成功',
          data: {
            app_name: '智股通',
            app_version: '1.0.0',
            build_time: new Date().toLocaleString(),
            database: {
              path: 'data/smart_stock.db',
              connected: true,
              created_at: new Date().toLocaleString(),
              stats: {
                stock_basic: 2,
                stock_daily: 100,
                technical_signals: 15,
                ai_analysis_log: 0
              }
            },
            database_size: '2.45 MB',
            status: 'running',
            uptime: '2h 15m'
          },
          time: new Date().toLocaleString()
        }

      case 'HealthCheck':
        return {
          success: true,
          message: '系统正常',
          data: {
            database: true,
            healthy: true,
            timestamp: new Date().toLocaleString()
          },
          time: new Date().toLocaleString()
        }

      case 'SearchStocks':
        const [keyword, searchLimit, offset] = args
        return {
          success: true,
          message: '搜索股票成功',
          data: {
            stocks: [
              {
                code: '000001',
                name: '平安银行',
                industry: '银行',
                market: '深交所主板',
                listing_date: '1991-04-03',
                created_at: '2024-01-01 10:00:00'
              },
              {
                code: '000002',
                name: '万科A',
                industry: '房地产',
                market: '深交所主板',
                listing_date: '1991-01-29',
                created_at: '2024-01-01 10:00:00'
              }
            ].filter(stock =>
              !keyword ||
              stock.code.includes(keyword) ||
              stock.name.includes(keyword)
            ).slice(offset, offset + searchLimit),
            total: 2,
            limit: searchLimit,
            offset
          },
          time: new Date().toLocaleString()
        }

      case 'GetStockDailyData':
        const [code, dataLimit] = args
        const mockData = Array.from({ length: Math.min(dataLimit, 30) }, (_, i) => ({
          id: i + 1,
          code,
          date: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          open: 10 + Math.random() * 5,
          high: 11 + Math.random() * 5,
          low: 9 + Math.random() * 4,
          close: 10.5 + Math.random() * 4,
          volume: Math.floor(Math.random() * 1000000),
          amount: Math.floor(Math.random() * 100000000),
          change: (Math.random() - 0.5) * 2,
          change_pct: (Math.random() - 0.5) * 10,
          created_at: new Date().toLocaleString()
        }))

        return {
          success: true,
          message: '获取日线数据成功',
          data: mockData,
          time: new Date().toLocaleString()
        }

      case 'GetTechnicalSignals':
        const [signalCode] = args
        return {
          success: true,
          message: '获取技术信号成功',
          data: {
            stock_code: signalCode,
            signals: [
              {
                id: 1,
                code: signalCode,
                date: new Date().toISOString().split('T')[0],
                signal_type: 'MACD',
                signal_value: 0.15,
                strength: 'BUY',
                description: 'MACD金叉信号',
                confidence: 0.75,
                created_at: new Date().toLocaleString()
              },
              {
                id: 2,
                code: signalCode,
                date: new Date().toISOString().split('T')[0],
                signal_type: 'RSI',
                signal_value: 25.5,
                strength: 'STRONG_BUY',
                description: 'RSI超卖信号',
                confidence: 0.68,
                created_at: new Date().toLocaleString()
              }
            ],
            signal_count: 2
          },
          time: new Date().toLocaleString()
        }

      case 'BackupData':
        return {
          success: true,
          message: '数据备份成功',
          data: {
            backup_path: `backup/smart_stock_backup_${new Date().toISOString().slice(0,10).replace(/-/g, '')}_${new Date().toTimeString().slice(0,8).replace(/:/g, '')}.db`,
            backup_time: new Date().toLocaleString()
          },
          time: new Date().toLocaleString()
        }

      case 'GetSignalConfigs':
        return {
          success: true,
          message: '获取信号配置成功',
          data: [
            { id: 1, signal_type: 'MACD', weight: 1.2, enabled: true, description: 'MACD指标权重', created_at: new Date().toLocaleString(), updated_at: new Date().toLocaleString() },
            { id: 2, signal_type: 'RSI', weight: 1.0, enabled: true, description: 'RSI指标权重', created_at: new Date().toLocaleString(), updated_at: new Date().toLocaleString() },
            { id: 3, signal_type: 'KDJ', weight: 0.8, enabled: true, description: 'KDJ指标权重', created_at: new Date().toLocaleString(), updated_at: new Date().toLocaleString() },
            { id: 4, signal_type: 'BOLL', weight: 0.9, enabled: true, description: '布林带指标权重', created_at: new Date().toLocaleString(), updated_at: new Date().toLocaleString() },
            { id: 5, signal_type: 'CCI', weight: 0.7, enabled: true, description: 'CCI指标权重', created_at: new Date().toLocaleString(), updated_at: new Date().toLocaleString() },
            { id: 6, signal_type: 'WR', weight: 0.6, enabled: true, description: '威廉指标权重', created_at: new Date().toLocaleString(), updated_at: new Date().toLocaleString() },
            { id: 7, signal_type: 'MA', weight: 0.5, enabled: true, description: '移动平均线权重', created_at: new Date().toLocaleString(), updated_at: new Date().toLocaleString() },
          ],
          time: new Date().toLocaleString()
        }

      case 'GetSignalCombos':
        return {
          success: true,
          message: '获取信号组合成功',
          data: [
            {
              id: 1,
              name: '技术分析综合策略',
              description: '综合多种技术指标的量化策略',
              enabled: true,
              created_at: new Date().toLocaleString(),
              updated_at: new Date().toLocaleString(),
              signals: [
                { id: 1, signal_type: 'MACD', weight: 1.2, enabled: true, description: 'MACD指标权重', created_at: new Date().toLocaleString(), updated_at: new Date().toLocaleString() },
                { id: 2, signal_type: 'RSI', weight: 1.0, enabled: true, description: 'RSI指标权重', created_at: new Date().toLocaleString(), updated_at: new Date().toLocaleString() },
                { id: 3, signal_type: 'KDJ', weight: 0.8, enabled: true, description: 'KDJ指标权重', created_at: new Date().toLocaleString(), updated_at: new Date().toLocaleString() },
              ]
            },
            {
              id: 2,
              name: '趋势跟踪策略',
              description: '主要使用MACD和移动平均线的趋势策略',
              enabled: true,
              created_at: new Date().toLocaleString(),
              updated_at: new Date().toLocaleString(),
              signals: [
                { id: 1, signal_type: 'MACD', weight: 1.5, enabled: true, description: 'MACD指标权重增加', created_at: new Date().toLocaleString(), updated_at: new Date().toLocaleString() },
                { id: 7, signal_type: 'MA', weight: 1.0, enabled: true, description: '移动平均线权重', created_at: new Date().toLocaleString(), updated_at: new Date().toLocaleString() },
                { id: 2, signal_type: 'RSI', weight: 0.5, enabled: true, description: 'RSI指标权重减少', created_at: new Date().toLocaleString(), updated_at: new Date().toLocaleString() },
              ]
            },
            {
              id: 3,
              name: '震荡策略',
              description: '适用于震荡市场的超买超卖策略',
              enabled: true,
              created_at: new Date().toLocaleString(),
              updated_at: new Date().toLocaleString(),
              signals: [
                { id: 2, signal_type: 'RSI', weight: 1.5, enabled: true, description: 'RSI指标权重增加', created_at: new Date().toLocaleString(), updated_at: new Date().toLocaleString() },
                { id: 6, signal_type: 'WR', weight: 1.2, enabled: true, description: '威廉指标权重增加', created_at: new Date().toLocaleString(), updated_at: new Date().toLocaleString() },
                { id: 5, signal_type: 'CCI', weight: 1.0, enabled: true, description: 'CCI指标权重', created_at: new Date().toLocaleString(), updated_at: new Date().toLocaleString() },
              ]
            }
          ],
          time: new Date().toLocaleString()
        }

      case 'CalculateComboScore':
        const [comboId, stockSymbol] = args
        return {
          success: true,
          message: '计算组合分数成功',
          data: {
            combo_id: comboId,
            combo_name: '技术分析综合策略',
            stock_code: stockSymbol,
            score: 2.45,
            signals: [
              { signal_type: 'MACD', signal_value: 0.15, strength: 'BUY' },
              { signal_type: 'RSI', signal_value: 25.5, strength: 'STRONG_BUY' },
              { signal_type: 'KDJ', signal_value: 0.8, strength: 'BUY' },
            ]
          },
          time: new Date().toLocaleString()
        }

      case 'GetComboResults':
        const [resultComboID, resultCode, resultLimit] = args
        const mockResults = Array.from({ length: Math.min(resultLimit, 10) }, (_, i) => ({
          id: i + 1,
          combo_id: resultComboID,
          combo_name: '技术分析综合策略',
          code: resultCode,
          date: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          score: Math.random() * 4 - 1,
          signal_count: Math.floor(Math.random() * 5) + 2,
          buy_signals: Math.floor(Math.random() * 3) + 1,
          sell_signals: Math.floor(Math.random() * 2),
          description: '综合技术分析信号结果',
          created_at: new Date().toLocaleString()
        }))

        return {
          success: true,
          message: '获取组合结果成功',
          data: mockResults,
          time: new Date().toLocaleString()
        }

      case 'SyncExternalData':
        const [syncCodes] = args
        return {
          success: true,
          message: '同步外部数据成功',
          data: {
            synced_count: syncCodes?.length || 0,
            sync_time: new Date().toLocaleString(),
            details: syncCodes?.map((code: string) => ({ code, status: 'success' })) || []
          },
          time: new Date().toLocaleString()
        }

      case 'GetExternalStockList':
        const [extLimit, extOffset] = args
        const mockExternalStocks = Array.from({ length: Math.min(extLimit, 20) }, (_, i) => ({
          code: `${600000 + i + extOffset}`,
          name: `股票${600000 + i + extOffset}`,
          price: (Math.random() * 50 + 10).toFixed(2),
          change: (Math.random() * 4 - 2).toFixed(2),
          change_percent: (Math.random() * 8 - 4).toFixed(2),
          volume: Math.floor(Math.random() * 1000000),
          amount: Math.floor(Math.random() * 50000000),
          market: 'sh',
          update_time: new Date().toLocaleString()
        }))

        return {
          success: true,
          message: '获取外部股票列表成功',
          data: mockExternalStocks,
          time: new Date().toLocaleString()
        }

      case 'GetExternalRealtimeData':
        const [realtimeCode] = args
        return {
          success: true,
          message: '获取实时数据成功',
          data: {
            code: realtimeCode,
            name: `股票${realtimeCode}`,
            price: (Math.random() * 50 + 10).toFixed(2),
            open: (Math.random() * 50 + 10).toFixed(2),
            high: (Math.random() * 50 + 10).toFixed(2),
            low: (Math.random() * 50 + 10).toFixed(2),
            pre_close: (Math.random() * 50 + 10).toFixed(2),
            change: (Math.random() * 4 - 2).toFixed(2),
            change_percent: (Math.random() * 8 - 4).toFixed(2),
            volume: Math.floor(Math.random() * 1000000),
            amount: Math.floor(Math.random() * 50000000),
            update_time: new Date().toLocaleString()
          },
          time: new Date().toLocaleString()
        }

      case 'GetExternalDailyData':
        const [dailyCode, , , dailyLimit] = args
        const mockDailyData = Array.from({ length: Math.min(dailyLimit, 100) }, (_, i) => ({
          code: dailyCode,
          date: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          open: (Math.random() * 50 + 10).toFixed(2),
          high: (Math.random() * 50 + 10).toFixed(2),
          low: (Math.random() * 50 + 10).toFixed(2),
          close: (Math.random() * 50 + 10).toFixed(2),
          volume: Math.floor(Math.random() * 1000000),
          amount: Math.floor(Math.random() * 50000000)
        }))

        return {
          success: true,
          message: '获取日线数据成功',
          data: mockDailyData,
          time: new Date().toLocaleString()
        }

      case 'RefreshExternalCache':
        return {
          success: true,
          message: '刷新缓存成功',
          data: {
            cache_cleared: true,
            refresh_time: new Date().toLocaleString()
          },
          time: new Date().toLocaleString()
        }

      case 'GetExternalServiceStatus':
        return {
          success: true,
          message: '获取服务状态成功',
          data: {
            cache_size: Math.floor(Math.random() * 1000),
            cache_enabled: true,
            request_count: Math.floor(Math.random() * 10000),
            error_count: Math.floor(Math.random() * 10),
            supported_markets: ['sh', 'sz', 'bj'],
            update_time: new Date().toLocaleString()
          },
          time: new Date().toLocaleString()
        }

      case 'GetMarketIndices':
        return {
          success: true,
          message: '获取市场指数成功',
          data: [
            {
              code: 'sh000001',
              name: '上证指数',
              price: (Math.random() * 1000 + 3000).toFixed(2),
              change: (Math.random() * 100 - 50).toFixed(2),
              change_percent: (Math.random() * 4 - 2).toFixed(2),
              volume: Math.floor(Math.random() * 10000000),
              amount: Math.floor(Math.random() * 500000000),
              update_time: new Date().toLocaleString()
            },
            {
              code: 'sz399001',
              name: '深证成指',
              price: (Math.random() * 2000 + 10000).toFixed(2),
              change: (Math.random() * 200 - 100).toFixed(2),
              change_percent: (Math.random() * 4 - 2).toFixed(2),
              volume: Math.floor(Math.random() * 8000000),
              amount: Math.floor(Math.random() * 400000000),
              update_time: new Date().toLocaleString()
            },
            {
              code: 'sz399006',
              name: '创业板指',
              price: (Math.random() * 500 + 2000).toFixed(2),
              change: (Math.random() * 50 - 25).toFixed(2),
              change_percent: (Math.random() * 4 - 2).toFixed(2),
              volume: Math.floor(Math.random() * 6000000),
              amount: Math.floor(Math.random() * 300000000),
              update_time: new Date().toLocaleString()
            }
          ],
          time: new Date().toLocaleString()
        }

      case 'ExportData':
        const [dataType, outputPath] = args
        const mockRecordCount = Math.floor(Math.random() * 10000) + 1000
        const mockFileSize = mockRecordCount * 100 // 模拟文件大小

        return {
          success: true,
          message: '导出成功',
          data: {
            success: true,
            message: '导出成功',
            file_path: outputPath,
            record_count: mockRecordCount,
            file_size: mockFileSize,
            export_time: new Date().toLocaleString(),
            data_type: dataType
          },
          time: new Date().toLocaleString()
        }

      case 'ImportData':
        const [,] = args
        const mockTotalRecords = Math.floor(Math.random() * 5000) + 500
        const mockSuccessCount = Math.floor(mockTotalRecords * 0.9)
        const mockErrorCount = Math.floor(mockTotalRecords * 0.05)
        const mockDuplicateCount = Math.floor(mockTotalRecords * 0.05)

        return {
          success: true,
          message: '导入成功',
          data: {
            success: true,
            message: '导入成功',
            total_records: mockTotalRecords,
            success_count: mockSuccessCount,
            error_count: mockErrorCount,
            duplicate_count: mockDuplicateCount,
            import_time: new Date().toLocaleString(),
            errors: mockErrorCount > 0 ? [
              '第15行：日期格式错误',
              '第23行：价格数据无效',
              '第45行：重复记录'
            ] : []
          },
          time: new Date().toLocaleString()
        }

      case 'GetExportTemplate':
        const [templateType, templateFormat] = args
        let templateContent = ''

        if (templateType === 'stock_basic') {
          if (templateFormat === 'csv') {
            templateContent = '代码,名称,行业,市场,上市日期\n000001,平安银行,银行,sh,1991-04-03\n600000,浦发银行,银行,sh,1999-11-10\n'
          } else {
            templateContent = JSON.stringify([
              { code: '000001', name: '平安银行', industry: '银行', market: 'sh', listing_date: '1991-04-03' },
              { code: '600000', name: '浦发银行', industry: '银行', market: 'sh', listing_date: '1999-11-10' }
            ], null, 2)
          }
        } else if (templateType === 'stock_daily') {
          if (templateFormat === 'csv') {
            templateContent = '代码,日期,开盘价,最高价,最低价,收盘价,成交量,成交额\n000001,2024-01-01,10.50,10.80,10.20,10.75,1000000,10750000.00\n'
          } else {
            templateContent = JSON.stringify([
              { code: '000001', date: '2024-01-01', open: 10.50, high: 10.80, low: 10.20, close: 10.75, volume: 1000000, amount: 10750000.00 }
            ], null, 2)
          }
        }

        return {
          success: true,
          message: '获取模板成功',
          data: {
            template: templateContent,
            filename: `${templateType}_template.${templateFormat}`
          },
          time: new Date().toLocaleString()
        }

      case 'BatchExportStocks':
        const [, , , exportFormat] = args
        return {
          success: true,
          message: '批量导出成功',
          data: {
            success: true,
            message: '批量导出成功',
            file_path: `exports/stocks_batch_${new Date().toISOString().slice(0,10).replace(/-/g, '')}.${exportFormat}`,
            record_count: Math.floor(Math.random() * 50000) + 5000,
            file_size: Math.floor(Math.random() * 10000000) + 1000000,
            export_time: new Date().toLocaleString(),
            data_type: 'all'
          },
          time: new Date().toLocaleString()
        }

      case 'CheckDataQuality':
        return {
          success: true,
          message: '数据质量检查完成',
          data: {
            total_records: Math.floor(Math.random() * 10000) + 5000,
            total_issues: Math.floor(Math.random() * 50) + 5,
            issues_by_type: {
              missing_data: Math.floor(Math.random() * 10) + 2,
              outlier: Math.floor(Math.random() * 15) + 3,
              inconsistency: Math.floor(Math.random() * 8) + 1,
              duplicate: Math.floor(Math.random() * 5) + 1
            },
            issues_by_severity: {
              low: Math.floor(Math.random() * 15) + 5,
              medium: Math.floor(Math.random() * 10) + 3,
              high: Math.floor(Math.random() * 5) + 1,
              critical: Math.floor(Math.random() * 2)
            },
            quality_score: Math.random() * 30 + 70, // 70-100分
            check_date: new Date().toLocaleString(),
            summary: '数据质量良好，存在一些需要注意的问题',
            recommendations: [
              '补充缺失的数据，确保数据完整性',
              '检查并处理异常值，确保数据准确性',
              '统一数据格式和标准，提高数据一致性'
            ]
          },
          time: new Date().toLocaleString()
        }

      case 'GetDataQualityMetrics':
        return {
          success: true,
          message: '获取数据质量指标成功',
          data: {
            completeness: Math.random() * 15 + 85, // 85-100%
            accuracy: Math.random() * 10 + 90,      // 90-100%
            consistency: Math.random() * 20 + 80,   // 80-100%
            timeliness: Math.random() * 30 + 70,     // 70-100%
            validity: Math.random() * 10 + 90,      // 90-100%
            overall_score: Math.random() * 20 + 80, // 80-100%
            last_checked: new Date().toLocaleString()
          },
          time: new Date().toLocaleString()
        }

      case 'DetectAnomalies':
        const [anomalyStockCode] = args
        const anomalyCount = Math.floor(Math.random() * 5)
        const mockAnomalies = Array.from({ length: anomalyCount }, (_, i) => ({
          stock_code: anomalyStockCode,
          detection_type: ['price_spike', 'volume_anomaly', 'gap'][Math.floor(Math.random() * 3)],
          anomaly_value: Math.random() * 0.2 - 0.1, // -10% 到 +10%
          expected_range: '-5% ~ 5%',
          confidence: Math.random() * 0.5 + 0.5, // 0.5-1.0
          record_date: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          description: ['价格异常波动', '成交量异常', '向上跳空', '向下跳空'][Math.floor(Math.random() * 4)],
          detected_at: new Date().toLocaleString()
        }))

        return {
          success: true,
          message: `异常检测完成，发现${anomalyCount}个异常`,
          data: mockAnomalies,
          time: new Date().toLocaleString()
        }

      case 'BatchDetectAnomalies':
        const [batchCodes, days] = args
        const stockList = batchCodes.split(',')
        const batchAnomalies: { [key: string]: any[] } = {}

        stockList.forEach((code: string) => {
          const codeAnomalies = Array.from({ length: Math.floor(Math.random() * 3) }, (_, i) => ({
            stock_code: code.trim(),
            detection_type: ['price_spike', 'volume_anomaly', 'gap'][Math.floor(Math.random() * 3)],
            anomaly_value: Math.random() * 0.2 - 0.1,
            expected_range: '-5% ~ 5%',
            confidence: Math.random() * 0.5 + 0.5,
            record_date: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
            description: '检测到异常数据',
            detected_at: new Date().toLocaleString()
          }))
          batchAnomalies[code.trim()] = codeAnomalies
        })

        return {
          success: true,
          message: '批量异常检测完成',
          data: {
            total_stocks: stockList.length,
            days_checked: days,
            anomalies: batchAnomalies,
            check_time: new Date().toLocaleString()
          },
          time: new Date().toLocaleString()
        }

      default:
        return {
          success: false,
          message: '未知方法',
          error: `Method ${method} not found`,
          time: new Date().toLocaleString()
        }
    }
  }

  // 获取系统信息
  async getSystemInfo(): Promise<ApiResponse> {
    return this.callBackend('GetSystemInfo')
  }

  // 健康检查
  async healthCheck(): Promise<ApiResponse> {
    return this.callBackend('HealthCheck')
  }

  // 搜索股票
  async searchStocks(keyword: string, searchLimit: number = 20, offset: number = 0): Promise<ApiResponse> {
    return this.callBackend('SearchStocks', keyword, searchLimit, offset)
  }

  // 获取股票基本信息
  async getStockInfo(code: string): Promise<ApiResponse> {
    return this.callBackend('GetStockInfo', code)
  }

  // 获取股票日线数据
  async getStockDailyData(code: string, dataLimit: number = 30): Promise<ApiResponse> {
    return this.callBackend('GetStockDailyData', code, dataLimit)
  }

  // 获取技术信号
  async getTechnicalSignals(code: string): Promise<ApiResponse> {
    return this.callBackend('GetTechnicalSignals', code)
  }

  // 备份数据
  async backupData(): Promise<ApiResponse> {
    return this.callBackend('BackupData')
  }

  // 添加股票
  async addStock(code: string, name: string, industry?: string, market?: string, listingDate?: string): Promise<ApiResponse> {
    return this.callBackend('AddStock', code, name, industry, market, listingDate)
  }

  // 获取股票统计信息
  async getStockStats(code: string): Promise<ApiResponse> {
    return this.callBackend('GetStockStats', code)
  }

  // 信号配置相关方法

  // 获取信号配置列表
  async getSignalConfigs(): Promise<ApiResponse> {
    return this.callBackend('GetSignalConfigs')
  }

  // 获取信号组合列表
  async getSignalCombos(): Promise<ApiResponse> {
    return this.callBackend('GetSignalCombos')
  }

  // 更新信号配置
  async updateSignalConfig(config: SignalConfig): Promise<ApiResponse> {
    return this.callBackend('UpdateSignalConfig', config)
  }

  // 更新信号组合
  async updateSignalCombo(combo: SignalCombo): Promise<ApiResponse> {
    return this.callBackend('UpdateSignalCombo', combo)
  }

  // 计算组合信号分数
  async calculateComboScore(comboID: number, stockCode: string): Promise<ApiResponse> {
    return this.callBackend('CalculateComboScore', comboID, stockCode)
  }

  // 获取组合信号结果
  async getComboResults(comboID: number, stockCode: string, limit: number = 30): Promise<ApiResponse> {
    return this.callBackend('GetComboResults', comboID, stockCode, limit)
  }

  // 外部数据源相关方法

  // 同步外部数据源
  async syncExternalData(codes: string[]): Promise<ApiResponse> {
    return this.callBackend('SyncExternalData', codes)
  }

  // 获取外部股票列表
  async getExternalStockList(limit: number = 100, offset: number = 0): Promise<ApiResponse> {
    return this.callBackend('GetExternalStockList', limit, offset)
  }

  // 获取外部实时数据
  async getExternalRealtimeData(code: string): Promise<ApiResponse> {
    return this.callBackend('GetExternalRealtimeData', code)
  }

  // 获取外部日线数据
  async getExternalDailyData(code: string, startDate?: string, endDate?: string, limit: number = 200): Promise<ApiResponse> {
    return this.callBackend('GetExternalDailyData', code, startDate, endDate, limit)
  }

  // 刷新外部数据缓存
  async refreshExternalCache(): Promise<ApiResponse> {
    return this.callBackend('RefreshExternalCache')
  }

  // 获取外部数据服务状态
  async getExternalServiceStatus(): Promise<ApiResponse> {
    return this.callBackend('GetExternalServiceStatus')
  }

  // 获取市场指数
  async getMarketIndices(): Promise<ApiResponse> {
    return this.callBackend('GetMarketIndices')
  }

  // 导入导出相关方法

  // 导出数据
  async exportData(dataType: string, stockCodes: string, startDate: string, endDate: string, format: string, outputPath: string, includeHeaders: boolean): Promise<ApiResponse> {
    return this.callBackend('ExportData', dataType, stockCodes, startDate, endDate, format, outputPath, includeHeaders)
  }

  // 导入数据
  async importData(filePath: string, dataType: string, overwrite: boolean): Promise<ApiResponse> {
    return this.callBackend('ImportData', filePath, dataType, overwrite)
  }

  // 获取导出模板
  async getExportTemplate(dataType: string, format: string): Promise<ApiResponse> {
    return this.callBackend('GetExportTemplate', dataType, format)
  }

  // 批量导出股票数据
  async batchExportStocks(stockCodes: string, startDate: string, endDate: string, format: string): Promise<ApiResponse> {
    return this.callBackend('BatchExportStocks', stockCodes, startDate, endDate, format)
  }

  // 数据质量监控相关方法

  // 检查数据质量
  async checkDataQuality(): Promise<ApiResponse> {
    return this.callBackend('CheckDataQuality')
  }

  // 获取数据质量指标
  async getDataQualityMetrics(): Promise<ApiResponse> {
    return this.callBackend('GetDataQualityMetrics')
  }

  // 检测异常数据
  async detectAnomalies(stockCode: string, days: number): Promise<ApiResponse> {
    return this.callBackend('DetectAnomalies', stockCode, days)
  }

  // 批量检测异常数据
  async batchDetectAnomalies(stockCodes: string, days: number): Promise<ApiResponse> {
    return this.callBackend('BatchDetectAnomalies', stockCodes, days)
  }

  // 投资组合相关方法

  // 获取投资组合列表
  async getPortfolios(): Promise<ApiResponse> {
    return this.callBackend('GetPortfolios')
  }

  // 获取投资组合详情
  async getPortfolio(portfolioId: string): Promise<ApiResponse> {
    return this.callBackend('GetPortfolio', portfolioId)
  }

  // 创建投资组合
  async createPortfolio(portfolio: any): Promise<ApiResponse> {
    return this.callBackend('CreatePortfolio', portfolio)
  }

  // 获取持仓列表
  async getPositions(portfolioId: string): Promise<ApiResponse> {
    return this.callBackend('GetPositions', portfolioId)
  }

  // 添加持仓
  async addPosition(position: any): Promise<ApiResponse> {
    return this.callBackend('AddPosition', position)
  }

  // 获取交易记录
  async getTransactions(portfolioId: string, limit: number = 50): Promise<ApiResponse> {
    return this.callBackend('GetTransactions', portfolioId, limit)
  }

  // 投资组合分析
  async analyzePortfolio(params: any): Promise<ApiResponse> {
    return this.callBackend('AnalyzePortfolio', params)
  }

  // 新闻相关方法

  // 获取新闻列表
  async getNews(params: {
    category?: string
    source?: string
    keyword?: string
    limit?: number
    offset?: number
  }): Promise<ApiResponse> {
    return this.callBackend('GetNews', params)
  }

  // 获取新闻源列表
  async getNewsSources(): Promise<ApiResponse> {
    return this.callBackend('GetNewsSources')
  }

  // 获取新闻详情
  async getNewsDetail(newsId: string): Promise<ApiResponse> {
    return this.callBackend('GetNewsDetail', newsId)
  }

  // 搜索新闻
  async searchNews(keyword: string, filters?: any): Promise<ApiResponse> {
    return this.callBackend('SearchNews', keyword, filters)
  }

  // 推送通知相关方法

  // 获取推送消息列表
  async getPushMessages(params: {
    type?: string
    limit?: number
    offset?: number
  }): Promise<ApiResponse> {
    return this.callBackend('GetPushMessages', params)
  }

  // 获取推送订阅列表
  async getPushSubscriptions(): Promise<ApiResponse> {
    return this.callBackend('GetPushSubscriptions')
  }

  // 发送推送消息
  async sendPushMessage(message: any): Promise<ApiResponse> {
    return this.callBackend('SendPushMessage', message)
  }

  // 更新推送设置
  async updatePushSettings(settings: any): Promise<ApiResponse> {
    return this.callBackend('UpdatePushSettings', settings)
  }

  // 获取推送分析数据
  async getPushAnalytics(days: number = 7): Promise<ApiResponse> {
    return this.callBackend('GetPushAnalytics', days)
  }

  // 管理推送订阅
  async manageSubscription(action: string, subscriptionId: string, data?: any): Promise<ApiResponse> {
    return this.callBackend('ManageSubscription', action, subscriptionId, data)
  }
}

export const apiService = new ApiService()
export default apiService