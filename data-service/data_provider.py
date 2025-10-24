#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据提供者模块
使用akshare获取股票数据
"""

import akshare as ak
import pandas as pd
import numpy as np
import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import logging
from cachetools import TTLCache
import time

from config import config

logger = logging.getLogger(__name__)

class DataProvider:
    """数据提供者类"""

    def __init__(self):
        self.cache = TTLCache(maxsize=config.CACHE_MAX_SIZE, ttl=config.CACHE_EXPIRE_SECONDS)
        self.session = None
        self.last_update = {}
        self.request_count = 0
        self.error_count = 0

    async def initialize(self):
        """初始化数据提供者"""
        self.session = aiohttp.ClientSession()
        logger.info("数据提供者初始化完成")

    async def cleanup(self):
        """清理资源"""
        if self.session:
            await self.session.close()
        logger.info("数据提供者清理完成")

    def _get_cache_key(self, method: str, **kwargs) -> str:
        """生成缓存键"""
        params = sorted(kwargs.items())
        return f"{method}:{hash(str(params))}"

    async def _cached_request(self, func, cache_key: str, *args, **kwargs):
        """带缓存的请求"""
        # 检查缓存
        if cache_key in self.cache:
            logger.debug(f"命中缓存: {cache_key}")
            return self.cache[cache_key]

        try:
            # 执行请求
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # 存入缓存
            self.cache[cache_key] = result
            self.request_count += 1
            return result

        except Exception as e:
            self.error_count += 1
            logger.error(f"请求失败: {e}")
            raise

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 测试获取股票基本信息
            test_data = await self.get_stock_basic("000001")
            return {
                "status": "healthy",
                "cache_size": len(self.cache),
                "request_count": self.request_count,
                "error_count": self.error_count,
                "last_check": datetime.now().isoformat(),
                "test_data": test_data is not None
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }

    async def get_stock_basic(self, code: str) -> Optional[Dict[str, Any]]:
        """获取股票基本信息"""
        cache_key = self._get_cache_key("stock_basic", code=code)

        async def _fetch():
            try:
                # 使用akshare获取股票基本信息
                stock_info = ak.stock_individual_info_em(symbol=code)
                if stock_info.empty:
                    return None

                # 获取行业信息
                industry_info = ak.stock_board_industry_name_em()
                stock_industry = "未知"

                # 确定市场
                market = "sh" if code.startswith("6") else "sz"

                return {
                    "code": code,
                    "name": stock_info.loc[stock_info['item'] == '股票简称', 'value'].iloc[0] if not stock_info.empty else "未知",
                    "industry": stock_industry,
                    "market": market,
                    "listing_date": stock_info.loc[stock_info['item'] == '上市日期', 'value'].iloc[0] if not stock_info.empty else None,
                    "total_share": stock_info.loc[stock_info['item'] == '总股本', 'value'].iloc[0] if not stock_info.empty else None,
                    "float_share": stock_info.loc[stock_info['item'] == '流通股', 'value'].iloc[0] if not stock_info.empty else None,
                    "update_time": datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"获取股票基本信息失败 {code}: {e}")
                return None

        return await self._cached_request(_fetch, cache_key)

    async def get_stock_list(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """获取股票列表"""
        cache_key = self._get_cache_key("stock_list", limit=limit, offset=offset)

        async def _fetch():
            try:
                # 获取A股列表
                stock_list = ak.stock_zh_a_spot_em()

                # 添加市场信息
                stock_list['market'] = stock_list['代码'].apply(
                    lambda x: 'sh' if x.startswith('6') else 'sz'
                )

                # 选择需要的列并重命名
                columns_mapping = {
                    '代码': 'code',
                    '名称': 'name',
                    '最新价': 'price',
                    '涨跌幅': 'change_percent',
                    '涨跌额': 'change_amount',
                    '成交量': 'volume',
                    '成交额': 'amount',
                    '市场': 'market'
                }

                result_list = []
                for _, row in stock_list.iloc[offset:offset+limit].iterrows():
                    stock_data = {}
                    for zh_col, en_col in columns_mapping.items():
                        if zh_col in row:
                            stock_data[en_col] = row[zh_col]
                    stock_data['update_time'] = datetime.now().isoformat()
                    result_list.append(stock_data)

                return result_list

            except Exception as e:
                logger.error(f"获取股票列表失败: {e}")
                return []

        return await self._cached_request(_fetch, cache_key)

    async def get_daily_data(self, code: str, start_date: str = None, end_date: str = None, limit: int = 200) -> Optional[List[Dict[str, Any]]]:
        """获取股票日线数据"""
        if not start_date:
            start_date = (datetime.now() - timedelta(days=limit*2)).strftime("%Y%m%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")

        cache_key = self._get_cache_key("daily_data", code=code, start_date=start_date, end_date=end_date, limit=limit)

        async def _fetch():
            try:
                # 使用akshare获取历史数据
                stock_zh_a_hist_df = ak.stock_zh_a_hist(
                    symbol=code,
                    period="daily",
                    start_date=start_date,
                    end_date=end_date
                )

                if stock_zh_a_hist_df.empty:
                    return []

                # 重命名列
                columns_mapping = {
                    '日期': 'date',
                    '开盘': 'open',
                    '收盘': 'close',
                    '最高': 'high',
                    '最低': 'low',
                    '成交量': 'volume',
                    '成交额': 'amount'
                }

                result_data = []
                for _, row in stock_zh_a_hist_df.tail(limit).iterrows():
                    daily_data = {'code': code}
                    for zh_col, en_col in columns_mapping.items():
                        if zh_col in row:
                            daily_data[en_col] = float(row[zh_col]) if pd.notna(row[zh_col]) else 0.0
                    result_data.append(daily_data)

                return result_data

            except Exception as e:
                logger.error(f"获取日线数据失败 {code}: {e}")
                return []

        return await self._cached_request(_fetch, cache_key)

    async def get_realtime_data(self, code: str) -> Optional[Dict[str, Any]]:
        """获取股票实时数据"""
        cache_key = self._get_cache_key("realtime_data", code=code)

        async def _fetch():
            try:
                # 使用akshare获取实时数据
                stock_zh_a_spot_df = ak.stock_zh_a_spot_em()
                stock_data = stock_zh_a_spot_df[stock_zh_a_spot_df['代码'] == code]

                if stock_data.empty:
                    return None

                row = stock_data.iloc[0]
                return {
                    "code": code,
                    "name": row['名称'],
                    "price": float(row['最新价']),
                    "open": float(row['今开']),
                    "high": float(row['最高']),
                    "low": float(row['最低']),
                    "pre_close": float(row['昨收']),
                    "change": float(row['涨跌额']),
                    "change_percent": float(row['涨跌幅']),
                    "volume": int(row['成交量']),
                    "amount": float(row['成交额']),
                    "update_time": datetime.now().isoformat()
                }

            except Exception as e:
                logger.error(f"获取实时数据失败 {code}: {e}")
                return None

        return await self._cached_request(_fetch, cache_key)

    async def get_batch_data(self, codes: List[str], fields: List[str]) -> Dict[str, Any]:
        """批量获取股票数据"""
        result = {"success": 0, "failed": 0, "data": {}}

        for code in codes:
            try:
                stock_data = {}

                if "basic" in fields:
                    basic_info = await self.get_stock_basic(code)
                    if basic_info:
                        stock_data["basic"] = basic_info

                if "daily" in fields:
                    daily_data = await self.get_daily_data(code, limit=50)
                    if daily_data:
                        stock_data["daily"] = daily_data

                if "realtime" in fields:
                    realtime_data = await self.get_realtime_data(code)
                    if realtime_data:
                        stock_data["realtime"] = realtime_data

                if stock_data:
                    result["data"][code] = stock_data
                    result["success"] += 1
                else:
                    result["failed"] += 1

                # 添加延迟避免请求过频
                await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f"批量获取数据失败 {code}: {e}")
                result["failed"] += 1

        return result

    async def get_market_indices(self) -> List[Dict[str, Any]]:
        """获取主要指数信息"""
        cache_key = self._get_cache_key("market_indices")

        async def _fetch():
            try:
                # 获取主要指数
                index_data = ak.stock_zh_index_spot_em()

                # 筛选主要指数
                major_indices = ['上证指数', '深证成指', '创业板指', '科创50', '沪深300', '中证500']
                filtered_data = index_data[index_data['代码'].isin(major_indices)]

                result = []
                for _, row in filtered_data.iterrows():
                    result.append({
                        "code": row['代码'],
                        "name": row['名称'],
                        "price": float(row['最新价']),
                        "change": float(row['涨跌额']),
                        "change_percent": float(row['涨跌幅']),
                        "volume": int(row['成交量']),
                        "amount": float(row['成交额']),
                        "update_time": datetime.now().isoformat()
                    })

                return result

            except Exception as e:
                logger.error(f"获取指数信息失败: {e}")
                return []

        return await self._cached_request(_fetch, cache_key)

    async def get_sector_data(self) -> List[Dict[str, Any]]:
        """获取行业板块数据"""
        cache_key = self._get_cache_key("sector_data")

        async def _fetch():
            try:
                # 获取行业板块数据
                sector_data = ak.stock_board_industry_name_em()

                result = []
                for _, row in sector_data.head(50).iterrows():  # 只取前50个行业
                    result.append({
                        "code": row['板块代码'],
                        "name": row['板块名称'],
                        "description": row['板块名称'],
                        "update_time": datetime.now().isoformat()
                    })

                return result

            except Exception as e:
                logger.error(f"获取行业数据失败: {e}")
                return []

        return await self._cached_request(_fetch, cache_key)

    async def refresh_cache(self):
        """刷新缓存"""
        self.cache.clear()
        logger.info("缓存已刷新")

    async def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        return {
            "cache_size": len(self.cache),
            "cache_enabled": config.CACHE_ENABLED,
            "request_count": self.request_count,
            "error_count": self.error_count,
            "supported_markets": config.SUPPORTED_MARKETS,
            "technical_indicators": config.TECHNICAL_INDICATORS,
            "update_time": datetime.now().isoformat()
        }