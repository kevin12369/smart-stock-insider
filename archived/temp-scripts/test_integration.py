#!/usr/bin/env python3
"""
智股通AI增强轻量化版集成测试脚本

测试所有核心功能：
1. 后端API服务
2. GLM-4.5-Flash AI分析
3. 专家圆桌会议系统
4. 股票数据服务
5. 前端界面访问
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, Any

class APIIntegrationTester:
    def __init__(self):
        self.base_url = "http://localhost:8001"
        self.frontend_url = "http://localhost:10001"
        self.results = {
            "backend": False,
            "frontend": False,
            "glm_ai": False,
            "stock_data": False,
            "expert_system": False,
            "quick_analysis": False
        }

    async def test_backend_health(self) -> bool:
        """测试后端健康状态"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ 后端健康检查: {data['status']}")
                        print(f"   - GLM AI: {data['services']['glm_ai']}")
                        print(f"   - 数据服务: {data['services']['data_service']}")
                        print(f"   - 专家系统: {data['services']['expert_roundtable']}")

                        # 更新结果状态
                        self.results["backend"] = True
                        if data["services"]["glm_ai"] == "healthy":
                            self.results["glm_ai"] = True
                        if data["services"]["data_service"] == "available":
                            self.results["stock_data"] = True
                        if data["services"]["expert_roundtable"] == "available":
                            self.results["expert_system"] = True

                        return True
                    else:
                        print(f"❌ 后端健康检查失败: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ 后端连接失败: {e}")
            return False

    async def test_frontend_access(self) -> bool:
        """测试前端访问"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.frontend_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        if "智股通" in content and "智能投资研究平台" in content:
                            print("✅ 前端界面正常加载")
                            self.results["frontend"] = True
                            return True
                        else:
                            print("❌ 前端内容不完整")
                            return False
                    else:
                        print(f"❌ 前端访问失败: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ 前端连接失败: {e}")
            return False

    async def test_expert_list(self) -> bool:
        """测试专家列表获取"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/expert-roundtable/experts") as response:
                    if response.status == 200:
                        data = await response.json()
                        experts = data.get("experts", [])
                        if len(experts) == 4:
                            print("✅ 专家列表获取成功")
                            for expert in experts:
                                print(f"   - {expert['name']}: {expert['description'][:30]}...")
                            return True
                        else:
                            print(f"❌ 专家数量不正确: {len(experts)}")
                            return False
                    else:
                        print(f"❌ 专家列表获取失败: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ 专家列表测试失败: {e}")
            return False

    async def test_stock_info(self) -> bool:
        """测试股票信息获取"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/stock/000001/info") as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("success"):
                            stock = data["data"]
                            print("✅ 股票信息获取成功")
                            print(f"   - 股票名称: {stock['name']}")
                            print(f"   - 当前价格: ¥{stock['current_price']}")
                            print(f"   - 涨跌幅: {stock['change_percent']:.2f}%")
                            return True
                        else:
                            print(f"❌ 股票信息获取失败: {data.get('message')}")
                            return False
                    else:
                        print(f"❌ 股票信息请求失败: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ 股票信息测试失败: {e}")
            return False

    async def test_quick_analysis(self) -> bool:
        """测试专家快速分析"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/api/expert-roundtable/quick-analysis?symbol=000001") as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("success"):
                            analysis = data["analysis"]
                            print("✅ 专家快速分析成功")
                            print(f"   - 专家类型: {data['expert_type']}")
                            print(f"   - 技术评分: {analysis['technical_score']}/10")
                            print(f"   - 投资信号: {analysis['signal']}")
                            print(f"   - 置信度: {analysis['confidence']*100:.1f}%")
                            print(f"   - 分析摘要: {analysis['reasoning'][:50]}...")
                            self.results["quick_analysis"] = True
                            return True
                        else:
                            print(f"❌ 快速分析失败: {data.get('message')}")
                            return False
                    else:
                        print(f"❌ 快速分析请求失败: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ 快速分析测试失败: {e}")
            return False

    async def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("🧪 智股通AI增强轻量化版集成测试")
        print("=" * 60)
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"后端地址: {self.base_url}")
        print(f"前端地址: {self.frontend_url}")
        print("-" * 60)

        # 运行测试
        tests = [
            ("后端健康检查", self.test_backend_health),
            ("前端界面访问", self.test_frontend_access),
            ("专家列表获取", self.test_expert_list),
            ("股票信息获取", self.test_stock_info),
            ("专家快速分析", self.test_quick_analysis),
        ]

        for test_name, test_func in tests:
            print(f"\n🔍 测试: {test_name}")
            try:
                await test_func()
            except Exception as e:
                print(f"❌ 测试异常: {e}")

        # 输出测试结果总结
        print("\n" + "=" * 60)
        print("📊 测试结果总结")
        print("=" * 60)

        total_tests = len(self.results)
        passed_tests = sum(self.results.values())

        for test_name, result in self.results.items():
            status = "✅ 通过" if result else "❌ 失败"
            test_display_name = {
                "backend": "后端服务",
                "frontend": "前端界面",
                "glm_ai": "GLM-4.5-Flash AI",
                "stock_data": "股票数据服务",
                "expert_system": "专家圆桌系统",
                "quick_analysis": "专家快速分析"
            }.get(test_name, test_name)
            print(f"{test_display_name}: {status}")

        print(f"\n🎯 总体结果: {passed_tests}/{total_tests} 测试通过")

        if passed_tests == total_tests:
            print("🎉 所有功能测试通过！智股通AI增强轻量化版运行正常！")
        elif passed_tests >= total_tests * 0.8:
            print("✅ 大部分功能正常，系统基本可用")
        else:
            print("⚠️ 部分功能存在问题，建议检查配置")

        print("\n📱 访问地址:")
        print(f"   前端界面: {self.frontend_url}")
        print(f"   后端API文档: {self.base_url}/docs")

async def main():
    """主函数"""
    tester = APIIntegrationTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())