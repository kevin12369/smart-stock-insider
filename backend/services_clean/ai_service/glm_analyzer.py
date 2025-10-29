#!/usr/bin/env python3
"""
GLM-4.5-Flash AI分析核心接口

Author: Smart Stock Insider Team
Version: 1.0.0
"""

import json
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import httpx
from loguru import logger

from core.config import settings


class GLMAnalyzer:
    """GLM-4.5-Flash AI分析器"""

    def __init__(self):
        self.api_key = settings.GLM_API_KEY
        self.base_url = settings.GLM_BASE_URL
        self.model = settings.GLM_MODEL
        self.max_tokens = getattr(settings, 'GLM_MAX_TOKENS', 96000)
        self.temperature = getattr(settings, 'GLM_TEMPERATURE', 0.7)

        # 验证配置
        if not self.api_key:
            raise ValueError("GLM_API_KEY 未配置")

    async def _call_glm_api(self, messages: list, expert_role: str = None) -> str:
        """调用GLM-4.5-Flash API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "stream": False
            }

            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()

                result = response.json()
                return result["choices"][0]["message"]["content"]

        except httpx.HTTPStatusError as e:
            logger.error(f"GLM API HTTP错误: {e}")
            raise
        except Exception as e:
            logger.error(f"GLM API调用失败: {e}")
            raise

    async def analyze_with_expert_role(
        self,
        content: str,
        expert_role: str,
        system_prompt: str,
        output_format: str = "json"
    ) -> Dict[str, Any]:
        """使用专家角色进行分析"""

        messages = [
            {
                "role": "system",
                "content": f"{system_prompt}\n\n请以{expert_role}的身份进行分析，输出格式为{output_format}。"
            },
            {
                "role": "user",
                "content": content
            }
        ]

        try:
            raw_response = await self._call_glm_api(messages, expert_role)

            # 尝试解析JSON响应
            if output_format.lower() == "json":
                try:
                    # 提取JSON部分
                    if "```json" in raw_response:
                        json_start = raw_response.find("```json") + 7
                        json_end = raw_response.find("```", json_start)
                        json_str = raw_response[json_start:json_end].strip()
                    else:
                        json_str = raw_response.strip()

                    return json.loads(json_str)
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON解析失败，返回原始响应: {e}")
                    return {
                        "raw_response": raw_response,
                        "expert_role": expert_role,
                        "timestamp": datetime.now().isoformat()
                    }
            else:
                return {
                    "response": raw_response,
                    "expert_role": expert_role,
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"专家分析失败 {expert_role}: {e}")
            return {
                "error": str(e),
                "expert_role": expert_role,
                "timestamp": datetime.now().isoformat()
            }

    async def health_check(self) -> bool:
        """GLM服务健康检查"""
        try:
            test_messages = [
                {"role": "user", "content": "测试连接，请回复OK"}
            ]
            response = await self._call_glm_api(test_messages)
            return "OK" in response or "ok" in response
        except Exception as e:
            logger.error(f"GLM健康检查失败: {e}")
            return False


# 全局GLM分析器实例
glm_analyzer = GLMAnalyzer()


# 预定义的专家角色提示词
EXPERT_PROMPTS = {
    "technical": """
你是一位资深的技术面分析师，拥有15年股票技术分析经验。请从以下角度分析股票：

1. 技术指标分析 (MACD, KDJ, RSI, 布林带等)
2. K线形态识别 (头肩顶底、双顶双底、三角形等)
3. 趋势线分析 (支撑位、阻力位、趋势通道)
4. 量价关系分析 (放量突破、缩量整理等)
5. 短期走势预测 (1-4周)

请提供：
- 技术面评分 (1-10分，10分为最优)
- 明确的买卖信号 (买入/持有/卖出)
- 关键技术价位 (支撑位、阻力位、目标位)
- 具体的操作建议和理由

输出JSON格式：
{
  "technical_score": 8.5,
  "signal": "买入",
  "key_levels": {
    "support": 12.50,
    "resistance": 15.80,
    "target": 18.20
  },
  "recommendation": "建议买入",
  "reasoning": "技术分析详细理由",
  "time_horizon": "1-4周",
  "confidence": 0.85
}
""",

    "fundamental": """
你是一位专业的基本面分析师，拥有丰富的财务分析和估值经验。请从以下角度分析股票：

1. 财务报表分析 (资产负债表、利润表、现金流量表)
2. 关键财务指标 (ROE、ROA、毛利率、净利率等)
3. 估值模型计算 (PE、PB、PEG、DCF等)
4. 行业地位和竞争优势
5. 成长性和盈利能力评估

请提供：
- 基本面评分 (1-10分，10分为最优)
- 合理估值区间
- 财务健康状况评估
- 长期投资价值判断
- 风险因素提示

输出JSON格式：
{
  "fundamental_score": 7.8,
  "valuation_range": {
    "low": 14.20,
    "fair_value": 16.50,
    "high": 18.80
  },
  "financial_health": "健康",
  "long_term_outlook": "看好",
  "key_metrics": {
    "pe_ratio": 15.2,
    "pb_ratio": 2.1,
    "roe": 0.18,
    "debt_ratio": 0.35
  },
  "investment_thesis": "基本面投资逻辑",
  "confidence": 0.80
}
""",

    "news": """
你是一位专业的新闻分析师，擅长从新闻事件中挖掘投资机会和风险。请分析以下新闻信息：

1. 新闻情感倾向分析 (正面/负面/中性)
2. 重大事件解读和影响评估
3. 政策变化的影响分析
4. 市场情绪和预期变化
5. 潜在的催化剂和风险因素

请提供：
- 新闻面评分 (1-10分，10分为最正面)
- 情感倾向和强度
- 影响程度评估 (高/中/低)
- 投资机会和风险提示
- 市场预期变化

输出JSON格式：
{
  "news_score": 6.5,
  "sentiment": "中性偏正面",
  "sentiment_strength": 0.6,
  "impact_level": "中等",
  "key_factors": [
    "政策利好因素1",
    "市场情绪因素2",
    "行业趋势因素3"
  ],
  "opportunities": [
    "投资机会1",
    "投资机会2"
  ],
  "risks": [
    "风险因素1",
    "风险因素2"
  ],
  "market_impact": "市场影响分析",
  "confidence": 0.75
}
""",

    "risk": """
你是一位专业的风控分析师，专注于投资风险管理和仓位控制。请从以下角度评估投资风险：

1. 市场风险评估 (系统性风险、非系统性风险)
2. 波动率分析和VaR计算
3. 仓位管理建议
4. 止损止盈策略制定
5. 黑天鹅事件预警

请提供：
- 风险评级 (低/中/高)
- 建议仓位比例
- 止损止盈点位
- 风险控制措施
- 最大回撤预估

输出JSON格式：
{
  "risk_rating": "中等",
  "risk_score": 6.2,
  "recommended_position": "0.15-0.25",
  "stop_loss": 11.80,
  "take_profit": [17.50, 19.80],
  "max_drawdown_estimate": 0.18,
  "risk_factors": [
    "市场风险1",
    "流动性风险2",
    "政策风险3"
  ],
  "risk_control_measures": [
    "风控措施1",
    "风控措施2"
  ],
  "var_analysis": {
    "var_95": 0.12,
    "var_99": 0.18
  },
  "confidence": 0.85
}
"""
}


async def get_expert_analysis(expert_type: str, content: str) -> Dict[str, Any]:
    """获取专家分析结果"""
    if expert_type not in EXPERT_PROMPTS:
        raise ValueError(f"不支持的专家类型: {expert_type}")

    system_prompt = EXPERT_PROMPTS[expert_type]

    return await glm_analyzer.analyze_with_expert_role(
        content=content,
        expert_role=expert_type,
        system_prompt=system_prompt,
        output_format="json"
    )