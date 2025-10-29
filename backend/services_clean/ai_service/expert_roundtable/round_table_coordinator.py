#!/usr/bin/env python3
"""
专家圆桌会议协调器

Author: Smart Stock Insider Team
Version: 1.0.0
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from loguru import logger

from ..glm_analyzer import get_expert_analysis
from ...data_service.stock_service import stock_service


@dataclass
class ExpertOpinion:
    """专家意见数据结构"""
    expert_type: str
    score: float
    signal: str
    analysis: Dict[str, Any]
    confidence: float
    timestamp: datetime
    key_insights: List[str]


@dataclass
class MarketData:
    """市场数据结构"""
    symbol: str
    price_data: Dict[str, Any]
    technical_indicators: Dict[str, Any]
    fundamental_data: Dict[str, Any]
    news_data: List[Dict[str, Any]]
    market_sentiment: Dict[str, Any]


class RoundTableCoordinator:
    """专家圆桌会议协调器"""

    def __init__(self):
        self.expert_types = ["technical", "fundamental", "news", "risk"]
        self.weighting_system = {
            "technical": 0.30,      # 技术面权重
            "fundamental": 0.35,    # 基本面权重
            "news": 0.20,           # 新闻面权重
            "risk": 0.15            # 风险面权重
        }

        # 专家专业领域
        self.expert_domains = {
            "technical": "技术面分析师",
            "fundamental": "基本面分析师",
            "news": "新闻分析师",
            "risk": "风控分析师"
        }

    async def start_round_table(self, symbol: str) -> Dict[str, Any]:
        """启动专家圆桌会议"""
        logger.info(f"启动专家圆桌会议: {symbol}")

        try:
            # 1. 数据收集阶段
            market_data = await self._collect_market_data(symbol)

            # 2. 专家分析阶段 (并行执行)
            expert_opinions = await self._concurrent_expert_analysis(market_data)

            # 3. 观点整合阶段
            consolidated_analysis = await self._consolidate_opinions(expert_opinions)

            # 4. 综合建议生成
            final_recommendation = await self._generate_final_recommendation(
                symbol, market_data, expert_opinions, consolidated_analysis
            )

            return {
                "symbol": symbol,
                "meeting_timestamp": datetime.now().isoformat(),
                "market_data": market_data,
                "expert_opinions": expert_opinions,
                "consolidated_analysis": consolidated_analysis,
                "final_recommendation": final_recommendation,
                "meeting_status": "completed"
            }

        except Exception as e:
            logger.error(f"专家圆桌会议失败 {symbol}: {e}")
            return {
                "symbol": symbol,
                "meeting_timestamp": datetime.now().isoformat(),
                "error": str(e),
                "meeting_status": "failed"
            }

    async def _collect_market_data(self, symbol: str) -> MarketData:
        """收集市场数据"""
        logger.info(f"收集市场数据: {symbol}")

        try:
            # 获取基础股票数据
            stock_info = await stock_service.get_stock_info(symbol)

            # 获取历史价格数据
            price_data = await stock_service.get_historical_data(symbol, period="1y")

            # 计算技术指标
            technical_indicators = await stock_service.get_technical_indicators(symbol)

            # 获取基本面数据 (简化版本)
            fundamental_data = await stock_service.get_fundamental_data(symbol)

            # 获取新闻数据 (简化版本)
            news_data = await stock_service.get_stock_news(symbol, limit=10)

            return MarketData(
                symbol=symbol,
                price_data=price_data,
                technical_indicators=technical_indicators,
                fundamental_data=fundamental_data,
                news_data=news_data,
                market_sentiment={"overall": "neutral", "score": 0.5}
            )

        except Exception as e:
            logger.error(f"市场数据收集失败 {symbol}: {e}")
            raise

    async def _concurrent_expert_analysis(self, market_data: MarketData) -> List[ExpertOpinion]:
        """并行专家分析"""
        logger.info("开始并行专家分析")

        # 创建分析任务
        tasks = []
        for expert_type in self.expert_types:
            task = self._analyze_with_expert(expert_type, market_data)
            tasks.append(task)

        # 并行执行所有专家分析
        results = await asyncio.gather(*tasks, return_exceptions=True)

        expert_opinions = []
        for i, result in enumerate(results):
            expert_type = self.expert_types[i]

            if isinstance(result, Exception):
                logger.error(f"专家{expert_type}分析失败: {result}")
                # 创建默认意见
                opinion = ExpertOpinion(
                    expert_type=expert_type,
                    score=5.0,
                    signal="持有",
                    analysis={"error": str(result)},
                    confidence=0.0,
                    timestamp=datetime.now(),
                    key_insights=[f"专家{expert_type}分析失败"]
                )
            else:
                opinion = self._parse_expert_result(expert_type, result)

            expert_opinions.append(opinion)

        return expert_opinions

    async def _analyze_with_expert(self, expert_type: str, market_data: MarketData) -> Dict[str, Any]:
        """单个专家分析"""
        # 构建专家特定的分析内容
        content = self._build_analysis_content(expert_type, market_data)

        # 调用专家分析
        return await get_expert_analysis(expert_type, content)

    def _build_analysis_content(self, expert_type: str, market_data: MarketData) -> str:
        """构建专家分析内容"""
        base_info = f"""
股票代码: {market_data.symbol}
当前价格: {market_data.price_data.get('current_price', 'N/A')}
涨跌幅: {market_data.price_data.get('change_percent', 'N/A')}%
成交量: {market_data.price_data.get('volume', 'N/A')}
"""

        if expert_type == "technical":
            return f"""
{base_info}

技术指标数据:
{self._format_technical_indicators(market_data.technical_indicators)}

历史价格数据 (最近30天):
{self._format_price_history(market_data.price_data)}

请基于以上技术数据进行专业分析。
"""

        elif expert_type == "fundamental":
            return f"""
{base_info}

基本面数据:
{self._format_fundamental_data(market_data.fundamental_data)}

请基于以上基本面数据进行专业分析。
"""

        elif expert_type == "news":
            return f"""
{base_info}

相关新闻数据:
{self._format_news_data(market_data.news_data)}

请基于以上新闻信息进行专业分析。
"""

        elif expert_type == "risk":
            return f"""
{base_info}

风险评估数据:
技术指标: {self._format_technical_indicators(market_data.technical_indicators)}
基本面数据: {self._format_fundamental_data(market_data.fundamental_data)}
新闻数据: {self._format_news_data(market_data.news_data)}

请基于以上数据进行专业的风险评估。
"""

        return base_info

    def _format_technical_indicators(self, indicators: Dict[str, Any]) -> str:
        """格式化技术指标"""
        if not indicators:
            return "暂无技术指标数据"

        formatted = []
        for key, value in indicators.items():
            if isinstance(value, (int, float)):
                formatted.append(f"{key}: {value:.4f}")
            else:
                formatted.append(f"{key}: {value}")

        return "\n".join(formatted)

    def _format_price_history(self, price_data: Dict[str, Any]) -> str:
        """格式化价格历史"""
        history = price_data.get('history', [])
        if not history:
            return "暂无历史数据"

        # 取最近10天数据
        recent_data = history[-10:] if len(history) > 10 else history

        formatted = []
        for data in recent_data:
            date = data.get('date', 'N/A')
            price = data.get('close', 'N/A')
            volume = data.get('volume', 'N/A')
            formatted.append(f"{date}: 收盘价 {price}, 成交量 {volume}")

        return "\n".join(formatted)

    def _format_fundamental_data(self, fundamental_data: Dict[str, Any]) -> str:
        """格式化基本面数据"""
        if not fundamental_data:
            return "暂无基本面数据"

        formatted = []
        for key, value in fundamental_data.items():
            if isinstance(value, (int, float)):
                formatted.append(f"{key}: {value:.2f}")
            else:
                formatted.append(f"{key}: {value}")

        return "\n".join(formatted)

    def _format_news_data(self, news_data: List[Dict[str, Any]]) -> str:
        """格式化新闻数据"""
        if not news_data:
            return "暂无相关新闻"

        formatted = []
        for i, news in enumerate(news_data[:5], 1):  # 取最近5条新闻
            title = news.get('title', 'N/A')
            date = news.get('date', 'N/A')
            sentiment = news.get('sentiment', 'neutral')
            formatted.append(f"{i}. {title} ({date}) [{sentiment}]")

        return "\n".join(formatted)

    def _parse_expert_result(self, expert_type: str, result: Dict[str, Any]) -> ExpertOpinion:
        """解析专家分析结果"""
        if "error" in result:
            return ExpertOpinion(
                expert_type=expert_type,
                score=5.0,
                signal="持有",
                analysis=result,
                confidence=0.0,
                timestamp=datetime.now(),
                key_insights=[f"专家{expert_type}分析出错"]
            )

        # 提取关键信息
        score = result.get(f"{expert_type}_score", result.get("score", 5.0))
        signal = result.get("signal", result.get("recommendation", "持有"))
        confidence = result.get("confidence", 0.7)

        # 提取关键洞察
        key_insights = []
        if "reasoning" in result:
            key_insights.append(result["reasoning"])
        if "recommendation" in result:
            key_insights.append(result["recommendation"])
        if "key_factors" in result:
            key_insights.extend(result["key_factors"])

        return ExpertOpinion(
            expert_type=expert_type,
            score=float(score),
            signal=signal,
            analysis=result,
            confidence=float(confidence),
            timestamp=datetime.now(),
            key_insights=key_insights[:3]  # 最多保留3个关键洞察
        )

    async def _consolidate_opinions(self, expert_opinions: List[ExpertOpinion]) -> Dict[str, Any]:
        """整合专家意见"""
        logger.info("整合专家意见")

        # 计算加权平均分
        weighted_score = 0.0
        total_weight = 0.0

        for opinion in expert_opinions:
            weight = self.weighting_system.get(opinion.expert_type, 0.25)
            weighted_score += opinion.score * weight * opinion.confidence
            total_weight += weight * opinion.confidence

        final_score = weighted_score / total_weight if total_weight > 0 else 5.0

        # 分析意见一致性
        signals = [opinion.signal for opinion in expert_opinions]
        consensus_level = self._calculate_consensus_level(signals)

        # 提取共同洞察
        all_insights = []
        for opinion in expert_opinions:
            all_insights.extend(opinion.key_insights)

        return {
            "final_score": round(final_score, 2),
            "consensus_level": consensus_level,
            "individual_scores": {
                opinion.expert_type: opinion.score
                for opinion in expert_opinions
            },
            "individual_signals": {
                opinion.expert_type: opinion.signal
                for opinion in expert_opinions
            },
            "key_insights": all_insights,
            "analysis_timestamp": datetime.now().isoformat()
        }

    def _calculate_consensus_level(self, signals: List[str]) -> float:
        """计算意见一致性水平"""
        if not signals:
            return 0.0

        # 简化的一致性计算
        signal_counts = {}
        for signal in signals:
            signal_counts[signal] = signal_counts.get(signal, 0) + 1

        # 最多的信号数量 / 总信号数量
        max_count = max(signal_counts.values())
        consensus_level = max_count / len(signals)

        return round(consensus_level, 2)

    async def _generate_final_recommendation(
        self,
        symbol: str,
        market_data: MarketData,
        expert_opinions: List[ExpertOpinion],
        consolidated_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成最终投资建议"""
        logger.info(f"生成最终投资建议: {symbol}")

        final_score = consolidated_analysis["final_score"]
        consensus_level = consolidated_analysis["consensus_level"]

        # 根据分数确定建议
        if final_score >= 8.0:
            recommendation = "强烈买入"
            risk_level = "低"
        elif final_score >= 6.5:
            recommendation = "买入"
            risk_level = "中等偏低"
        elif final_score >= 4.0:
            recommendation = "持有"
            risk_level = "中等"
        elif final_score >= 2.5:
            recommendation = "卖出"
            risk_level = "中等偏高"
        else:
            recommendation = "强烈卖出"
            risk_level = "高"

        # 提取关键风险因素
        risk_opinion = next((op for op in expert_opinions if op.expert_type == "risk"), None)
        risk_factors = risk_opinion.key_insights if risk_opinion else []

        # 生成投资理由
        investment_reasoning = self._generate_investment_reasoning(
            expert_opinions, consolidated_analysis
        )

        return {
            "recommendation": recommendation,
            "confidence": round(final_score / 10, 2),
            "risk_level": risk_level,
            "target_price": self._estimate_target_price(market_data, expert_opinions),
            "investment_horizon": "1-3个月",
            "position_size": self._recommend_position_size(final_score, risk_opinion),
            "stop_loss": self._recommend_stop_loss(market_data, expert_opinions),
            "key_reasons": investment_reasoning,
            "risk_factors": risk_factors,
            "next_review_date": self._suggest_next_review_date(),
            "disclaimer": "投资建议仅供参考，投资有风险，入市需谨慎"
        }

    def _generate_investment_reasoning(
        self,
        expert_opinions: List[ExpertOpinion],
        consolidated_analysis: Dict[str, Any]
    ) -> List[str]:
        """生成投资理由"""
        reasons = []

        # 从各专家意见中提取关键理由
        for opinion in expert_opinions:
            expert_name = self.expert_domains.get(opinion.expert_type, opinion.expert_type)

            if opinion.score >= 7.0:
                reasons.append(f"{expert_name}给出{opinion.score}分高分，看好{opinion.signal}")
            elif opinion.score <= 3.0:
                reasons.append(f"{expert_name}给出{opinion.score}分低分，建议{opinion.signal}")

        # 添加共识相关信息
        consensus_level = consolidated_analysis["consensus_level"]
        if consensus_level >= 0.8:
            reasons.append(f"专家团队意见高度一致({consensus_level:.0%})")
        elif consensus_level <= 0.4:
            reasons.append(f"专家团队意见分歧较大({consensus_level:.0%})")

        return reasons[:5]  # 最多返回5个理由

    def _estimate_target_price(
        self,
        market_data: MarketData,
        expert_opinions: List[ExpertOpinion]
    ) -> Optional[float]:
        """估算目标价格"""
        current_price = market_data.price_data.get('current_price')
        if not current_price:
            return None

        # 基于技术分析和基本面分析估算目标价
        technical_opinion = next((op for op in expert_opinions if op.expert_type == "technical"), None)
        fundamental_opinion = next((op for op in expert_opinions if op.expert_type == "fundamental"), None)

        target_prices = []

        if technical_opinion and "key_levels" in technical_opinion.analysis:
            key_levels = technical_opinion.analysis["key_levels"]
            if "target" in key_levels:
                target_prices.append(key_levels["target"])

        if fundamental_opinion and "valuation_range" in fundamental_opinion.analysis:
            valuation = fundamental_opinion.analysis["valuation_range"]
            if "fair_value" in valuation:
                target_prices.append(valuation["fair_value"])

        if target_prices:
            return sum(target_prices) / len(target_prices)

        # 简化估算：基于当前价格和综合评分
        score_adjustment = (consolidated_analysis["final_score"] - 5.0) / 5.0
        return current_price * (1 + score_adjustment * 0.2)  # 最多20%的调整

    def _recommend_position_size(self, final_score: float, risk_opinion: Optional[ExpertOpinion]) -> str:
        """推荐仓位大小"""
        if risk_opinion and "recommended_position" in risk_opinion.analysis:
            return risk_opinion.analysis["recommended_position"]

        # 基于分数推荐仓位
        if final_score >= 8.0:
            return "20-30%"
        elif final_score >= 6.5:
            return "10-20%"
        elif final_score >= 4.0:
            return "5-10%"
        else:
            return "0-5%"

    def _recommend_stop_loss(self, market_data: MarketData, expert_opinions: List[ExpertOpinion]) -> Optional[float]:
        """推荐止损价格"""
        current_price = market_data.price_data.get('current_price')
        if not current_price:
            return None

        risk_opinion = next((op for op in expert_opinions if op.expert_type == "risk"), None)
        if risk_opinion and "stop_loss" in risk_opinion.analysis:
            return risk_opinion.analysis["stop_loss"]

        # 简化止损：当前价格的8-12%
        return current_price * 0.92

    def _suggest_next_review_date(self) -> str:
        """建议下次复盘日期"""
        from datetime import datetime, timedelta
        next_date = datetime.now() + timedelta(days=7)
        return next_date.strftime("%Y-%m-%d")


# 全局圆桌会议协调器实例
round_table_coordinator = RoundTableCoordinator()