"""
投资组合API单元测试
"""

import pytest
import asyncio
import json
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 创建FastAPI应用
from fastapi import FastAPI
from backend.api.portfolio import router as portfolio_router

app = FastAPI()
app.include_router(portfolio_router)

client = TestClient(app)

@pytest.fixture
def mock_portfolio_optimizer():
    """模拟投资组合优化器"""
    with patch('backend.api.portfolio.portfolio_optimizer') as mock_optimizer:
        # 模拟优化结果
        mock_optimization_result = Mock(
            weights={"AAPL": 0.4, "MSFT": 0.3, "GOOGL": 0.2, "JPM": 0.1},
            expected_return=0.112,
            expected_volatility=0.165,
            sharpe_ratio=0.55,
            method="markowitz",
            optimization_time=0.25,
            constraints_met=True,
            risk_contributions={"AAPL": 0.045, "MSFT": 0.034, "GOOGL": 0.028, "JPM": 0.012},
            timestamp=datetime.now(),
            metadata={"iterations": 150}
        )

        mock_optimizer.optimize_portfolio = AsyncMock(return_value=mock_optimization_result)

        # 模拟风险分析结果
        mock_risk_analysis = Mock(
            var_95=0.025,
            var_99=0.035,
            cvar_95=0.032,
            cvar_99=0.045,
            confidence_levels=[0.95, 0.99],
            time_horizon=1,
            calculation_method="historical_simulation",
            scenarios=[
                {"scenario": "market_crash", "impact": -0.15, "probability": 0.02},
                {"scenario": "policy_change", "impact": 0.08, "probability": 0.05}
            ]
        )

        mock_optimizer.analyze_portfolio_risk = AsyncMock(return_value=mock_risk_analysis)

        # 模拟有效前沿计算
        mock_efficient_frontier = Mock(
            points=[
                {"return": 0.08, "volatility": 0.12, "sharpe_ratio": 0.42},
                {"return": 0.10, "volatility": 0.15, "sharpe_ratio": 0.47},
                {"return": 0.12, "volatility": 0.18, "sharpe_ratio": 0.50},
                {"return": 0.14, "volatility": 0.22, "sharpe_ratio": 0.50}
            ],
            optimal_portfolio={"return": 0.12, "volatility": 0.18, "sharpe_ratio": 0.50},
            calculation_time=1.2
        )

        mock_optimizer.calculate_efficient_frontier = AsyncMock(return_value=mock_efficient_frontier)

        # 模拟再平衡建议
        mock_rebalancing = Mock(
            current_weights={"AAPL": 0.5, "MSFT": 0.3, "GOOGL": 0.2},
            target_weights={"AAPL": 0.4, "MSFT": 0.35, "GOOGL": 0.25},
            rebalancing_actions=[
                {"asset": "AAPL", "action": "sell", "amount": 0.1},
                {"asset": "MSFT", "action": "buy", "amount": 0.05},
                {"asset": "GOOGL", "action": "buy", "amount": 0.05}
            ],
            transaction_costs=0.0025,
            tracking_error=0.001
        )

        mock_optimizer.calculate_rebalancing = AsyncMock(return_value=mock_rebalancing)

        # 模拟方法列表
        mock_optimizer.get_optimization_methods = Mock(return_value=[
            {"method": "markowitz", "name": "马科维茨均值-方差优化", "description": "现代投资组合理论经典方法"},
            {"method": "minimum_variance", "name": "最小方差优化", "description": "最小化投资组合风险"},
            {"method": "maximum_sharpe", "name": "最大夏普比率优化", "description": "最大化风险调整收益"},
            {"method": "risk_parity", "name": "风险平价", "description": "等风险贡献投资组合"},
            {"method": "equal_weight", "name": "等权重", "description": "简单等权重分配"},
            {"method": "black_litterman", "name": "Black-Litterman", "description": "结合投资者观点的均衡收益模型"}
        ])

        yield mock_optimizer

@pytest.fixture
def sample_assets():
    """示例资产数据"""
    return [
        {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "expected_return": 0.12,
            "volatility": 0.22,
            "category": "technology",
            "market_cap": 2800000000000
        },
        {
            "symbol": "MSFT",
            "name": "Microsoft Corporation",
            "expected_return": 0.10,
            "volatility": 0.18,
            "category": "technology",
            "market_cap": 2500000000000
        },
        {
            "symbol": "GOOGL",
            "name": "Alphabet Inc.",
            "expected_return": 0.11,
            "volatility": 0.20,
            "category": "technology",
            "market_cap": 1800000000000
        },
        {
            "symbol": "JPM",
            "name": "JPMorgan Chase & Co.",
            "expected_return": 0.08,
            "volatility": 0.15,
            "category": "finance",
            "market_cap": 400000000000
        }
    ]

@pytest.fixture
def sample_optimization_request():
    """示例优化请求"""
    return {
        "assets": [
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "expected_return": 0.12,
                "volatility": 0.22,
                "category": "technology"
            },
            {
                "symbol": "MSFT",
                "name": "Microsoft Corporation",
                "expected_return": 0.10,
                "volatility": 0.18,
                "category": "technology"
            }
        ],
        "method": "markowitz",
        "constraints": {
            "min_weight": 0.0,
            "max_weight": 0.5,
            "target_return": None,
            "target_volatility": None
        }
    }

@pytest.fixture
def sample_risk_request():
    """示例风险分析请求"""
    return {
        "weights": {"AAPL": 0.4, "MSFT": 0.3, "GOOGL": 0.2, "JPM": 0.1},
        "confidence_levels": [0.95, 0.99],
        "time_horizon": 1,
        "method": "historical_simulation"
    }

@pytest.fixture
def sample_rebalancing_request():
    """示例再平衡请求"""
    return {
        "current_weights": {"AAPL": 0.5, "MSFT": 0.3, "GOOGL": 0.15, "JPM": 0.05},
        "target_weights": {"AAPL": 0.4, "MSFT": 0.35, "GOOGL": 0.2, "JPM": 0.05},
        "constraints": {
            "max_transaction_cost": 0.01,
            "min_trade_size": 0.01
        }
    }

class TestPortfolioAPI:
    """投资组合API测试类"""

    def test_optimize_portfolio_success(self, mock_portfolio_optimizer, sample_optimization_request):
        """测试成功优化投资组合"""
        response = client.post("/api/portfolio/optimize", json=sample_optimization_request)

        assert response.status_code == 200
        data = response.json()

        assert "weights" in data
        assert "expected_return" in data
        assert "expected_volatility" in data
        assert "sharpe_ratio" in data
        assert "method" in data
        assert "optimization_time" in data
        assert "constraints_met" in data
        assert "risk_contributions" in data
        assert "timestamp" in data

        # 验证优化结果
        assert len(data["weights"]) == len(sample_optimization_request["assets"])
        assert data["expected_return"] == 0.112
        assert data["method"] == "markowitz"
        assert data["constraints_met"] is True

        # 验证权重约束
        total_weight = sum(data["weights"].values())
        assert abs(total_weight - 1.0) < 1e-6

        # 验证服务调用
        mock_portfolio_optimizer.optimize_portfolio.assert_called_once()

    def test_optimize_portfolio_invalid_request(self):
        """测试无效的优化请求"""
        invalid_requests = [
            {},  # 空请求
            {"assets": []},  # 空资产列表
            {"assets": [{"symbol": "AAPL"}]},  # 资产信息不完整
            {"assets": sample_assets(), "method": "invalid_method"},  # 无效方法
            {"assets": sample_assets(), "method": "markowitz", "constraints": "invalid"}  # 无效约束
        ]

        for invalid_request in invalid_requests:
            response = client.post("/api/portfolio/optimize", json=invalid_request)
            assert response.status_code == 422

    def test_optimize_portfolio_different_methods(self, mock_portfolio_optimizer, sample_assets):
        """测试不同的优化方法"""
        methods = ["markowitz", "minimum_variance", "maximum_sharpe", "risk_parity", "equal_weight"]

        for method in methods:
            request = {
                "assets": sample_assets,
                "method": method,
                "constraints": {"min_weight": 0.0, "max_weight": 0.5}
            }

            response = client.post("/api/portfolio/optimize", json=request)

            assert response.status_code == 200
            data = response.json()
            assert data["method"] == method

    def test_optimize_portfolio_with_constraints(self, mock_portfolio_optimizer, sample_assets):
        """测试带约束的优化"""
        constraints = {
            "min_weight": 0.05,
            "max_weight": 0.4,
            "sector_limits": {
                "technology": 0.7,
                "finance": 0.3
            },
            "target_return": 0.10
        }

        request = {
            "assets": sample_assets,
            "method": "markowitz",
            "constraints": constraints
        }

        response = client.post("/api/portfolio/optimize", json=request)

        assert response.status_code == 200
        data = response.json()

        # 验证约束满足
        for weight in data["weights"].values():
            assert constraints["min_weight"] <= weight <= constraints["max_weight"]

    def test_analyze_risk_success(self, mock_portfolio_optimizer, sample_risk_request):
        """测试成功分析风险"""
        response = client.post("/api/portfolio/risk/analyze", json=sample_risk_request)

        assert response.status_code == 200
        data = response.json()

        assert "var_95" in data
        assert "var_99" in data
        assert "cvar_95" in data
        assert "cvar_99" in data
        assert "confidence_levels" in data
        assert "time_horizon" in data
        assert "calculation_method" in data
        assert "scenarios" in data

        # 验证风险指标
        assert data["var_95"] == 0.025
        assert data["var_99"] == 0.035
        assert data["cvar_95"] == 0.032
        assert data["cvar_99"] == 0.045

        # 验证服务调用
        mock_portfolio_optimizer.analyze_portfolio_risk.assert_called_once()

    def test_analyze_risk_invalid_request(self):
        """测试无效的风险分析请求"""
        invalid_requests = [
            {},  # 空请求
            {"weights": {}},  # 空权重
            {"weights": {"AAPL": 1.5}},  # 权重和不等于1
            {"weights": {"AAPL": 0.5, "MSFT": 0.6}},  # 权重和大于1
            {"weights": {"AAPL": -0.1}},  # 负权重
            {"weights": sample_weights(), "confidence_levels": [1.1]},  # 无效置信水平
            {"weights": sample_weights(), "time_horizon": -1}  # 无效时间范围
        ]

        for invalid_request in invalid_requests:
            response = client.post("/api/portfolio/risk/analyze", json=invalid_request)
            assert response.status_code == 422

    def test_analyze_risk_var_calculation(self, mock_portfolio_optimizer):
        """测试VaR计算"""
        var_request = {
            "weights": {"AAPL": 0.4, "MSFT": 0.3, "GOOGL": 0.3},
            "confidence_level": 0.95,
            "time_horizon": 1,
            "method": "historical_simulation"
        }

        mock_portfolio_optimizer.calculate_var = AsyncMock(return_value={
            "var": 0.025,
            "confidence_level": 0.95,
            "time_horizon": 1,
            "method": "historical_simulation",
            "calculation_time": 0.15
        })

        response = client.post("/api/portfolio/risk/var", json=var_request)

        assert response.status_code == 200
        data = response.json()

        assert "var" in data
        assert "confidence_level" in data
        assert "time_horizon" in data
        assert "method" in data

        assert data["var"] == 0.025

    def test_analyze_risk_cvar_calculation(self, mock_portfolio_optimizer):
        """测试CVaR计算"""
        cvar_request = {
            "weights": {"AAPL": 0.4, "MSFT": 0.3, "GOOGL": 0.3},
            "confidence_level": 0.95,
            "time_horizon": 1,
            "method": "historical_simulation"
        }

        mock_portfolio_optimizer.calculate_cvar = AsyncMock(return_value={
            "cvar": 0.032,
            "confidence_level": 0.95,
            "time_horizon": 1,
            "method": "historical_simulation",
            "calculation_time": 0.18
        })

        response = client.post("/api/portfolio/risk/cvar", json=cvar_request)

        assert response.status_code == 200
        data = response.json()

        assert "cvar" in data
        assert "confidence_level" in data
        assert "time_horizon" in data
        assert "method" in data

        assert data["cvar"] == 0.032

    def test_analyze_risk_stress_test(self, mock_portfolio_optimizer):
        """测试压力测试"""
        stress_request = {
            "weights": {"AAPL": 0.4, "MSFT": 0.3, "GOOGL": 0.3},
            "scenarios": [
                {"name": "market_crash", "impact": -0.2},
                {"name": "interest_rate_hike", "impact": 0.1},
                {"name": "inflation_spike", "impact": -0.15}
            ],
            "num_simulations": 10000
        }

        mock_portfolio_optimizer.stress_test = AsyncMock(return_value={
            "scenarios": [
                {"name": "market_crash", "impact": -0.18, "probability": 0.02},
                {"name": "interest_rate_hike", "impact": 0.08, "probability": 0.05},
                {"name": "inflation_spike", "impact": -0.12, "probability": 0.03}
            ],
            "worst_case": {
                "scenario": "market_crash",
                "impact": -0.18,
                "confidence": 0.95
            },
            "var": 0.028,
            "cvar": 0.035,
            "simulation_time": 2.5
        })

        response = client.post("/api/portfolio/risk/stress-test", json=stress_request)

        assert response.status_code == 200
        data = response.json()

        assert "scenarios" in data
        assert "worst_case" in data
        assert "var" in data
        assert "cvar" in data
        assert "simulation_time" in data

        assert len(data["scenarios"]) == 3
        assert data["worst_case"]["scenario"] == "market_crash"

    def test_calculate_efficient_frontier_success(self, mock_portfolio_optimizer, sample_assets):
        """测试成功计算有效前沿"""
        frontier_request = {
            "assets": sample_assets,
            "num_portfolios": 20,
            "risk_free_rate": 0.03,
            "target_returns": None
        }

        response = client.post("/api/portfolio/efficient-frontier", json=frontier_request)

        assert response.status_code == 200
        data = response.json()

        assert "points" in data
        assert "optimal_portfolio" in data
        assert "calculation_time" in data

        assert len(data["points"]) == 20
        assert "return" in data["optimal_portfolio"]
        assert "volatility" in data["optimal_portfolio"]
        assert "sharpe_ratio" in data["optimal_portfolio"]

    def test_calculate_efficient_frontier_with_targets(self, mock_portfolio_optimizer, sample_assets):
        """测试带目标收益的有效前沿计算"""
        frontier_request = {
            "assets": sample_assets,
            "target_returns": [0.08, 0.10, 0.12, 0.14],
            "num_portfolios": 50
        }

        response = client.post("/api/portfolio/efficient-frontier", json=frontier_request)

        assert response.status_code == 200
        data = response.json()

        assert len(data["points"]) >= len(frontier_request["target_returns"])

    def test_calculate_rebalancing_success(self, mock_portfolio_optimizer, sample_rebalancing_request):
        """测试成功计算再平衡"""
        response = client.post("/api/portfolio/rebalance", json=sample_rebalancing_request)

        assert response.status_code == 200
        data = response.json()

        assert "current_weights" in data
        assert "target_weights" in data
        assert "rebalancing_actions" in data
        assert "transaction_costs" in data
        assert "tracking_error" in data

        # 验证再平衡动作
        assert len(data["rebalancing_actions"]) >= 1

        for action in data["rebalancing_actions"]:
            assert "asset" in action
            assert "action" in action  # buy/sell/hold
            assert "amount" in action

    def test_calculate_rebalancing_invalid_request(self):
        """测试无效的再平衡请求"""
        invalid_requests = [
            {},  # 空请求
            {"current_weights": {}},  # 空当前权重
            {"current_weights": {"AAPL": 0.5}, "target_weights": {}},  # 空目标权重
            {"current_weights": {"AAPL": 1.2}, "target_weights": {"MSFT": 0.8}},  # 权重和不等于1
            {"current_weights": {"AAPL": -0.1}, "target_weights": {"MSFT": 1.1}}  # 负权重
        ]

        for invalid_request in invalid_requests:
            response = client.post("/api/portfolio/rebalance", json=invalid_request)
            assert response.status_code == 422

    def test_get_optimization_methods_success(self, mock_portfolio_optimizer):
        """测试成功获取优化方法列表"""
        response = client.get("/api/portfolio/methods")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) >= 6  # 至少包含6种方法

        for method in data:
            assert "method" in method
            assert "name" in method
            assert "description" in method

        # 验证包含主要方法
        method_names = [method["method"] for method in data]
        assert "markowitz" in method_names
        assert "minimum_variance" in method_names
        assert "maximum_sharpe" in method_names

    def test_get_optimization_methods_error(self, mock_portfolio_optimizer):
        """测试获取优化方法列表错误"""
        mock_portfolio_optimizer.get_optimization_methods.side_effect = Exception("Service error")

        response = client.get("/api/portfolio/methods")

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data

    def test_error_handling_500(self):
        """测试500错误处理"""
        with patch('backend.api.portfolio.portfolio_optimizer') as mock_optimizer:
            mock_optimizer.optimize_portfolio.side_effect = Exception("Internal error")

            response = client.post("/api/portfolio/optimize", json={
                "assets": [{"symbol": "AAPL", "expected_return": 0.12, "volatility": 0.22}],
                "method": "markowitz"
            })

            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "投资组合优化失败" in data["detail"]

    def test_validation_errors(self):
        """测试验证错误"""
        validation_errors = [
            # 资产数据验证错误
            {
                "request": {
                    "assets": [
                        {"symbol": "", "expected_return": 0.12, "volatility": 0.22}  # 空symbol
                    ],
                    "method": "markowitz"
                },
                "expected_field": "symbol"
            },
            # 数值验证错误
            {
                "request": {
                    "assets": [
                        {"symbol": "AAPL", "expected_return": "invalid", "volatility": 0.22}  # 无效预期收益
                    ],
                    "method": "markowitz"
                },
                "expected_field": "expected_return"
            },
            # 范围验证错误
            {
                "request": {
                    "assets": [
                        {"symbol": "AAPL", "expected_return": 0.12, "volatility": 1.5}  # 波动率过大
                    ],
                    "method": "markowitz"
                },
                "expected_field": "volatility"
            }
        ]

        for test_case in validation_errors:
            response = client.post("/api/portfolio/optimize", json=test_case["request"])
            assert response.status_code == 422

    def test_concurrent_optimizations(self, mock_portfolio_optimizer):
        """测试并发优化"""
        import threading
        import time

        results = []
        errors = []

        def optimize_portfolio():
            try:
                response = client.post("/api/portfolio/optimize", json={
                    "assets": [
                        {"symbol": f"STOCK_{threading.current_thread().ident}",
                         "expected_return": 0.10, "volatility": 0.20}
                    ],
                    "method": "markowitz"
                })
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))

        # 创建多个并发线程
        threads = []
        for i in range(5):
            thread = threading.Thread(target=optimize_portfolio)
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证结果
        assert len(errors) == 0, f"并发优化出现错误: {errors}"
        assert len(results) == 5
        assert all(status in [200, 422, 500] for status in results)

    def test_large_portfolio_optimization(self, mock_portfolio_optimizer):
        """测试大规模投资组合优化"""
        # 创建大规模资产数据
        large_assets = [
            {"symbol": f"STOCK_{i:03d}", "expected_return": 0.05 + i * 0.001, "volatility": 0.15 + i * 0.002}
            for i in range(100)
        ]

        request = {
            "assets": large_assets,
            "method": "equal_weight"  # 使用等权重避免复杂计算
        }

        # 模拟大规模优化的处理
        mock_large_result = Mock(
            weights={f"STOCK_{i:03d}": 0.01 for i in range(100)},
            expected_return=0.10,
            expected_volatility=0.16,
            sharpe_ratio=0.44,
            method="equal_weight",
            optimization_time=2.5,
            constraints_met=True,
            risk_contributions={f"STOCK_{i:03d}": 0.0016 for i in range(100)},
            timestamp=datetime.now(),
            metadata={"asset_count": 100}
        )

        mock_portfolio_optimizer.optimize_portfolio = AsyncMock(return_value=mock_large_result)

        response = client.post("/api/portfolio/optimize", json=request)

        assert response.status_code == 200
        data = response.json()

        # 验证大规模结果
        assert len(data["weights"]) == 100
        assert data["optimization_time"] == 2.5

@pytest.mark.unit
@pytest.mark.api
@pytest.mark.portfolio
class TestPortfolioAPIIntegration:
    """投资组合API集成测试"""

    def test_complete_portfolio_optimization_workflow(self, mock_portfolio_optimizer):
        """测试完整的投资组合优化工作流程"""
        # 1. 获取可用优化方法
        methods_response = client.get("/api/portfolio/methods")
        assert methods_response.status_code == 200

        # 2. 优化投资组合
        optimize_request = {
            "assets": [
                {"symbol": "AAPL", "name": "Apple", "expected_return": 0.12, "volatility": 0.22, "category": "technology"},
                {"symbol": "MSFT", "name": "Microsoft", "expected_return": 0.10, "volatility": 0.18, "category": "technology"}
            ],
            "method": "markowitz",
            "constraints": {"min_weight": 0.0, "max_weight": 0.6}
        }

        optimize_response = client.post("/api/portfolio/optimize", json=optimize_request)
        assert optimize_response.status_code == 200
        optimize_data = optimize_response.json()

        # 3. 分析投资组合风险
        risk_response = client.post("/api/portfolio/risk/analyze", json={
            "weights": optimize_data["weights"],
            "confidence_levels": [0.95, 0.99],
            "time_horizon": 1
        })
        assert risk_response.status_code == 200

        # 4. 计算有效前沿
        frontier_response = client.post("/api/portfolio/efficient-frontier", json={
            "assets": optimize_request["assets"],
            "num_portfolios": 20
        })
        assert frontier_response.status_code == 200

        # 5. 计算再平衡建议
        rebalancing_response = client.post("/api/portfolio/rebalance", json={
            "current_weights": optimize_data["weights"],
            "target_weights": {"AAPL": 0.45, "MSFT": 0.55}
        })
        assert rebalancing_response.status_code == 200

    def test_multi_objective_optimization(self, mock_portfolio_optimizer):
        """测试多目标优化"""
        # 模拟不同目标下的优化结果
        scenarios = [
            {
                "name": "保守型",
                "constraints": {"max_volatility": 0.15, "min_return": 0.05}
            },
            {
                "name": "平衡型",
                "constraints": {"target_return": 0.10, "max_volatility": 0.20}
            },
            {
                "name": "激进型",
                "constraints": {"target_return": 0.15, "min_volatility": 0.10}
            }
        ]

        optimization_results = []

        for scenario in scenarios:
            request = {
                "assets": [
                    {"symbol": "AAPL", "expected_return": 0.12, "volatility": 0.22},
                    {"symbol": "MSFT", "expected_return": 0.10, "volatility": 0.18}
                ],
                "method": "markowitz",
                "constraints": scenario["constraints"]
            }

            # 模拟不同的优化结果
            if scenario["name"] == "保守型":
                mock_result = Mock(
                    weights={"AAPL": 0.3, "MSFT": 0.7},
                    expected_return=0.085,
                    expected_volatility=0.14,
                    sharpe_ratio=0.40
                )
            elif scenario["name"] == "平衡型":
                mock_result = Mock(
                    weights={"AAPL": 0.6, "MSFT": 0.4},
                    expected_return=0.112,
                    expected_volatility=0.20,
                    sharpe_ratio=0.41
                )
            else:  # 激进型
                mock_result = Mock(
                    weights={"AAPL": 0.8, "MSFT": 0.2},
                    expected_return=0.135,
                    expected_volatility": 0.25,
                    sharpe_ratio=0.42
                )

            mock_portfolio_optimizer.optimize_portfolio = AsyncMock(return_value=mock_result)

            response = client.post("/api/portfolio/optimize", json=request)
            assert response.status_code == 200

            result_data = response.json()
            optimization_results.append({
                "scenario": scenario["name"],
                "result": result_data
            })

        # 验证不同场景的结果差异
        assert len(optimization_results) == 3
        conservative = optimization_results[0]["result"]
        aggressive = optimization_results[2]["result"]

        assert conservative["expected_volatility"] < aggressive["expected_volatility"]
        assert aggressive["expected_return"] > conservative["expected_return"]

    def test_risk_management_workflow(self, mock_portfolio_optimizer):
        """测试风险管理完整工作流程"""
        # 1. 创建投资组合
        portfolio_weights = {"AAPL": 0.4, "MSFT": 0.3, "GOOGL": 0.2, "JPM": 0.1}

        # 2. 计算基础风险指标
        var_response = client.post("/api/portfolio/risk/var", json={
            "weights": portfolio_weights,
            "confidence_level": 0.95,
            "time_horizon": 1
        })
        assert var_response.status_code == 200

        # 3. 计算CVaR
        cvar_response = client.post("/api/portfolio/risk/cvar", json={
            "weights": portfolio_weights,
            "confidence_level": 0.95,
            "time_horizon": 1
        })
        assert cvar_response.status_code == 200

        # 4. 压力测试
        stress_response = client.post("/api/portfolio/risk/stress-test", json={
            "weights": portfolio_weights,
            "scenarios": [
                {"name": "market_crash", "impact": -0.25},
                {"name": "interest_spike", "impact": 0.15},
                {"name": "inflation_shock", "impact": -0.20}
            ]
        })
        assert stress_response.status_code == 200

        # 5. 综合风险分析
        risk_response = client.post("/api/portfolio/risk/analyze", json={
            "weights": portfolio_weights,
            "confidence_levels": [0.95, 0.99],
            "time_horizon": 1
        })
        assert risk_response.status_code == 200

        # 验证风险指标的一致性
        var_data = var_response.json()
        cvar_data = cvar_response.json()
        stress_data = stress_response.json()
        risk_data = risk_response.json()

        # CVaR应该大于VaR
        assert cvar_data["cvar"] >= var_data["var"]

        # 压力测试结果应该包含worst_case信息
        assert "worst_case" in stress_data

        # 综合分析应该包含所有指标
        assert all(metric in risk_data for metric in ["var_95", "cvar_95", "scenarios"])