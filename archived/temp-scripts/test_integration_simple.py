#!/usr/bin/env python3
"""
智股通AI增强轻量化版集成测试脚本
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_integration():
    """运行集成测试"""
    base_url = "http://localhost:8001"
    frontend_url = "http://localhost:10001"

    print("=" * 60)
    print("智股通AI增强轻量化版集成测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"后端地址: {base_url}")
    print(f"前端地址: {frontend_url}")
    print("-" * 60)

    results = []

    # 1. 测试后端健康状态
    print("\n测试后端健康状态...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ 后端健康检查: {data['status']}")
                    print(f"   GLM AI: {data['services']['glm_ai']}")
                    print(f"   数据服务: {data['services']['data_service']}")
                    print(f"   专家系统: {data['services']['expert_roundtable']}")
                    results.append("后端健康检查: 通过")
                else:
                    print(f"❌ 后端健康检查失败: {response.status}")
                    results.append("后端健康检查: 失败")
    except Exception as e:
        print(f"❌ 后端连接失败: {e}")
        results.append("后端健康检查: 失败")

    # 2. 测试前端访问
    print("\n测试前端界面访问...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(frontend_url) as response:
                if response.status == 200:
                    content = await response.text()
                    if "智股通" in content:
                        print("✅ 前端界面正常加载")
                        results.append("前端界面访问: 通过")
                    else:
                        print("❌ 前端内容不完整")
                        results.append("前端界面访问: 失败")
                else:
                    print(f"❌ 前端访问失败: {response.status}")
                    results.append("前端界面访问: 失败")
    except Exception as e:
        print(f"❌ 前端连接失败: {e}")
        results.append("前端界面访问: 失败")

    # 3. 测试专家列表
    print("\n测试专家列表获取...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/api/expert-roundtable/experts") as response:
                if response.status == 200:
                    data = await response.json()
                    experts = data.get("experts", [])
                    if len(experts) == 4:
                        print("✅ 专家列表获取成功")
                        for expert in experts:
                            print(f"   - {expert['name']}")
                        results.append("专家列表获取: 通过")
                    else:
                        print(f"❌ 专家数量不正确: {len(experts)}")
                        results.append("专家列表获取: 失败")
                else:
                    print(f"❌ 专家列表获取失败: {response.status}")
                    results.append("专家列表获取: 失败")
    except Exception as e:
        print(f"❌ 专家列表测试失败: {e}")
        results.append("专家列表获取: 失败")

    # 4. 测试股票信息
    print("\n测试股票信息获取...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/api/stock/000001/info") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        stock = data["data"]
                        print("✅ 股票信息获取成功")
                        print(f"   - 股票名称: {stock['name']}")
                        print(f"   - 当前价格: ¥{stock['current_price']}")
                        print(f"   - 涨跌幅: {stock['change_percent']:.2f}%")
                        results.append("股票信息获取: 通过")
                    else:
                        print(f"❌ 股票信息获取失败: {data.get('message')}")
                        results.append("股票信息获取: 失败")
                else:
                    print(f"❌ 股票信息请求失败: {response.status}")
                    results.append("股票信息获取: 失败")
    except Exception as e:
        print(f"❌ 股票信息测试失败: {e}")
        results.append("股票信息获取: 失败")

    # 5. 测试专家快速分析
    print("\n测试专家快速分析...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{base_url}/api/expert-roundtable/quick-analysis?symbol=000001") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        analysis = data["analysis"]
                        print("✅ 专家快速分析成功")
                        print(f"   - 专家类型: {data['expert_type']}")
                        print(f"   - 技术评分: {analysis['technical_score']}/10")
                        print(f"   - 投资信号: {analysis['signal']}")
                        print(f"   - 置信度: {analysis['confidence']*100:.1f}%")
                        results.append("专家快速分析: 通过")
                    else:
                        print(f"❌ 快速分析失败: {data.get('message')}")
                        results.append("专家快速分析: 失败")
                else:
                    print(f"❌ 快速分析请求失败: {response.status}")
                    results.append("专家快速分析: 失败")
    except Exception as e:
        print(f"❌ 快速分析测试失败: {e}")
        results.append("专家快速分析: 失败")

    # 输出测试结果总结
    print("\n" + "=" * 60)
    print("测试结果总结")
    print("=" * 60)

    total_tests = len(results)
    passed_tests = sum(1 for r in results if "通过" in r)

    for result in results:
        status = "✅" if "通过" in result else "❌"
        print(f"{status} {result}")

    print(f"\n总体结果: {passed_tests}/{total_tests} 测试通过")

    if passed_tests == total_tests:
        print("🎉 所有功能测试通过！智股通AI增强轻量化版运行正常！")
    elif passed_tests >= total_tests * 0.8:
        print("✅ 大部分功能正常，系统基本可用")
    else:
        print("⚠️ 部分功能存在问题，建议检查配置")

    print("\n访问地址:")
    print(f"   前端界面: {frontend_url}")
    print(f"   后端API文档: {base_url}/docs")

    return passed_tests, total_tests

if __name__ == "__main__":
    asyncio.run(test_integration())