"""
专家圆桌会议协调器
管理四位AI分析师的协作和意见整合
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List
from ..glm_analyzer import glm_analyzer


class RoundTableCoordinator:
    """专家圆桌会议协调器"""

    def __init__(self):
        self.experts = {
            "technical": {
                "name": "技术面分析师",
                "role": "technical",
                "description": "15年技术分析经验，专注技术指标、K线形态和趋势分析",
                "specialties": ["MACD", "KDJ", "RSI", "布林带", "趋势线"]
            },
            "fundamental": {
                "name": "基本面分析师",
                "role": "fundamental",
                "description": "专业财务分析背景，精通估值模型和行业分析",
                "specialties": ["财务报表", "估值模型", "ROE分析", "竞争优势"]
            },
            "news": {
                "name": "新闻分析师",
                "role": "news",
                "description": "资深财经记者背景，擅长新闻情感分析和事件解读",
                "specialties": ["情感分析", "政策解读", "市场情绪", "舆情监测"]
            },
            "risk": {
                "name": "风控分析师",
                "role": "risk",
                "description": "专业风险管理师，专注投资风险控制和仓位管理",
                "specialties": ["VaR计算", "仓位管理", "止损策略", "波动率分析"]
            }
        }

    async def start_round_table(self, symbol: str) -> Dict[str, Any]:
        """启动专家圆桌会议"""

        try:
            # 1. 数据收集阶段
            market_data = await self._collect_market_data(symbol)

            # 2. 专家分析阶段 (并行执行)
            expert_opinions = await self._concurrent_expert_analysis(symbol, market_data)

            # 3. 观点整合阶段
            consolidated_analysis = await self._consolidate_opinions(expert_opinions)

            # 4. 最终建议生成
            final_recommendation = await self._generate_final_recommendation(
                symbol, expert_opinions, consolidated_analysis
            )

            return {
                "symbol": symbol,
                "meeting_timestamp": datetime.now().isoformat(),
                "expert_opinions": expert_opinions,
                "consolidated_analysis": consolidated_analysis,
                "final_recommendation": final_recommendation,
                "meeting_status": "completed"
            }

        except Exception as e:
            return {
                "symbol": symbol,
                "error": f"专家圆桌会议失败: {str(e)}",
                "meeting_status": "failed",
                "meeting_timestamp": datetime.now().isoformat()
            }

    async def _collect_market_data(self, symbol: str) -> Dict[str, Any]:
        """收集市场数据"""
        try:
            from ..data_service.stock_service_lite import stock_service_lite

            # 获取股票基本信息
            stock_info = await stock_service_lite.get_stock_info(symbol)

            # 获取历史数据
            history_data = await stock_service_lite.get_stock_history(symbol, "1m")

            return {
                "basic_info": stock_info,
                "history": history_data,
                "collection_time": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"收集市场数据失败 {symbol}: {e}")
            return {
                "basic_info": {"success": False, "error": "DATA_UNAVAILABLE", "message": f"暂时无法获取股票 {symbol} 的数据，请稍后再试"},
                "history": {"success": False, "error": "DATA_UNAVAILABLE", "message": f"暂时无法获取股票 {symbol} 的历史数据，请稍后再试"},
                "collection_time": datetime.now().isoformat(),
                "error": str(e)
            }

    async def _concurrent_expert_analysis(self, symbol: str, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """并行专家分析"""

        analysis_tasks = []

        for expert_key, expert_config in self.experts.items():
            task = self._single_expert_analysis(
                symbol, expert_key, expert_config, market_data
            )
            analysis_tasks.append(task)

        # 等待所有专家完成分析
        expert_opinions = await asyncio.gather(*analysis_tasks, return_exceptions=True)

        # 处理异常结果
        valid_opinions = []
        for i, opinion in enumerate(expert_opinions):
            expert_key = list(self.experts.keys())[i]
            if isinstance(opinion, Exception):
                valid_opinions.append({
                    "expert_type": expert_key,
                    "expert_name": self.experts[expert_key]["name"],
                    "error": str(opinion),
                    "timestamp": datetime.now().isoformat()
                })
            else:
                opinion["expert_type"] = expert_key
                opinion["expert_name"] = self.experts[expert_key]["name"]
                valid_opinions.append(opinion)

        return valid_opinions

    async def _single_expert_analysis(
        self,
        symbol: str,
        expert_type: str,
        expert_config: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """单个专家分析"""

        try:
            # 构建分析提示
            analysis_prompt = self._build_analysis_prompt(
                symbol, expert_type, expert_config, market_data
            )

            # 调用GLM分析
            result = await glm_analyzer.analyze_with_expert_role(
                analysis_prompt,
                expert_type,
                f"你是{expert_config['name']}，请基于提供的市场数据进行专业分析。",
                "json"
            )

            # 格式化专家意见
            expert_opinion = {
                "expert_type": expert_type,
                "expert_name": expert_config["name"],
                "analysis": result,
                "specialties": expert_config["specialties"],
                "confidence": self._extract_confidence(result),
                "timestamp": datetime.now().isoformat()
            }

            # 提取关键信息
            if isinstance(result, dict):
                expert_opinion.update({
                    "score": result.get("score", 7.0),
                    "signal": result.get("signal", "持有"),
                    "key_insights": result.get("key_insights", [])
                })

            return expert_opinion

        except Exception as e:
            return {
                "expert_type": expert_type,
                "expert_name": expert_config["name"],
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _build_analysis_prompt(
        self,
        symbol: str,
        expert_type: str,
        expert_config: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> str:
        """构建分析提示"""

        prompt = f"""
作为{expert_config['name']}，请对股票 {symbol} 进行专业分析。

市场数据：
- 当前价格: {market_data.get('basic_info', {}).get('current_price', 'N/A')}
- 涨跌幅: {market_data.get('basic_info', {}).get('change_percent', 'N/A')}%
- 成交量: {market_data.get('basic_info', {}).get('volume', 'N/A')}

分析要点：
"""

        # 根据专家类型添加特定的分析要点
        if expert_type == "technical":
            prompt += """
1. 技术指标分析 (MACD, KDJ, RSI等)
2. 趋势判断和形态分析
3. 支撑位和阻力位识别
4. 短期走势预测 (1-4周)
"""
        elif expert_type == "fundamental":
            prompt += """
1. 财务状况评估
2. 估值水平分析
3. 行业地位和竞争优势
4. 长期投资价值判断
"""
        elif expert_type == "news":
            prompt += """
1. 相关新闻舆情分析
2. 市场情绪评估
3. 政策和事件影响
4. 新闻驱动的价格影响
"""
        elif expert_type == "risk":
            prompt += """
1. 投资风险评估
2. 仓位管理建议
3. 止损策略制定
4. 波动性分析

请提供JSON格式的分析结果，包含：
- score: 评分 (0-10)
- signal: 投资信号 ("买入", "持有", "卖出")
- key_insights: 关键洞察 (列表)
- confidence: 分析置信度 (0-1)
- reasoning: 分析理由
"""

        return prompt

    def _extract_confidence(self, result: Any) -> float:
        """提取置信度"""
        if isinstance(result, dict):
            return float(result.get("confidence", 0.7))
        return 0.7

    async def _consolidate_opinions(self, expert_opinions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """整合专家意见"""

        valid_opinions = [op for op in expert_opinions if "error" not in op]

        if not valid_opinions:
            return {"error": "没有有效的专家意见"}

        # 统计分析
        signals = {"买入": 0, "持有": 0, "卖出": 0}
        total_score = 0
        total_confidence = 0
        all_insights = []

        for opinion in valid_opinions:
            analysis = opinion.get("analysis", {})
            if isinstance(analysis, dict):
                signal = analysis.get("signal", "持有")
                score = analysis.get("score", 7.0)
                confidence = analysis.get("confidence", 0.7)
                insights = analysis.get("key_insights", [])

                if signal in signals:
                    signals[signal] += 1
                total_score += score
                total_confidence += confidence
                all_insights.extend(insights if isinstance(insights, list) else [])

        # 计算平均值
        avg_score = total_score / len(valid_opinions) if valid_opinions else 7.0
        avg_confidence = total_confidence / len(valid_opinions) if valid_opinions else 0.7

        # 确定主导信号
        dominant_signal = max(signals, key=signals.get)

        return {
            "dominant_signal": dominant_signal,
            "signal_distribution": signals,
            "average_score": round(avg_score, 1),
            "average_confidence": round(avg_confidence, 2),
            "consensus_level": max(signals.values()) / len(valid_opinions) if valid_opinions else 0,
            "key_insights": all_insights[:10],  # 最多10个关键洞察
            "valid_experts": len(valid_opinions),
            "total_experts": len(expert_opinions)
        }

    async def _generate_final_recommendation(
        self,
        symbol: str,
        expert_opinions: List[Dict[str, Any]],
        consolidated_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成最终投资建议"""

        if "error" in consolidated_analysis:
            return {
                "recommendation": "建议重新分析",
                "confidence": 0.0,
                "risk_level": "高",
                "reason": "专家分析数据不足"
            }

        # 基于整合分析生成建议
        dominant_signal = consolidated_analysis["dominant_signal"]
        avg_score = consolidated_analysis["average_score"]
        avg_confidence = consolidated_analysis["average_confidence"]
        consensus_level = consolidated_analysis["consensus_level"]

        # 确定最终建议
        if avg_score >= 8.0 and consensus_level >= 0.75:
            recommendation = "强烈买入"
        elif avg_score >= 6.5 and consensus_level >= 0.5:
            recommendation = "买入"
        elif avg_score >= 4.0:
            recommendation = "持有"
        elif avg_score >= 2.0:
            recommendation = "卖出"
        else:
            recommendation = "强烈卖出"

        # 确定风险等级
        if avg_confidence >= 0.8:
            risk_level = "低"
        elif avg_confidence >= 0.6:
            risk_level = "中等"
        else:
            risk_level = "高"

        # 生成建议理由
        key_reasons = [
            f"专家共识度: {consensus_level*100:.1f}%",
            f"综合评分: {avg_score}/10",
            f"主导信号: {dominant_signal}",
            f"专家参与: {consolidated_analysis['valid_experts']}/{consolidated_analysis['total_experts']}位"
        ]

        return {
            "recommendation": recommendation,
            "confidence": avg_confidence,
            "risk_level": risk_level,
            "target_price": None,  # 可以根据需要添加
            "stop_loss": None,      # 可以根据需要添加
            "position_size": self._suggest_position_size(avg_score, risk_level),
            "key_reasons": key_reasons,
            "disclaimer": "投资建议仅供参考，不构成投资建议。投资有风险，入市需谨慎。"
        }

    def _suggest_position_size(self, score: float, risk_level: str) -> str:
        """建议仓位大小"""
        if score >= 8.0 and risk_level == "低":
            return "重仓 (20-30%)"
        elif score >= 6.5:
            return "中等仓位 (10-20%)"
        elif score >= 4.0:
            return "轻仓 (5-10%)"
        else:
            return "观望或清仓"


# 创建全局实例
round_table_coordinator = RoundTableCoordinator()