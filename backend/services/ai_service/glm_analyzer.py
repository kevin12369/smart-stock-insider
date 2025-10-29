"""
GLM-4.5-Flash AI分析服务
简化版本，专注于专家圆桌会议功能
"""

import httpx
import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel


class GLMAnalyzer:
    """GLM-4.5-Flash AI分析器"""

    def __init__(self):
        self.api_key = os.getenv("GLM_API_KEY", "cfc8b95952484113863c16338f682547.VUsS3wsFHwDERwye")
        self.base_url = os.getenv("GLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4/chat/completions")
        self.model = os.getenv("GLM_MODEL", "glm-4.5-flash")
        self.client = httpx.AsyncClient(timeout=60.0)

    async def health_check(self) -> bool:
        """健康检查"""
        try:
            # 简单的健康检查，测试API连接
            response = await self.client.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": "健康检查"}],
                    "max_tokens": 10
                }
            )
            return response.status_code == 200
        except Exception as e:
            print(f"GLM健康检查失败: {e}")
            return False

    async def analyze_with_expert_role(
        self,
        content: str,
        expert_role: str,
        system_prompt: str,
        output_format: str = "json"
    ) -> Dict[str, Any]:
        """使用专家角色进行分析"""

        expert_prompts = {
            "technical": {
                "system": "你是一位资深的技术面分析师，拥有15年技术分析经验。你专注于技术指标、K线形态和趋势分析，擅长MACD、KDJ、RSI等技术指标。",
                "focus": "技术指标分析、趋势判断、关键价位识别"
            },
            "fundamental": {
                "system": "你是一位专业的基本面分析师，拥有深厚的财务分析背景。你精通估值模型和行业分析，擅长财务报表分析和ROE分析。",
                "focus": "财务分析、估值评估、竞争优势分析"
            },
            "news": {
                "system": "你是一位资深的新闻分析师，拥有财经记者背景。你擅长新闻情感分析和事件解读，精通政策解读和市场情绪分析。",
                "focus": "新闻影响、市场情绪、政策解读"
            },
            "risk": {
                "system": "你是一位专业的风险管理师，专注投资风险控制和仓位管理。你擅长VaR计算、止损策略和波动率分析。",
                "focus": "风险评估、仓位管理、止损策略"
            }
        }

        expert_config = expert_prompts.get(expert_role, expert_prompts["technical"])

        try:
            messages = [
                {"role": "system", "content": expert_config["system"]},
                {"role": "user", "content": content}
            ]

            response = await self.client.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": 2000,
                    "temperature": 0.7
                }
            )

            if response.status_code == 200:
                result = response.json()
                analysis_text = result["choices"][0]["message"]["content"]

                # 尝试解析JSON格式输出
                if output_format == "json":
                    try:
                        analysis_data = json.loads(analysis_text)
                    except json.JSONDecodeError:
                        # 如果不是JSON格式，包装成JSON
                        analysis_data = {
                            "analysis": analysis_text,
                            "expert_type": expert_role,
                            "focus": expert_config["focus"],
                            "timestamp": datetime.now().isoformat()
                        }
                else:
                    analysis_data = {
                        "analysis": analysis_text,
                        "expert_type": expert_role,
                        "focus": expert_config["focus"],
                        "timestamp": datetime.now().isoformat()
                    }

                return analysis_data
            else:
                return {
                    "error": f"API请求失败: {response.status_code}",
                    "expert_type": expert_role,
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            return {
                "error": f"分析过程出错: {str(e)}",
                "expert_type": expert_role,
                "timestamp": datetime.now().isoformat()
            }

    async def quick_analysis(self, symbol: str) -> Dict[str, Any]:
        """快速技术分析"""
        content = f"""
        请对股票 {symbol} 进行快速技术分析：

        分析要点：
        1. 当前技术指标状况 (MACD, KDJ, RSI等)
        2. 短期走势判断 (1-4周)
        3. 关键技术价位 (支撑位、阻力位、目标价)
        4. 简单操作建议 (买入/持有/卖出)
        5. 置信度评估 (0-1)

        请以JSON格式返回分析结果，包含以下字段：
        - technical_score: 技术评分 (0-10)
        - signal: 投资信号 ("买入", "持有", "卖出")
        - key_levels: 关键价位 (support, resistance, target)
        - recommendation: 操作建议
        - reasoning: 分析理由
        - time_horizon: 时间范围
        - confidence: 置信度 (0-1)
        """

        result = await self.analyze_with_expert_role(
            content,
            "technical",
            "你是技术面分析师，请提供专业的技术分析。",
            "json"
        )

        return result

    async def full_expert_analysis(self, symbol: str) -> Dict[str, Any]:
        """完整专家圆桌分析"""

        # 四个专家的分析任务
        analysis_tasks = [
            ("技术面分析师", "technical", f"请对股票 {symbol} 进行全面的技术分析，包括趋势、支撑阻力位、技术指标等"),
            ("基本面分析师", "fundamental", f"请对股票 {symbol} 进行基本面分析，包括财务状况、估值水平、行业地位等"),
            ("新闻分析师", "news", f"请分析股票 {symbol} 相关的新闻舆情和市场情绪影响"),
            ("风控分析师", "risk", f"请评估股票 {symbol} 的投资风险，包括市场风险、流动性风险、波动性等")
        ]

        expert_opinions = []

        # 并行执行专家分析
        tasks = []
        for expert_name, expert_type, prompt in analysis_tasks:
            task = self.analyze_with_expert_role(
                prompt + "\n请提供详细的分析结果。",
                expert_type,
                f"你是{expert_name}，请提供专业的分析。",
                "json"
            )
            tasks.append(task)

        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    expert_opinions.append({
                        "expert_type": analysis_tasks[i][1],
                        "expert_name": analysis_tasks[i][0],
                        "error": str(result),
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    expert_opinions.append({
                        "expert_type": analysis_tasks[i][1],
                        "expert_name": analysis_tasks[i][0],
                        "analysis": result,
                        "timestamp": datetime.now().isoformat()
                    })

            # 生成综合建议
            consolidated_analysis = await self._generate_consolidated_analysis(symbol, expert_opinions)

            return {
                "symbol": symbol,
                "meeting_timestamp": datetime.now().isoformat(),
                "expert_opinions": expert_opinions,
                "consolidated_analysis": consolidated_analysis,
                "meeting_status": "completed"
            }

        except Exception as e:
            return {
                "symbol": symbol,
                "error": f"专家圆桌分析失败: {str(e)}",
                "meeting_status": "failed"
            }

    async def _generate_consolidated_analysis(self, symbol: str, expert_opinions: list) -> Dict[str, Any]:
        """生成综合分析"""

        # 汇总专家意见
        valid_opinions = [op for op in expert_opinions if "error" not in op]

        if not valid_opinions:
            return {
                "summary": "无法获取有效专家意见",
                "recommendation": "建议重新分析",
                "confidence": 0.0,
                "risk_level": "未知"
            }

        # 简单的共识算法
        positive_signals = 0
        negative_signals = 0
        total_confidence = 0

        for opinion in valid_opinions:
            analysis = opinion.get("analysis", {})
            if isinstance(analysis, dict):
                signal = analysis.get("signal", "持有")
                confidence = analysis.get("confidence", 0.5)

                if signal in ["买入", "强烈买入"]:
                    positive_signals += 1
                elif signal in ["卖出", "强烈卖出"]:
                    negative_signals += 1

                total_confidence += confidence

        # 生成最终建议
        avg_confidence = total_confidence / len(valid_opinions) if valid_opinions else 0

        if positive_signals > negative_signals:
            recommendation = "买入"
            risk_level = "中等"
        elif negative_signals > positive_signals:
            recommendation = "卖出"
            risk_level = "高"
        else:
            recommendation = "持有"
            risk_level = "中等"

        return {
            "summary": f"基于{len(valid_opinions)}位专家的分析，建议{recommendation}",
            "recommendation": recommendation,
            "confidence": min(avg_confidence, 1.0),
            "risk_level": risk_level,
            "expert_count": len(valid_opinions),
            "positive_signals": positive_signals,
            "negative_signals": negative_signals
        }


# 创建全局实例
glm_analyzer = GLMAnalyzer()

# 导出便捷函数
async def get_expert_analysis(expert_type: str, content: str) -> Dict[str, Any]:
    """获取专家分析"""
    return await glm_analyzer.analyze_with_expert_role(
        content,
        expert_type,
        f"你是{expert_type}分析师，请提供专业分析。",
        "json"
    )