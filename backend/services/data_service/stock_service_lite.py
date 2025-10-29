"""
股票数据服务 - 轻量化版本
使用akshare获取真实股票数据
"""

import akshare as ak
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import pandas as pd


class StockServiceLite:
    """轻量化股票数据服务"""

    def __init__(self):
        self.cache = {}
        self.cache_timeout = 300  # 5分钟缓存

    async def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """获取股票基本信息"""
        try:
            # 检查缓存
            cache_key = f"stock_info_{symbol}"
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if (datetime.now() - timestamp).seconds < self.cache_timeout:
                    return cached_data

            # 使用akshare获取股票数据
            if len(symbol) == 6 and symbol.isdigit():
                # A股股票
                stock_data = await self._get_a_stock_info(symbol)
            else:
                # 其他格式，尝试转换
                normalized_symbol = self._normalize_symbol(symbol)
                stock_data = await self._get_a_stock_info(normalized_symbol)

            # 格式化数据
            formatted_data = self._format_stock_data(stock_data, symbol)

            # 缓存数据
            self.cache[cache_key] = (formatted_data, datetime.now())

            return formatted_data

        except Exception as e:
            # 网络问题或数据获取失败时，返回404风格错误响应
            print(f"获取股票数据失败 {symbol}: {e}")
            return self._get_error_response(symbol, str(e))

    async def _get_a_stock_info(self, symbol: str) -> Dict[str, Any]:
        """获取A股股票信息"""
        try:
            # 获取实时行情
            stock_zh_a_spot_df = ak.stock_zh_a_spot_em()
            stock_info = stock_zh_a_spot_df[stock_zh_a_spot_df['代码'] == symbol]

            if stock_info.empty:
                raise ValueError(f"未找到股票代码: {symbol}")

            stock_row = stock_info.iloc[0]

            return {
                'symbol': symbol,
                'name': stock_row['名称'],
                'current_price': float(stock_row['最新价']),
                'change': float(stock_row['涨跌额']),
                'change_percent': float(stock_row['涨跌幅']),
                'volume': int(stock_row['成交量']),
                'turnover': float(stock_row['成交额']),
                'high': float(stock_row['最高']),
                'low': float(stock_row['最低']),
                'open': float(stock_row['今开']),
                'yesterday_close': float(stock_row['昨收']),
                'updated_at': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"获取A股数据失败 {symbol}: {e}")
            raise

    def _normalize_symbol(self, symbol: str) -> str:
        """标准化股票代码"""
        if len(symbol) == 6:
            return symbol
        elif len(symbol) < 6:
            # 补零
            return symbol.zfill(6)
        else:
            # 截取后6位
            return symbol[-6:]

    def _format_stock_data(self, stock_data: Dict[str, Any], symbol: str) -> Dict[str, Any]:
        """格式化股票数据"""
        if not stock_data:
            return self._get_error_response(symbol, "数据为空")

        # 计算涨跌幅百分比
        change_percent = 0.0
        if stock_data.get('yesterday_close') and stock_data.get('current_price'):
            change_percent = ((stock_data['current_price'] - stock_data['yesterday_close']) /
                           stock_data['yesterday_close']) * 100

        return {
            'symbol': symbol,
            'name': stock_data.get('name', f'股票{symbol}'),
            'current_price': stock_data.get('current_price', 15.50),
            'change': stock_data.get('change', 0.25),
            'change_percent': round(change_percent, 2),
            'volume': stock_data.get('volume', 1000000),
            'turnover': stock_data.get('turnover', 15500000),
            'high': stock_data.get('high', 15.80),
            'low': stock_data.get('low', 15.20),
            'open': stock_data.get('open', 15.30),
            'yesterday_close': stock_data.get('yesterday_close', 15.25),
            'updated_at': datetime.now().isoformat()
        }

    def _get_error_response(self, symbol: str, error_message: str) -> Dict[str, Any]:
        """获取404风格的错误响应"""
        return {
            'success': False,
            'error': 'DATA_UNAVAILABLE',
            'message': f'暂时无法获取股票 {symbol} 的数据，请稍后再试',
            'details': error_message,
            'suggestion': '可能是网络连接问题或数据源暂时不可用，建议稍后重试',
            'retry_later': True,
            'symbol': symbol,
            'timestamp': datetime.now().isoformat()
        }

    async def get_stock_history(self, symbol: str, period: str = "1m") -> Dict[str, Any]:
        """获取股票历史数据"""
        try:
            # 使用akshare获取历史数据
            if period == "1m":
                # 获取最近1个月数据
                end_date = datetime.now().strftime('%Y%m%d')
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')

                stock_hist = ak.stock_zh_a_hist(symbol=symbol, start_date=start_date, end_date=end_date)

                if stock_hist.empty:
                    return self._get_error_response(symbol, "未找到历史数据")

                # 转换数据格式
                history_data = []
                for _, row in stock_hist.tail(20).iterrows():  # 最近20天
                    history_data.append({
                        'date': row['日期'].strftime('%Y-%m-%d'),
                        'open': float(row['开盘']),
                        'high': float(row['最高']),
                        'low': float(row['最低']),
                        'close': float(row['收盘']),
                        'volume': int(row['成交量'])
                    })

                return {
                    'symbol': symbol,
                    'period': period,
                    'data': history_data,
                    'count': len(history_data)
                }

            else:
                return self._get_error_response(symbol, "不支持的时间周期")

        except Exception as e:
            print(f"获取历史数据失败 {symbol}: {e}")
            return self._get_error_response(symbol, str(e))

    
    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()

    async def search_stocks(self, keyword: str) -> list:
        """搜索股票"""
        try:
            # 简单的股票搜索
            if len(keyword) == 6 and keyword.isdigit():
                # 精确匹配股票代码
                stock_info = await self.get_stock_info(keyword)
                return [{
                    'symbol': stock_info['symbol'],
                    'name': stock_info['name'],
                    'match_type': 'exact'
                }]
            else:
                # 关键词搜索（这里简化处理）
                common_stocks = [
                    {'symbol': '000001', 'name': '平安银行'},
                    {'symbol': '000002', 'name': '万科A'},
                    {'symbol': '600036', 'name': '招商银行'},
                    {'symbol': '600519', 'name': '贵州茅台'},
                    {'symbol': '000858', 'name': '五粮液'}
                ]

                results = []
                for stock in common_stocks:
                    if keyword in stock['symbol'] or keyword in stock['name']:
                        results.append({
                            'symbol': stock['symbol'],
                            'name': stock['name'],
                            'match_type': 'keyword'
                        })

                return results[:10]  # 最多返回10个结果

        except Exception as e:
            print(f"搜索股票失败 {keyword}: {e}")
            return []


# 创建全局实例
stock_service_lite = StockServiceLite()