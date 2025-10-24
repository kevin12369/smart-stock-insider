#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智股通AI分析服务
提供技术分析、基本面分析、消息面分析等AI功能
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from fastapi import HTTPException
from pydantic import BaseModel

from data_provider import DataProvider
from config import config

# 配置日志
logger = logging.getLogger(__name__)

# AI分析相关模型
class TechnicalAnalysisRequest(BaseModel):
    code: str
    period: int = 30
    indicators: List[str] = ["MACD", "RSI", "KDJ", "MA", "BOLL"]
    analysis_type: str = "comprehensive"  # comprehensive, trend, oscillator, volume

class FundamentalAnalysisRequest(BaseModel):
    code: str
    analysis_depth: str = "basic"  # basic, detailed, comprehensive
    include_industry: bool = True
    include_peer: bool = False

class NewsAnalysisRequest(BaseModel):
    code: str
    days: int = 7
    sentiment_analysis: bool = True
    keyword_extraction: bool = True

class PortfolioAnalysisRequest(BaseModel):
    stocks: List[str]
    analysis_type: str = "risk_return"  # risk_return, correlation, optimization
    period: int = 30

class TechnicalAnalysisResult(BaseModel):
    code: str
    current_price: float
    trend_direction: str
    trend_strength: str
    support_level: float
    resistance_level: float
    signals: List[Dict[str, Any]]
    indicators: Dict[str, Any]
    recommendation: str
    confidence: float
    analysis_time: str
    charts: Dict[str, Any]

class FundamentalAnalysisResult(BaseModel):
    code: str
    company_name: str
    industry: str
    market_cap: float
    pe_ratio: float
    pb_ratio: float
    roe: float
    debt_ratio: float
    revenue_growth: float
    profit_growth: float
    valuation_level: str
    financial_health: str
    recommendation: str
    confidence: float
    analysis_time: str

class NewsAnalysisResult(BaseModel):
    code: str
    company_name: str
    news_count: int
    sentiment_score: float
    sentiment_trend: str
    key_topics: List[str]
    risk_events: List[str]
    recommendation: str
    confidence: float
    analysis_time: str

class PortfolioAnalysisResult(BaseModel):
    portfolio_id: str
    total_value: float
    stock_analysis: Dict[str, Any]
    risk_metrics: Dict[str, Any]
    return_metrics: Dict[str, Any]
    correlation_matrix: List[List[float]]
    optimization_suggestions: List[Dict[str, Any]]
    recommendation: str
    confidence: float
    analysis_time: str

class AIService:
    """AI分析服务"""

    def __init__(self, data_provider: DataProvider):
        self.data_provider = data_provider

    async def technical_analysis(self, request: TechnicalAnalysisRequest) -> TechnicalAnalysisResult:
        """技术分析"""
        try:
            logger.info(f"开始技术分析: {request.code}")

            # 获取历史数据
            daily_data = await self.data_provider.get_daily_data(
                request.code,
                None, None,
                request.period + 50  # 多获取一些数据用于计算指标
            )

            if not daily_data:
                raise HTTPException(status_code=404, detail="未找到股票数据")

            # 转换为DataFrame
            df = pd.DataFrame(daily_data)
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            df = df.sort_index()

            # 获取实时价格
            realtime_data = await self.data_provider.get_realtime_data(request.code)
            current_price = realtime_data['price'] if realtime_data else df.iloc[-1]['close']

            # 计算技术指标
            indicators = self._calculate_indicators(df, request.indicators)

            # 趋势分析
            trend_direction, trend_strength = self._analyze_trend(df)

            # 支撑位和阻力位
            support_level, resistance_level = self._calculate_support_resistance(df)

            # 生成信号
            signals = self._generate_signals(df, indicators)

            # 生成推荐
            recommendation, confidence = self._generate_recommendation(
                trend_direction, trend_strength, signals, indicators
            )

            result = TechnicalAnalysisResult(
                code=request.code,
                current_price=current_price,
                trend_direction=trend_direction,
                trend_strength=trend_strength,
                support_level=support_level,
                resistance_level=resistance_level,
                signals=signals,
                indicators=indicators,
                recommendation=recommendation,
                confidence=confidence,
                analysis_time=datetime.now().isoformat(),
                charts=self._generate_chart_data(df, indicators)
            )

            logger.info(f"技术分析完成: {request.code}, 推荐: {recommendation}")
            return result

        except Exception as e:
            logger.error(f"技术分析失败 {request.code}: {e}")
            raise HTTPException(status_code=500, detail=f"技术分析失败: {str(e)}")

    async def fundamental_analysis(self, request: FundamentalAnalysisRequest) -> FundamentalAnalysisResult:
        """基本面分析"""
        try:
            logger.info(f"开始基本面分析: {request.code}")

            # 获取基本信息
            basic_info = await self.data_provider.get_stock_basic(request.code)
            if not basic_info:
                raise HTTPException(status_code=404, detail="未找到股票基本信息")

            # 模拟财务数据（实际应用中需要接入真实财务数据API）
            financial_data = self._simulate_financial_data(request.code)

            # 计算估值指标
            valuation_level = self._calculate_valuation_level(financial_data)

            # 评估财务健康度
            financial_health = self._assess_financial_health(financial_data)

            # 生成推荐
            recommendation, confidence = self._generate_fundamental_recommendation(
                financial_data, valuation_level, financial_health
            )

            result = FundamentalAnalysisResult(
                code=request.code,
                company_name=basic_info['name'],
                industry=basic_info.get('industry', '未知'),
                market_cap=financial_data.get('market_cap', 0),
                pe_ratio=financial_data.get('pe_ratio', 0),
                pb_ratio=financial_data.get('pb_ratio', 0),
                roe=financial_data.get('roe', 0),
                debt_ratio=financial_data.get('debt_ratio', 0),
                revenue_growth=financial_data.get('revenue_growth', 0),
                profit_growth=financial_data.get('profit_growth', 0),
                valuation_level=valuation_level,
                financial_health=financial_health,
                recommendation=recommendation,
                confidence=confidence,
                analysis_time=datetime.now().isoformat()
            )

            logger.info(f"基本面分析完成: {request.code}, 推荐: {recommendation}")
            return result

        except Exception as e:
            logger.error(f"基本面分析失败 {request.code}: {e}")
            raise HTTPException(status_code=500, detail=f"基本面分析失败: {str(e)}")

    async def news_analysis(self, request: NewsAnalysisRequest) -> NewsAnalysisResult:
        """消息面分析"""
        try:
            logger.info(f"开始消息面分析: {request.code}")

            # 获取基本信息
            basic_info = await self.data_provider.get_stock_basic(request.code)
            if not basic_info:
                raise HTTPException(status_code=404, detail="未找到股票基本信息")

            # 模拟新闻数据（实际应用中需要接入真实新闻API）
            news_data = self._simulate_news_data(request.code, request.days)

            # 情感分析
            sentiment_score = self._calculate_sentiment_score(news_data)

            # 情感趋势
            sentiment_trend = self._analyze_sentiment_trend(news_data)

            # 关键词提取
            key_topics = self._extract_keywords(news_data) if request.keyword_extraction else []

            # 风险事件识别
            risk_events = self._identify_risk_events(news_data)

            # 生成推荐
            recommendation, confidence = self._generate_news_recommendation(
                sentiment_score, sentiment_trend, risk_events
            )

            result = NewsAnalysisResult(
                code=request.code,
                company_name=basic_info['name'],
                news_count=len(news_data),
                sentiment_score=sentiment_score,
                sentiment_trend=sentiment_trend,
                key_topics=key_topics,
                risk_events=risk_events,
                recommendation=recommendation,
                confidence=confidence,
                analysis_time=datetime.now().isoformat()
            )

            logger.info(f"消息面分析完成: {request.code}, 推荐: {recommendation}")
            return result

        except Exception as e:
            logger.error(f"消息面分析失败 {request.code}: {e}")
            raise HTTPException(status_code=500, detail=f"消息面分析失败: {str(e)}")

    async def portfolio_analysis(self, request: PortfolioAnalysisRequest) -> PortfolioAnalysisResult:
        """组合分析"""
        try:
            logger.info(f"开始组合分析: {len(request.stocks)}只股票")

            # 获取所有股票的基本信息和价格数据
            stock_data = {}
            for code in request.stocks:
                basic_info = await self.data_provider.get_stock_basic(code)
                realtime_data = await self.data_provider.get_realtime_data(code)
                if basic_info and realtime_data:
                    stock_data[code] = {
                        'name': basic_info['name'],
                        'price': realtime_data['price'],
                        'industry': basic_info.get('industry', '未知')
                    }

            if len(stock_data) == 0:
                raise HTTPException(status_code=404, detail="未找到有效的股票数据")

            # 模拟历史价格数据用于计算风险收益
            price_data = self._simulate_portfolio_price_data(request.stocks, request.period)

            # 计算风险指标
            risk_metrics = self._calculate_portfolio_risk(price_data)

            # 计算收益指标
            return_metrics = self._calculate_portfolio_return(price_data)

            # 计算相关系数矩阵
            correlation_matrix = self._calculate_correlation_matrix(price_data)

            # 生成优化建议
            optimization_suggestions = self._generate_optimization_suggestions(
                stock_data, risk_metrics, return_metrics, correlation_matrix
            )

            # 生成推荐
            recommendation, confidence = self._generate_portfolio_recommendation(
                risk_metrics, return_metrics, correlation_matrix
            )

            result = PortfolioAnalysisResult(
                portfolio_id=f"portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                total_value=sum(stock['price'] for stock in stock_data.values()),
                stock_analysis=stock_data,
                risk_metrics=risk_metrics,
                return_metrics=return_metrics,
                correlation_matrix=correlation_matrix,
                optimization_suggestions=optimization_suggestions,
                recommendation=recommendation,
                confidence=confidence,
                analysis_time=datetime.now().isoformat()
            )

            logger.info(f"组合分析完成: {len(stock_data)}只股票, 推荐: {recommendation}")
            return result

        except Exception as e:
            logger.error(f"组合分析失败: {e}")
            raise HTTPException(status_code=500, detail=f"组合分析失败: {str(e)}")

    def _calculate_indicators(self, df: pd.DataFrame, indicator_list: List[str]) -> Dict[str, Any]:
        """计算技术指标"""
        indicators = {}

        for indicator in indicator_list:
            if indicator == "MACD":
                indicators["MACD"] = self._calculate_macd(df)
            elif indicator == "RSI":
                indicators["RSI"] = self._calculate_rsi(df)
            elif indicator == "KDJ":
                indicators["KDJ"] = self._calculate_kdj(df)
            elif indicator == "MA":
                indicators["MA"] = self._calculate_ma(df)
            elif indicator == "BOLL":
                indicators["BOLL"] = self._calculate_boll(df)
            elif indicator == "CCI":
                indicators["CCI"] = self._calculate_cci(df)
            elif indicator == "WR":
                indicators["WR"] = self._calculate_wr(df)
            elif indicator == "DMI":
                indicators["DMI"] = self._calculate_dmi(df)
            elif indicator == "MTM":
                indicators["MTM"] = self._calculate_mtm(df)
            elif indicator == "TRIX":
                indicators["TRIX"] = self._calculate_trix(df)
            elif indicator == "DMA":
                indicators["DMA"] = self._calculate_dma(df)
            elif indicator == "EXPMA":
                indicators["EXPMA"] = self._calculate_expma(df)
            elif indicator == "BBI":
                indicators["BBI"] = self._calculate_bbi(df)
            elif indicator == "ARBR":
                indicators["ARBR"] = self._calculate_arbr(df)
            elif indicator == "VR":
                indicators["VR"] = self._calculate_vr(df)
            elif indicator == "OBV":
                indicators["OBV"] = self._calculate_obv(df)
            elif indicator == "EMV":
                indicators["EMV"] = self._calculate_emv(df)
            elif indicator == "SAR":
                indicators["SAR"] = self._calculate_sar(df)
            elif indicator == "ROC":
                indicators["ROC"] = self._calculate_roc(df)
            elif indicator == "BOLL_Width":
                indicators["BOLL_Width"] = self._calculate_boll_width(df)
            elif indicator == "MACD_Histogram":
                indicators["MACD_Histogram"] = self._calculate_macd_histogram(df)

        return indicators

    def _calculate_macd(self, df: pd.DataFrame, fast=12, slow=26, signal=9) -> Dict[str, float]:
        """计算MACD指标"""
        exp1 = df['close'].ewm(span=fast).mean()
        exp2 = df['close'].ewm(span=slow).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal).mean()
        histogram = macd - signal_line

        return {
            'macd': macd.iloc[-1],
            'signal': signal_line.iloc[-1],
            'histogram': histogram.iloc[-1],
            'macd_trend': 'up' if macd.iloc[-1] > macd.iloc[-2] else 'down'
        }

    def _calculate_rsi(self, df: pd.DataFrame, period=14) -> Dict[str, float]:
        """计算RSI指标"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return {
            'rsi': rsi.iloc[-1],
            'rsi_trend': 'up' if rsi.iloc[-1] > rsi.iloc[-2] else 'down',
            'overbought': rsi.iloc[-1] > 70,
            'oversold': rsi.iloc[-1] < 30
        }

    def _calculate_kdj(self, df: pd.DataFrame, n=9, m1=3, m2=3) -> Dict[str, float]:
        """计算KDJ指标"""
        low_min = df['low'].rolling(window=n).min()
        high_max = df['high'].rolling(window=n).max()
        rsv = (df['close'] - low_min) / (high_max - low_min) * 100
        k = rsv.ewm(span=m1).mean()
        d = k.ewm(span=m2).mean()
        j = 3 * k - 2 * d

        return {
            'k': k.iloc[-1],
            'd': d.iloc[-1],
            'j': j.iloc[-1],
            'kdj_signal': self._get_kdj_signal(k.iloc[-1], d.iloc[-1], j.iloc[-1])
        }

    def _calculate_ma(self, df: pd.DataFrame) -> Dict[str, float]:
        """计算移动平均线"""
        ma5 = df['close'].rolling(window=5).mean()
        ma10 = df['close'].rolling(window=10).mean()
        ma20 = df['close'].rolling(window=20).mean()
        ma60 = df['close'].rolling(window=60).mean()

        current_price = df['close'].iloc[-1]

        return {
            'ma5': ma5.iloc[-1],
            'ma10': ma10.iloc[-1],
            'ma20': ma20.iloc[-1],
            'ma60': ma60.iloc[-1],
            'price_vs_ma5': (current_price - ma5.iloc[-1]) / ma5.iloc[-1] * 100,
            'price_vs_ma20': (current_price - ma20.iloc[-1]) / ma20.iloc[-1] * 100,
            'ma_trend': self._get_ma_trend(ma5, ma10, ma20, ma60)
        }

    def _calculate_boll(self, df: pd.DataFrame, period=20, std_dev=2) -> Dict[str, float]:
        """计算布林带"""
        ma = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        upper_band = ma + std * std_dev
        lower_band = ma - std * std_dev

        current_price = df['close'].iloc[-1]

        return {
            'upper': upper_band.iloc[-1],
            'middle': ma.iloc[-1],
            'lower': lower_band.iloc[-1],
            'bandwidth': (upper_band.iloc[-1] - lower_band.iloc[-1]) / ma.iloc[-1],
            'price_position': (current_price - lower_band.iloc[-1]) / (upper_band.iloc[-1] - lower_band.iloc[-1]) * 100,
            'boll_signal': self._get_boll_signal(current_price, upper_band.iloc[-1], lower_band.iloc[-1])
        }

    def _calculate_cci(self, df: pd.DataFrame, period=14) -> Dict[str, float]:
        """计算CCI指标"""
        tp = (df['high'] + df['low'] + df['close']) / 3
        ma_tp = tp.rolling(window=period).mean()
        md = abs(tp - ma_tp).rolling(window=period).mean()
        cci = (tp - ma_tp) / (0.015 * md)

        return {
            'cci': cci.iloc[-1],
            'cci_trend': 'up' if cci.iloc[-1] > cci.iloc[-2] else 'down',
            'overbought': cci.iloc[-1] > 100,
            'oversold': cci.iloc[-1] < -100
        }

    def _calculate_wr(self, df: pd.DataFrame, period=14) -> Dict[str, float]:
        """计算威廉指标"""
        high_max = df['high'].rolling(window=period).max()
        low_min = df['low'].rolling(window=period).min()
        wr = (high_max - df['close']) / (high_max - low_min) * -100

        return {
            'wr': wr.iloc[-1],
            'wr_trend': 'up' if wr.iloc[-1] > wr.iloc[-2] else 'down',
            'overbought': wr.iloc[-1] < -20,
            'oversold': wr.iloc[-1] > -80
        }

    def _analyze_trend(self, df: pd.DataFrame) -> tuple[str, str]:
        """分析趋势"""
        if len(df) < 20:
            return "unknown", "weak"

        # 使用20日移动平均线判断趋势
        ma20 = df['close'].rolling(window=20).mean()
        current_price = df['close'].iloc[-1]

        if current_price > ma20.iloc[-1]:
            if ma20.iloc[-1] > ma20.iloc[-2]:
                return "upward", "strong"
            else:
                return "upward", "weak"
        else:
            if ma20.iloc[-1] < ma20.iloc[-2]:
                return "downward", "strong"
            else:
                return "downward", "weak"

    def _calculate_support_resistance(self, df: pd.DataFrame) -> tuple[float, float]:
        """计算支撑位和阻力位"""
        if len(df) < 20:
            return 0, 0

        # 使用近20日高低点
        recent_high = df['high'].tail(20).max()
        recent_low = df['low'].tail(20).min()

        # 计算动态支撑阻力位
        current_price = df['close'].iloc[-1]

        resistance_level = recent_high + (recent_high - recent_low) * 0.1
        support_level = recent_low - (recent_high - recent_low) * 0.1

        return support_level, resistance_level

    def _generate_signals(self, df: pd.DataFrame, indicators: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成交易信号"""
        signals = []

        # MACD信号
        if "MACD" in indicators:
            macd_data = indicators["MACD"]
            if macd_data["macd_trend"] == "up" and macd_data["histogram"] > 0:
                signals.append({
                    "type": "MACD金叉",
                    "signal": "买入",
                    "strength": "medium",
                    "description": "MACD金叉形成，趋势向上"
                })
            elif macd_data["macd_trend"] == "down" and macd_data["histogram"] < 0:
                signals.append({
                    "type": "MACD死叉",
                    "signal": "卖出",
                    "strength": "medium",
                    "description": "MACD死叉形成，趋势向下"
                })

        # RSI信号
        if "RSI" in indicators:
            rsi_data = indicators["RSI"]
            if rsi_data["oversold"]:
                signals.append({
                    "type": "RSI超卖",
                    "signal": "买入",
                    "strength": "strong",
                    "description": "RSI超卖，可能出现反弹"
                })
            elif rsi_data["overbought"]:
                signals.append({
                    "type": "RSI超买",
                    "signal": "卖出",
                    "strength": "strong",
                    "description": "RSI超买，可能出现调整"
                })

        # KDJ信号
        if "KDJ" in indicators:
            kdj_data = indicators["KDJ"]
            if kdj_data["kdj_signal"] == "金叉":
                signals.append({
                    "type": "KDJ金叉",
                    "signal": "买入",
                    "strength": "medium",
                    "description": "KDJ金叉，短线看涨"
                })
            elif kdj_data["kdj_signal"] == "死叉":
                signals.append({
                    "type": "KDJ死叉",
                    "signal": "卖出",
                    "strength": "medium",
                    "description": "KDJ死叉，短线看跌"
                })

        # 布林带信号
        if "BOLL" in indicators:
            boll_data = indicators["BOLL"]
            if boll_data["boll_signal"] == "突破上轨":
                signals.append({
                    "type": "布林带突破",
                    "signal": "买入",
                    "strength": "strong",
                    "description": "价格突破布林带上轨，强势上涨"
                })
            elif boll_data["boll_signal"] == "跌破下轨":
                signals.append({
                    "type": "布林带跌破",
                    "signal": "卖出",
                    "strength": "strong",
                    "description": "价格跌破布林带下轨，弱势下跌"
                })

        return signals

    def _generate_recommendation(self, trend_direction: str, trend_strength: str,
                               signals: List[Dict[str, Any]], indicators: Dict[str, Any]) -> tuple[str, float]:
        """生成推荐"""
        buy_signals = [s for s in signals if s["signal"] == "买入"]
        sell_signals = [s for s in signals if s["signal"] == "卖出"]

        buy_score = sum(3 if s["strength"] == "strong" else 2 if s["strength"] == "medium" else 1
                     for s in buy_signals)
        sell_score = sum(3 if s["strength"] == "strong" else 2 if s["strength"] == "medium" else 1
                      for s in sell_signals)

        net_score = buy_score - sell_score

        # 趋势权重
        trend_weight = 3 if trend_strength == "strong" else 2 if trend_strength == "medium" else 1
        if trend_direction == "upward":
            net_score += trend_weight
        elif trend_direction == "downward":
            net_score -= trend_weight

        if net_score >= 8:
            return "强烈买入", 0.85
        elif net_score >= 4:
            return "买入", 0.75
        elif net_score >= 0:
            return "持有", 0.65
        elif net_score >= -4:
            return "卖出", 0.65
        else:
            return "强烈卖出", 0.75

    def _get_kdj_signal(self, k: float, d: float, j: float) -> str:
        """获取KDJ信号"""
        if k > d and k > 20:
            return "金叉"
        elif k < d and k < 80:
            return "死叉"
        return "中性"

    def _get_ma_trend(self, ma5: pd.Series, ma10: pd.Series, ma20: pd.Series, ma60: pd.Series) -> str:
        """获取均线趋势"""
        current = [ma5.iloc[-1], ma10.iloc[-1], ma20.iloc[-1], ma60.iloc[-1]]
        previous = [ma5.iloc[-2], ma10.iloc[-2], ma20.iloc[-2], ma60.iloc[-2]]

        if all(c >= p for c, p in zip(current, previous)):
            return "多头排列"
        elif all(c <= p for c, p in zip(current, previous)):
            return "空头排列"
        else:
            return "震荡"

    def _get_boll_signal(self, price: float, upper: float, lower: float) -> str:
        """获取布林带信号"""
        if price > upper:
            return "突破上轨"
        elif price < lower:
            return "跌破下轨"
        else:
            return "区间震荡"

    def _generate_chart_data(self, df: pd.DataFrame, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """生成图表数据"""
        return {
            "price_data": [
                {
                    "date": date.strftime('%Y-%m-%d'),
                    "close": row['close'],
                    "high": row['high'],
                    "low": row['low'],
                    "open": row['open'],
                    "volume": row['volume']
                }
                for date, row in df.tail(60).iterrows()  # 最近60天
            ],
            "indicators": {
                "ma": indicators.get("MA", {}),
                "boll": indicators.get("BOLL", {}),
                "macd": indicators.get("MACD", {})
            }
        }

    def _simulate_financial_data(self, code: str) -> Dict[str, Any]:
        """模拟财务数据"""
        # 这里使用模拟数据，实际应用中需要接入真实财务数据API
        base_values = {
            "000001": {"market_cap": 2000000000000, "pe_ratio": 15.5, "pb_ratio": 1.2, "roe": 0.12, "debt_ratio": 0.6},
            "600000": {"market_cap": 3000000000000, "pe_ratio": 12.3, "pb_ratio": 0.9, "roe": 0.15, "debt_ratio": 0.5},
            "000002": {"market_cap": 1500000000000, "pe_ratio": 18.7, "pb_ratio": 1.5, "roe": 0.10, "debt_ratio": 0.7},
        }

        base = base_values.get(code, {
            "market_cap": 1000000000000,
            "pe_ratio": 16.0,
            "pb_ratio": 1.3,
            "roe": 0.13,
            "debt_ratio": 0.6
        })

        # 添加随机波动
        return {
            **base,
            "revenue_growth": base["roe"] * 100 + np.random.normal(0, 5),
            "profit_growth": base["roe"] * 80 + np.random.normal(0, 8)
        }

    def _calculate_valuation_level(self, financial_data: Dict[str, Any]) -> str:
        """计算估值水平"""
        pe_ratio = financial_data.get("pe_ratio", 16)
        pb_ratio = financial_data.get("pb_ratio", 1.3)

        if pe_ratio < 10 and pb_ratio < 0.8:
            return "低估"
        elif pe_ratio < 15 and pb_ratio < 1.2:
            return "合理"
        elif pe_ratio < 25 and pb_ratio < 2.0:
            return "偏高"
        else:
            return "高估"

    def _assess_financial_health(self, financial_data: Dict[str, Any]) -> str:
        """评估财务健康度"""
        roe = financial_data.get("roe", 0.1)
        debt_ratio = financial_data.get("debt_ratio", 0.6)

        if roe > 0.15 and debt_ratio < 0.4:
            return "优秀"
        elif roe > 0.10 and debt_ratio < 0.6:
            return "良好"
        elif roe > 0.05 and debt_ratio < 0.8:
            return "一般"
        else:
            return "较差"

    def _generate_fundamental_recommendation(self, financial_data: Dict[str, Any],
                                           valuation_level: str, financial_health: str) -> tuple[str, float]:
        """生成基本面推荐"""
        health_scores = {"优秀": 5, "良好": 4, "一般": 3, "较差": 2}
        valuation_scores = {"低估": 5, "合理": 4, "偏高": 3, "高估": 2}

        health_score = health_scores.get(financial_health, 3)
        valuation_score = valuation_scores.get(valuation_level, 3)

        total_score = (health_score + valuation_score) / 2

        if total_score >= 4.5:
            return "强烈买入", 0.8
        elif total_score >= 3.5:
            return "买入", 0.75
        elif total_score >= 2.5:
            return "持有", 0.65
        elif total_score >= 2.0:
            return "卖出", 0.6
        else:
            return "强烈卖出", 0.7

    def _simulate_news_data(self, code: str, days: int) -> List[Dict[str, Any]]:
        """模拟新闻数据"""
        # 这里使用模拟数据，实际应用中需要接入真实新闻API
        import random

        news_types = ["利好", "中性", "利空"]
        sentiments = {
            "利好": {"score": 0.8, "impact": "positive"},
            "中性": {"score": 0.0, "impact": "neutral"},
            "利空": {"score": -0.6, "impact": "negative"}
        }

        news_data = []
        for i in range(days):
            news_type = random.choice(news_types)
            sentiment = sentiments[news_type]
            news_data.append({
                "title": f"股票{code}相关新闻{i+1}",
                "content": f"关于{code}的{news_type}消息",
                "sentiment_score": sentiment["score"] + random.uniform(-0.1, 0.1),
                "impact": sentiment["impact"],
                "date": (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            })

        return news_data

    def _calculate_sentiment_score(self, news_data: List[Dict[str, Any]]) -> float:
        """计算情感得分"""
        if not news_data:
            return 0.0

        scores = [news["sentiment_score"] for news in news_data]
        return sum(scores) / len(scores)

    def _analyze_sentiment_trend(self, news_data: List[Dict[str, Any]]) -> str:
        """分析情感趋势"""
        if len(news_data) < 3:
            return "数据不足"

        # 按日期排序
        sorted_news = sorted(news_data, key=lambda x: x["date"])

        # 计算最近3天的平均情感得分
        recent_scores = [news["sentiment_score"] for news in sorted_news[-3:]]
        early_scores = [news["sentiment_score"] for news in sorted_news[:3]]

        recent_avg = sum(recent_scores) / len(recent_scores)
        early_avg = sum(early_scores) / len(early_scores)

        if recent_avg > early_avg + 0.1:
            return "改善"
        elif recent_avg < early_avg - 0.1:
            return "恶化"
        else:
            return "稳定"

    def _extract_keywords(self, news_data: List[Dict[str, Any]]) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取
        keywords = ["业绩", "财报", "收购", "重组", "新产品", "政策", "市场", "行业", "监管"]

        # 统计关键词出现频率
        keyword_counts = {}
        for news in news_data:
            content = news["title"] + " " + news["content"]
            for keyword in keywords:
                if keyword in content:
                    keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1

        # 返回出现频率最高的关键词
        sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
        return [keyword for keyword, count in sorted_keywords[:5]]

    def _identify_risk_events(self, news_data: List[Dict[str, Any]]) -> List[str]:
        """识别风险事件"""
        risk_keywords = ["调查", "处罚", "诉讼", "违规", "亏损", "风险", "警告"]
        risk_events = []

        for news in news_data:
            content = news["title"] + " " + news["content"]
            for keyword in risk_keywords:
                if keyword in content:
                    risk_events.append(f"{news['date']}: {keyword}相关")
                    break

        return risk_events

    def _generate_news_recommendation(self, sentiment_score: float, sentiment_trend: str,
                                     risk_events: List[str]) -> tuple[str, float]:
        """生成消息面推荐"""
        base_score = sentiment_score

        # 调整情感趋势权重
        if sentiment_trend == "改善":
            base_score += 0.2
        elif sentiment_trend == "恶化":
            base_score -= 0.2

        # 调整风险事件权重
        if len(risk_events) > 0:
            base_score -= len(risk_events) * 0.1

        confidence = 0.6 if len(risk_events) > 2 else 0.8

        if base_score > 0.3:
            return "积极", confidence
        elif base_score > -0.3:
            return "中性", confidence
        else:
            return "消极", confidence

    def _simulate_portfolio_price_data(self, stocks: List[str], period: int) -> Dict[str, pd.DataFrame]:
        """模拟组合价格数据"""
        price_data = {}

        for code in stocks:
            dates = pd.date_range(end=datetime.now(), periods=period, freq='D')
            prices = []

            # 模拟价格走势
            base_price = 10 + hash(code) % 20
            for i in range(period):
                change = np.random.normal(0, 0.02)
                base_price *= (1 + change)
                prices.append(base_price)

            price_data[code] = pd.DataFrame({
                'date': dates,
                'price': prices
            })

        return price_data

    def _calculate_portfolio_risk(self, price_data: Dict[str, pd.DataFrame]) -> Dict[str, float]:
        """计算组合风险指标"""
        if not price_data:
            return {"volatility": 0, "max_drawdown": 0, "beta": 0}

        # 计算收益率
        returns_data = {}
        for code, df in price_data.items():
            returns = df['price'].pct_change().dropna()
            if len(returns) > 0:
                returns_data[code] = returns

        if not returns_data:
            return {"volatility": 0, "max_drawdown": 0, "beta": 0}

        # 计算组合平均收益率
        portfolio_returns = pd.DataFrame(returns_data).mean(axis=1)

        # 计算波动率
        volatility = portfolio_returns.std() * np.sqrt(252)  # 年化波动率

        # 计算最大回撤
        cumulative_returns = (1 + portfolio_returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()

        # 简化的Beta计算（相对于市场基准）
        beta = 1.0 + np.random.normal(0, 0.2)

        return {
            "volatility": volatility,
            "max_drawdown": max_drawdown,
            "beta": beta
        }

    def _calculate_portfolio_return(self, price_data: Dict[str, pd.DataFrame]) -> Dict[str, float]:
        """计算组合收益指标"""
        if not price_data:
            return {"total_return": 0, "annual_return": 0, "sharpe_ratio": 0}

        total_returns = 0
        total_periods = 0

        for df in price_data.values():
            returns = df['price'].pct_change().dropna()
            if len(returns) > 0:
                total_returns += returns.sum()
                total_periods += len(returns)

        if total_periods == 0:
            return {"total_return": 0, "annual_return": 0, "sharpe_ratio": 0}

        avg_return = total_returns / len(price_data)
        annual_return = avg_return * 252

        # 简化的夏普比率计算
        sharpe_ratio = annual_return / 0.15 if annual_return != 0 else 0

        return {
            "total_return": total_returns,
            "annual_return": annual_return,
            "sharpe_ratio": sharpe_ratio
        }

    def _calculate_correlation_matrix(self, price_data: Dict[str, pd.DataFrame]) -> List[List[float]]:
        """计算相关系数矩阵"""
        if len(price_data) < 2:
            return [[1.0]]

        returns_data = {}
        for code, df in price_data.items():
            returns = df['price'].pct_change().dropna()
            if len(returns) > 0:
                returns_data[code] = returns

        if len(returns_data) < 2:
            return [[1.0]]

        returns_df = pd.DataFrame(returns_data)
        correlation_matrix = returns_df.corr()

        return correlation_matrix.values.tolist()

    def _generate_optimization_suggestions(self, stock_data: Dict[str, Any],
                                          risk_metrics: Dict[str, float],
                                          return_metrics: Dict[str, float],
                                          correlation_matrix: List[List[float]]) -> List[Dict[str, Any]]:
        """生成优化建议"""
        suggestions = []

        # 风险建议
        if risk_metrics.get("volatility", 0) > 0.25:
            suggestions.append({
                "type": "风险控制",
                "description": "组合波动率较高，建议降低仓位或配置防御性资产",
                "priority": "high"
            })

        if risk_metrics.get("max_drawdown", 0) < -0.2:
            suggestions.append({
                "type": "风险控制",
                "description": "最大回撤过大，建议设置止损位",
                "priority": "high"
            })

        # 分散化建议
        if len(stock_data) < 5:
            suggestions.append({
                "type": "分散化",
                "description": "股票数量较少，建议增加投资标的以分散风险",
                "priority": "medium"
            })

        # 收益建议
        if return_metrics.get("sharpe_ratio", 0) < 1:
            suggestions.append({
                "type": "收益优化",
                "description": "夏普比率较低，建议优化投资组合配置",
                "priority": "medium"
            })

        return suggestions

    def _generate_portfolio_recommendation(self, risk_metrics: Dict[str, float],
                                           return_metrics: Dict[str, float],
                                           correlation_matrix: List[List[float]]) -> tuple[str, float]:
        """生成组合推荐"""
        sharpe_ratio = return_metrics.get("sharpe_ratio", 0)
        max_drawdown = risk_metrics.get("max_drawdown", 0)

        score = sharpe_score = sharpe_ratio * 100
        if max_drawdown < -0.15:
            score -= 20
        if max_drawdown < -0.25:
            score -= 40

        if score > 80:
            return "优秀", 0.85
        elif score > 60:
            return "良好", 0.75
        elif score > 40:
            return "一般", 0.65
        elif score > 20:
            return "较差", 0.55
        else:
            return "很差", 0.45

    # 新增技术指标实现方法

    def _calculate_dmi(self, df: pd.DataFrame, period=14) -> Dict[str, float]:
        """计算DMI指标（动向指标）"""
        high = df['high']
        low = df['low']
        close = df['close']

        # 计算真实波幅
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # 计算上升动向和下降动向
        dm_plus = np.where((high - low.shift(1)) > 0,
                          high - low.shift(1) - abs((close.shift(1) - low.shift(1))), 0)
        dm_minus = np.where((low.shift(1) - high) > 0,
                           low.shift(1) - high - abs((high.shift(1) - close.shift(1))), 0)

        # 平滑处理
        tr_smooth = tr.rolling(window=period).mean()
        dm_plus_smooth = pd.Series(dm_plus).rolling(window=period).mean()
        dm_minus_smooth = pd.Series(dm_minus).rolling(window=period).mean()

        # 计算DI
        di_plus = 100 * dm_plus_smooth / tr_smooth
        di_minus = 100 * dm_minus_smooth / tr_smooth

        # 计算DX和ADX
        dx = 100 * abs(di_plus - di_minus) / (di_plus + di_minus)
        adx = dx.rolling(window=period).mean()

        return {
            'di_plus': di_plus.iloc[-1],
            'di_minus': di_minus.iloc[-1],
            'adx': adx.iloc[-1],
            'dmi_signal': self._get_dmi_signal(di_plus.iloc[-1], di_minus.iloc[-1])
        }

    def _calculate_mtm(self, df: pd.DataFrame, period=12) -> Dict[str, float]:
        """计算MTM指标（动量指标）"""
        close = df['close']
        mtm = close - close.shift(period)
        mtm_ma = mtm.rolling(window=period).mean()

        return {
            'mtm': mtm.iloc[-1],
            'mtm_ma': mtm_ma.iloc[-1],
            'mtm_trend': 'up' if mtm.iloc[-1] > 0 else 'down'
        }

    def _calculate_trix(self, df: pd.DataFrame, period=12) -> Dict[str, float]:
        """计算TRIX指标（三重指数平滑平均线）"""
        close = df['close']

        # 计算三重指数平滑
        ema1 = close.ewm(span=period).mean()
        ema2 = ema1.ewm(span=period).mean()
        ema3 = ema2.ewm(span=period).mean()

        # 计算TRIX
        trix = (ema3 - ema3.shift(1)) / ema3.shift(1) * 10000
        trix_ma = trix.rolling(window=9).mean()

        return {
            'trix': trix.iloc[-1],
            'trix_ma': trix_ma.iloc[-1],
            'trix_signal': self._get_trix_signal(trix.iloc[-1], trix_ma.iloc[-1])
        }

    def _calculate_dma(self, df: pd.DataFrame, short=10, long=50) -> Dict[str, float]:
        """计算DMA指标（平行线差）"""
        close = df['close']
        dma_short = close.rolling(window=short).mean()
        dma_long = close.rolling(window=long).mean()
        dma = dma_short - dma_long

        return {
            'dma': dma.iloc[-1],
            'dma_short': dma_short.iloc[-1],
            'dma_long': dma_long.iloc[-1],
            'dma_signal': 'buy' if dma.iloc[-1] > 0 else 'sell'
        }

    def _calculate_expma(self, df: pd.DataFrame, period=20) -> Dict[str, float]:
        """计算EXPMA指标（指数移动平均）"""
        close = df['close']
        expma = close.ewm(span=period).mean()

        return {
            'expma': expma.iloc[-1],
            'expma_signal': self._get_expma_signal(close.iloc[-1], expma.iloc[-1])
        }

    def _calculate_bbi(self, df: pd.DataFrame) -> Dict[str, float]:
        """计算BBI指标（多空指标）"""
        close = df['close']
        ma3 = close.rolling(window=3).mean()
        ma6 = close.rolling(window=6).mean()
        ma12 = close.rolling(window=12).mean()
        ma24 = close.rolling(window=24).mean()

        bbi = (ma3 + ma6 + ma12 + ma24) / 4

        return {
            'bbi': bbi.iloc[-1],
            'bbi_signal': self._get_bbi_signal(close.iloc[-1], bbi.iloc[-1])
        }

    def _calculate_arbr(self, df: pd.DataFrame, period=26) -> Dict[str, float]:
        """计算ARBR指标（人气意愿指标）"""
        high = df['high']
        low = df['low']
        close = df['close']
        open_price = df['open']

        # 计算AR指标
        ar = sum(high - open_price) / sum(open_price - low) * 100

        # 计算BR指标
        br = sum(high - close.shift(1)) / sum(close.shift(1) - low) * 100

        return {
            'ar': ar.iloc[-1],
            'br': br.iloc[-1],
            'arbr_signal': self._get_arbr_signal(ar.iloc[-1], br.iloc[-1])
        }

    def _calculate_vr(self, df: pd.DataFrame, period=24) -> Dict[str, float]:
        """计算VR指标（成交率变异指标）"""
        close = df['close']
        volume = df['volume']

        # 根据涨跌分类成交量
        rising_volume = volume[close > close.shift(1)]
        falling_volume = volume[close < close.shift(1)]
        flat_volume = volume[close == close.shift(1)]

        # 计算VR
        vr = (rising_volume.sum() + flat_volume.sum() / 2) / (falling_volume.sum() + flat_volume.sum() / 2) * 100

        return {
            'vr': vr.iloc[-1] if len(vr) > 0 else 100,
            'vr_signal': self._get_vr_signal(vr.iloc[-1] if len(vr) > 0 else 100)
        }

    def _calculate_obv(self, df: pd.DataFrame) -> Dict[str, float]:
        """计算OBV指标（能量潮指标）"""
        close = df['close']
        volume = df['volume']

        # 计算OBV
        obv = np.where(close > close.shift(1), volume,
                    np.where(close < close.shift(1), -volume, 0))
        obv_cumsum = pd.Series(obv).cumsum()

        # 计算OBV移动平均
        obv_ma = obv_cumsum.rolling(window=10).mean()

        return {
            'obv': obv_cumsum.iloc[-1],
            'obv_ma': obv_ma.iloc[-1],
            'obv_signal': self._get_obv_signal(obv_cumsum.iloc[-1], obv_ma.iloc[-1])
        }

    def _calculate_emv(self, df: pd.DataFrame) -> Dict[str, float]:
        """计算EMV指标（简易波动指标）"""
        high = df['high']
        low = df['low']
        volume = df['volume']

        # 计算EMV
        distance = (high + low) / 2 - (high.shift(1) + low.shift(1)) / 2
        box_height = high - low
        emv = distance / (box_height / volume) if box_height != 0 else 0

        # 计算EMV移动平均
        emv_ma = pd.Series(emv).rolling(window=14).mean()

        return {
            'emv': emv.iloc[-1] if len(emv) > 0 else 0,
            'emv_ma': emv_ma.iloc[-1] if len(emv_ma) > 0 else 0,
            'emv_signal': self._get_emv_signal(emv.iloc[-1] if len(emv) > 0 else 0,
                                              emv_ma.iloc[-1] if len(emv_ma) > 0 else 0)
        }

    def _calculate_sar(self, df: pd.DataFrame, af=0.02, max_af=0.2) -> Dict[str, float]:
        """计算SAR指标（抛物线指标）"""
        high = df['high'].values
        low = df['low'].values

        if len(high) < 5:
            return {'sar': 0, 'sar_signal': 'hold'}

        # 简化SAR计算
        sar = np.zeros(len(high))
        ep = np.zeros(len(high))
        af_values = np.zeros(len(high))

        # 初始化
        af_values[0] = af
        ep[0] = high[0]
        sar[0] = low[0] - (high[0] - low[0]) * 0.1
        is_uptrend = True

        for i in range(1, len(high)):
            if is_uptrend:
                ep[i] = max(high[i], ep[i-1])
                if ep[i] > ep[i-1]:
                    af_values[i] = min(af_values[i-1] + af, max_af)
                else:
                    af_values[i] = af_values[i-1]

                sar[i] = sar[i-1] + af_values[i] * (ep[i] - sar[i-1])

                if low[i] < sar[i]:
                    is_uptrend = False
                    sar[i] = ep[i]
                    ep[i] = low[i]
                    af_values[i] = af
            else:
                ep[i] = min(low[i], ep[i-1])
                if ep[i] < ep[i-1]:
                    af_values[i] = min(af_values[i-1] + af, max_af)
                else:
                    af_values[i] = af_values[i-1]

                sar[i] = sar[i-1] + af_values[i] * (ep[i] - sar[i-1])

                if high[i] > sar[i]:
                    is_uptrend = True
                    sar[i] = ep[i]
                    ep[i] = high[i]
                    af_values[i] = af

        current_price = df['close'].iloc[-1]
        current_sar = sar[-1]

        return {
            'sar': current_sar,
            'sar_signal': 'buy' if current_price > current_sar else 'sell'
        }

    def _calculate_roc(self, df: pd.DataFrame, period=12) -> Dict[str, float]:
        """计算ROC指标（变动率指标）"""
        close = df['close']
        roc = (close - close.shift(period)) / close.shift(period) * 100

        return {
            'roc': roc.iloc[-1],
            'roc_trend': 'up' if roc.iloc[-1] > 0 else 'down',
            'roc_signal': self._get_roc_signal(roc.iloc[-1])
        }

    def _calculate_boll_width(self, df: pd.DataFrame, period=20, std_dev=2) -> Dict[str, float]:
        """计算布林带宽度"""
        ma = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        upper_band = ma + std * std_dev
        lower_band = ma - std * std_dev

        boll_width = (upper_band - lower_band) / ma

        return {
            'boll_width': boll_width.iloc[-1],
            'boll_width_trend': 'expanding' if boll_width.iloc[-1] > boll_width.iloc[-2] else 'contracting'
        }

    def _calculate_macd_histogram(self, df: pd.DataFrame, fast=12, slow=26, signal=9) -> Dict[str, float]:
        """计算MACD柱状图"""
        exp1 = df['close'].ewm(span=fast).mean()
        exp2 = df['close'].ewm(span=slow).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal).mean()
        histogram = macd - signal_line

        # 计算柱状图斜率
        histogram_slope = histogram.diff()

        return {
            'histogram': histogram.iloc[-1],
            'histogram_slope': histogram_slope.iloc[-1],
            'histogram_signal': self._get_histogram_signal(histogram.iloc[-1], histogram_slope.iloc[-1])
        }

    # 信号判断辅助方法
    def _get_dmi_signal(self, di_plus, di_minus):
        """获取DMI信号"""
        if di_plus > di_minus and di_plus > 20:
            return "buy"
        elif di_minus > di_plus and di_minus > 20:
            return "sell"
        else:
            return "hold"

    def _get_trix_signal(self, trix, trix_ma):
        """获取TRIX信号"""
        if trix > trix_ma and trix > 0:
            return "buy"
        elif trix < trix_ma and trix < 0:
            return "sell"
        else:
            return "hold"

    def _get_expma_signal(self, price, expma):
        """获取EXPMA信号"""
        if price > expma:
            return "buy"
        else:
            return "sell"

    def _get_bbi_signal(self, price, bbi):
        """获取BBI信号"""
        if price > bbi:
            return "buy"
        else:
            return "sell"

    def _get_arbr_signal(self, ar, br):
        """获取ARBR信号"""
        if ar > 100 and br > 100:
            return "buy"
        elif ar < 100 and br < 100:
            return "sell"
        else:
            return "hold"

    def _get_vr_signal(self, vr):
        """获取VR信号"""
        if vr > 160:
            return "buy"
        elif vr < 40:
            return "sell"
        else:
            return "hold"

    def _get_obv_signal(self, obv, obv_ma):
        """获取OBV信号"""
        if obv > obv_ma:
            return "buy"
        else:
            return "sell"

    def _get_emv_signal(self, emv, emv_ma):
        """获取EMV信号"""
        if emv > emv_ma and emv > 0:
            return "buy"
        elif emv < emv_ma and emv < 0:
            return "sell"
        else:
            return "hold"

    def _get_roc_signal(self, roc):
        """获取ROC信号"""
        if roc > 0 and roc < 20:
            return "buy"
        elif roc < 0 and roc > -20:
            return "sell"
        else:
            return "hold"

    def _get_histogram_signal(self, histogram, slope):
        """获取MACD柱状图信号"""
        if histogram > 0 and slope > 0:
            return "strong_buy"
        elif histogram > 0 and slope < 0:
            return "sell"
        elif histogram < 0 and slope > 0:
            return "buy"
        else:
            return "strong_sell"

  def _get_dmi_signal(self, di_plus, di_minus):
        """获取DMI信号"""
        if di_plus > di_minus and di_plus > 20:
            return "buy"
        elif di_minus > di_plus and di_minus > 20:
            return "sell"
        else:
            return "hold"

    def _get_trix_signal(self, trix, trix_ma):
        """获取TRIX信号"""
        if trix > trix_ma and trix > 0:
            return "buy"
        elif trix < trix_ma and trix < 0:
            return "sell"
        else:
            return "hold"

    def _get_expma_signal(self, price, expma):
        """获取EXPMA信号"""
        if price > expma:
            return "buy"
        else:
            return "sell"

    def _get_bbi_signal(self, price, bbi):
        """获取BBI信号"""
        if price > bbi:
            return "buy"
        else:
            return "sell"

    def _get_arbr_signal(self, ar, br):
        """获取ARBR信号"""
        if ar > 100 and br > 100:
            return "buy"
        elif ar < 100 and br < 100:
            return "sell"
        else:
            return "hold"

    def _get_vr_signal(self, vr):
        """获取VR信号"""
        if vr > 160:
            return "buy"
        elif vr < 40:
            return "sell"
        else:
            return "hold"

    def _get_obv_signal(self, obv, obv_ma):
        """获取OBV信号"""
        if obv > obv_ma:
            return "buy"
        else:
            return "sell"

    def _get_emv_signal(self, emv, emv_ma):
        """获取EMV信号"""
        if emv > emv_ma and emv > 0:
            return "buy"
        elif emv < emv_ma and emv < 0:
            return "sell"
        else:
            return "hold"

    def _get_roc_signal(self, roc):
        """获取ROC信号"""
        if roc > 0 and roc < 20:
            return "buy"
        elif roc < 0 and roc > -20:
            return "sell"
        else:
            return "hold"

    def _get_histogram_signal(self, histogram, slope):
        """获取MACD柱状图信号"""
        if histogram > 0 and slope > 0:
            return "strong_buy"
        elif histogram > 0 and slope < 0:
            return "sell"
        elif histogram < 0 and slope > 0:
            return "buy"
        else:
            return "strong_sell"

# 创建AI服务实例
ai_service = None

def get_ai_service() -> AIService:
    """获取AI服务实例"""
    global ai_service
    return ai_service

def init_ai_service(data_provider: DataProvider):
    """初始化AI服务"""
    global ai_service
    ai_service = AIService(data_provider)
    logger.info("AI分析服务初始化完成")
    return ai_service