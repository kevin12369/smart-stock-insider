"""
投资组合优化器单元测试
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.services.ai_service.portfolio.optimizer import (
    PortfolioOptimizer, OptimizationMethod, Asset, OptimizationResult
)

@pytest.fixture
def portfolio_optimizer():
    """投资组合优化器夹具"""
    config = {
        "risk_free_rate": 0.03,
        "frequency": 252,
        "max_iterations": 1000,
        "tolerance": 1e-8
    }
    return PortfolioOptimizer(config)

@pytest.fixture
def sample_assets():
    """示例资产数据"""
    return [
        Asset(
            symbol="AAPL",
            name="Apple Inc.",
            expected_return=0.12,
            volatility=0.22,
            category="technology"
        ),
        Asset(
            symbol="MSFT",
            name="Microsoft Corporation",
            expected_return=0.10,
            volatility=0.18,
            category="technology"
        ),
        Asset(
            symbol="GOOGL",
            name="Alphabet Inc.",
            expected_return=0.11,
            volatility=0.20,
            category="technology"
        ),
        Asset(
            symbol="JPM",
            name="JPMorgan Chase & Co.",
            expected_return=0.08,
            volatility=0.15,
            category="finance"
        )
    ]

@pytest.fixture
def sample_returns_data():
    """示例收益率数据"""
    np.random.seed(42)
    dates = pd.date_range("2023-01-01", "2023-12-31", freq="D")

    # 生成相关的收益率数据
    assets = ["AAPL", "MSFT", "GOOGL", "JPM"]
    returns_data = {}

    for asset in assets:
        # 不同的资产有不同的特征
        if asset in ["AAPL", "MSFT", "GOOGL"]:
            returns = np.random.normal(0.001, 0.02, len(dates))
        else:  # JPM
            returns = np.random.normal(0.0005, 0.015, len(dates))

        returns_data[asset] = returns

    return pd.DataFrame(returns_data, index=dates)

@pytest.fixture
def sample_constraints():
    """示例约束条件"""
    return {
        "min_weight": 0.0,
        "max_weight": 0.5,
        "target_return": None,
        "target_volatility": None,
        "sector_limits": {
            "technology": 0.7,
            "finance": 0.3
        }
    }

class TestPortfolioOptimizer:
    """投资组合优化器测试类"""

    def test_initialization(self, portfolio_optimizer):
        """测试初始化"""
        assert portfolio_optimizer.risk_free_rate == 0.03
        assert portfolio_optimizer.frequency == 252
        assert portfolio_optimizer.max_iterations == 1000
        assert portfolio_optimizer.tolerance == 1e-8

    @pytest.mark.asyncio
    async def test_markowitz_optimization(self, portfolio_optimizer, sample_assets, sample_returns_data):
        """测试马科维茨优化"""
        result = await portfolio_optimizer.optimize_portfolio(
            assets=sample_assets,
            returns_data=sample_returns_data,
            method=OptimizationMethod.MARKOWITZ
        )

        assert isinstance(result, OptimizationResult)
        assert result.method == OptimizationMethod.MARKOWITZ
        assert len(result.weights) == len(sample_assets)
        assert result.constraints_met is True
        assert result.expected_return >= 0
        assert result.expected_volatility >= 0
        assert result.sharpe_ratio >= 0

        # 验证权重约束
        total_weight = sum(result.weights.values())
        assert abs(total_weight - 1.0) < 1e-6

        # 验证每个权重都是非负数
        for weight in result.weights.values():
            assert weight >= 0

    @pytest.mark.asyncio
    async def test_minimum_variance_optimization(self, portfolio_optimizer, sample_assets, sample_returns_data):
        """测试最小方差优化"""
        result = await portfolio_optimizer.optimize_portfolio(
            assets=sample_assets,
            returns_data=sample_returns_data,
            method=OptimizationMethod.MINIMUM_VARIANCE
        )

        assert result.method == OptimizationMethod.MINIMUM_VARIANCE
        assert result.expected_volatility >= 0

        # 最小方差组合的波动率应该相对较低
        assert result.expected_volatility < 0.25

    @pytest.mark.asyncio
    async def test_maximum_sharpe_optimization(self, portfolio_optimizer, sample_assets, sample_returns_data):
        """测试最大夏普比率优化"""
        result = await portfolio_optimizer.optimize_portfolio(
            assets=sample_assets,
            returns_data=sample_returns_data,
            method=OptimizationMethod.MAXIMUM_SHARPE
        )

        assert result.method == OptimizationMethod.MAXIMUM_SHARPE
        assert result.sharpe_ratio >= 0

    @pytest.mark.asyncio
    async def test_equal_weight_optimization(self, portfolio_optimizer, sample_assets):
        """测试等权重优化"""
        result = await portfolio_optimizer.optimize_portfolio(
            assets=sample_assets,
            method=OptimizationMethod.EQUAL_WEIGHT
        )

        assert result.method == OptimizationMethod.EQUAL_WEIGHT

        # 等权重组合中每个资产权重应该相等
        expected_weight = 1.0 / len(sample_assets)
        for weight in result.weights.values():
            assert abs(weight - expected_weight) < 1e-6

    @pytest.mark.asyncio
    async def test_risk_parity_optimization(self, portfolio_optimizer, sample_assets, sample_returns_data):
        """测试风险平价优化"""
        result = await portfolio_optimizer.optimize_portfolio(
            assets=sample_assets,
            returns_data=sample_returns_data,
            method=OptimizationMethod.RISK_PARITY
        )

        assert result.method == OptimizationMethod.RISK_PARITY

        # 风险平价组合中各资产的风险贡献应该大致相等
        risk_contributions = list(result.risk_contributions.values())
        mean_contribution = np.mean(risk_contributions)

        for contribution in risk_contributions:
            assert abs(contribution - mean_contribution) < 0.1  # 允许10%的误差

    @pytest.mark.asyncio
    async def test_optimization_with_constraints(self, portfolio_optimizer, sample_assets,
                                                sample_returns_data, sample_constraints):
        """测试带约束的优化"""
        result = await portfolio_optimizer.optimize_portfolio(
            assets=sample_assets,
            returns_data=sample_returns_data,
            method=OptimizationMethod.MARKOWITZ,
            constraints=sample_constraints
        )

        # 验证最大权重约束
        for weight in result.weights.values():
            assert weight <= sample_constraints["max_weight"]

        # 验证行业约束
        tech_weight = sum(weight for symbol, weight in result.weights.items()
                         if symbol in ["AAPL", "MSFT", "GOOGL"])
        finance_weight = result.weights.get("JPM", 0)

        assert tech_weight <= sample_constraints["sector_limits"]["technology"]
        assert finance_weight <= sample_constraints["sector_limits"]["finance"]

    def test_calculate_expected_returns(self, portfolio_optimizer, sample_returns_data):
        """测试计算期望收益率"""
        expected_returns = portfolio_optimizer._calculate_expected_returns(sample_returns_data)

        assert isinstance(expected_returns, pd.Series)
        assert len(expected_returns) == len(sample_returns_data.columns)
        assert all(ret >= 0 for ret in expected_returns)  # 年化收益率应该为正

    def test_calculate_covariance_matrix(self, portfolio_optimizer, sample_returns_data):
        """测试计算协方差矩阵"""
        covariance_matrix = portfolio_optimizer._calculate_covariance_matrix(sample_returns_data)

        assert isinstance(covariance_matrix, pd.DataFrame)
        assert covariance_matrix.shape == (len(sample_returns_data.columns), len(sample_returns_data.columns))

        # 验证协方差矩阵的对称性
        assert np.allclose(covariance_matrix.values, covariance_matrix.T.values)

        # 验证对角线元素为正（方差）
        assert all(np.diag(covariance_matrix) > 0)

    def test_generate_simulated_returns(self, portfolio_optimizer, sample_assets):
        """测试生成模拟收益率数据"""
        simulated_data = portfolio_optimizer._generate_simulated_returns(sample_assets)

        assert isinstance(simulated_data, pd.DataFrame)
        assert len(simulated_data.columns) == len(sample_assets)
        assert len(simulated_data) > 0

        # 验证每列都有数据
        for column in simulated_data.columns:
            assert len(simulated_data[column].dropna()) > 0

    @pytest.mark.asyncio
    async def test_optimization_error_handling(self, portfolio_optimizer):
        """测试优化错误处理"""
        # 测试空资产列表
        with pytest.raises(Exception):
            await portfolio_optimizer.optimize_portfolio(
                assets=[],
                method=OptimizationMethod.MARKOWITZ
            )

        # 测试无效的优化方法
        invalid_method = "invalid_method"
        result = await portfolio_optimizer.optimize_portfolio(
            assets=sample_assets,
            method=invalid_method
        )
        # 应该回退到默认方法
        assert result.method == OptimizationMethod.MARKOWITZ

    def test_portfolio_performance_metrics(self, portfolio_optimizer):
        """测试投资组合性能指标计算"""
        weights = {"AAPL": 0.4, "MSFT": 0.3, "GOOGL": 0.2, "JPM": 0.1}
        expected_returns = pd.Series({"AAPL": 0.12, "MSFT": 0.10, "GOOGL": 0.11, "JPM": 0.08})
        covariance_matrix = pd.DataFrame({
            "AAPL": [0.0484, 0.0324, 0.0360, 0.0216],
            "MSFT": [0.0324, 0.0324, 0.0288, 0.0180],
            "GOOGL": [0.0360, 0.0288, 0.0400, 0.0200],
            "JPM": [0.0216, 0.0180, 0.0200, 0.0225]
        })

        portfolio_return = portfolio_optimizer._calculate_portfolio_return(weights, expected_returns)
        portfolio_variance = portfolio_optimizer._calculate_portfolio_variance(weights, covariance_matrix)

        assert portfolio_return >= 0
        assert portfolio_variance >= 0

        portfolio_volatility = np.sqrt(portfolio_variance)
        sharpe_ratio = (portfolio_return - portfolio_optimizer.risk_free_rate) / portfolio_volatility

        assert sharpe_ratio >= 0

    def test_efficient_frontier_calculation(self, portfolio_optimizer, sample_assets, sample_returns_data):
        """测试有效前沿计算"""
        efficient_frontier = portfolio_optimizer._calculate_efficient_frontier(
            sample_assets, sample_returns_data, num_portfolios=20
        )

        assert len(efficient_frontier) == 20
        assert all("return" in point for point in efficient_frontier)
        assert all("volatility" in point for point in efficient_frontier)
        assert all("sharpe_ratio" in point for point in efficient_frontier)

        # 验证有效前沿的单调性
        returns = [point["return"] for point in efficient_frontier]
        volatilities = [point["volatility"] for point in efficient_frontier]

        # 有效的投资组合应该在有效前沿上
        for i in range(1, len(efficient_frontier)):
            if returns[i] > returns[i-1]:
                assert volatilities[i] >= volatilities[i-1]

    @pytest.mark.asyncio
    async def test_black_litterman_optimization(self, portfolio_optimizer, sample_assets, sample_returns_data):
        """测试Black-Litterman优化"""
        # 设置投资者观点
        investor_views = {
            "AAPL": {"expected_return": 0.15, "confidence": 0.7},
            "MSFT": {"expected_return": 0.08, "confidence": 0.5}
        }

        result = await portfolio_optimizer.optimize_portfolio(
            assets=sample_assets,
            returns_data=sample_returns_data,
            method=OptimizationMethod.BLACK_LITTERMAN
        )

        assert result.method == OptimizationMethod.BLACK_LITTERMAN
        assert result.constraints_met is True

    @pytest.mark.asyncio
    async def test_robustness_checks(self, portfolio_optimizer, sample_assets, sample_returns_data):
        """测试鲁棒性检查"""
        result = await portfolio_optimizer.optimize_portfolio(
            assets=sample_assets,
            returns_data=sample_returns_data,
            method=OptimizationMethod.MARKOWITZ
        )

        # 验证权重和为1
        total_weight = sum(result.weights.values())
        assert abs(total_weight - 1.0) < 1e-6

        # 验证权重在合理范围内
        for weight in result.weights.values():
            assert 0 <= weight <= 1

        # 验证性能指标的合理性
        assert result.expected_return >= 0
        assert result.expected_volatility >= 0
        assert not np.isnan(result.sharpe_ratio)
        assert not np.isinf(result.sharpe_ratio)

    def test_risk_contribution_calculation(self, portfolio_optimizer):
        """测试风险贡献计算"""
        weights = {"AAPL": 0.4, "MSFT": 0.3, "GOOGL": 0.2, "JPM": 0.1}
        covariance_matrix = pd.DataFrame({
            "AAPL": [0.0484, 0.0324, 0.0360, 0.0216],
            "MSFT": [0.0324, 0.0324, 0.0288, 0.0180],
            "GOOGL": [0.0360, 0.0288, 0.0400, 0.0200],
            "JPM": [0.0216, 0.0180, 0.0200, 0.0225]
        })

        risk_contributions = portfolio_optimizer._calculate_risk_contributions(weights, covariance_matrix)

        assert len(risk_contributions) == len(weights)
        assert all(contribution >= 0 for contribution in risk_contributions.values())

        # 验证风险贡献和等于投资组合方差
        total_risk = sum(risk_contributions.values())
        portfolio_variance = portfolio_optimizer._calculate_portfolio_variance(weights, covariance_matrix)
        assert abs(total_risk - portfolio_variance) < 1e-6

    @pytest.mark.asyncio
    async def test_optimization_timeout(self, portfolio_optimizer, sample_assets, sample_returns_data):
        """测试优化超时处理"""
        # 设置非常短的超时时间
        portfolio_optimizer.max_iterations = 1

        result = await portfolio_optimizer.optimize_portfolio(
            assets=sample_assets,
            returns_data=sample_returns_data,
            method=OptimizationMethod.MARKOWITZ
        )

        # 即使超时，也应该返回一个结果（可能是近似解）
        assert isinstance(result, OptimizationResult)
        assert result.optimization_time < 5.0  # 应该很快完成

    @pytest.mark.asyncio
    async def test_different_asset_numbers(self, portfolio_optimizer, sample_returns_data):
        """测试不同数量的资产"""
        # 测试少量资产（2个）
        assets_2 = [
            Asset("AAPL", "Apple Inc.", 0.12, 0.22),
            Asset("MSFT", "Microsoft", 0.10, 0.18)
        ]

        result_2 = await portfolio_optimizer.optimize_portfolio(
            assets=assets_2,
            returns_data=sample_returns_data[["AAPL", "MSFT"]],
            method=OptimizationMethod.MARKOWITZ
        )
        assert len(result_2.weights) == 2

        # 测试较多资产（如果数据支持）
        if len(sample_returns_data.columns) >= 6:
            assets_many = [
                Asset(symbol, f"Company {symbol}", 0.10, 0.20)
                for symbol in sample_returns_data.columns[:6]
            ]

            result_many = await portfolio_optimizer.optimize_portfolio(
                assets=assets_many,
                returns_data=sample_returns_data.iloc[:, :6],
                method=OptimizationMethod.EQUAL_WEIGHT
            )
            assert len(result_many.weights) == 6

@pytest.mark.unit
@pytest.mark.portfolio
@pytest.mark.ai
class TestPortfolioOptimizerIntegration:
    """投资组合优化器集成测试"""

    @pytest.mark.asyncio
    async def test_real_world_scenario(self, portfolio_optimizer):
        """测试真实世界场景"""
        # 模拟真实的资产数据
        assets = [
            Asset("AAPL", "Apple Inc.", 0.15, 0.25, "technology"),
            Asset("MSFT", "Microsoft", 0.12, 0.20, "technology"),
            Asset("GOOGL", "Alphabet", 0.14, 0.22, "technology"),
            Asset("AMZN", "Amazon", 0.18, 0.30, "consumer_discretionary"),
            Asset("JPM", "JPMorgan", 0.10, 0.18, "finance"),
            Asset("GS", "Goldman Sachs", 0.11, 0.20, "finance")
        ]

        # 生成更真实的收益率数据
        np.random.seed(123)
        dates = pd.date_range("2022-01-01", "2023-12-31", freq="D")

        returns_data = {}
        for asset in assets:
            base_return = asset.expected_return / 252
            volatility = asset.volatility / np.sqrt(252)
            returns = np.random.normal(base_return, volatility, len(dates))
            returns_data[asset.symbol] = returns

        returns_df = pd.DataFrame(returns_data, index=dates)

        # 执行多种优化方法
        methods = [
            OptimizationMethod.MARKOWITZ,
            OptimizationMethod.MINIMUM_VARIANCE,
            OptimizationMethod.MAXIMUM_SHARPE,
            OptimizationMethod.RISK_PARITY
        ]

        results = {}
        for method in methods:
            result = await portfolio_optimizer.optimize_portfolio(
                assets=assets,
                returns_data=returns_df,
                method=method
            )
            results[method] = result

        # 验证不同方法的结果
        for method, result in results.items():
            assert isinstance(result, OptimizationResult)
            assert result.method == method
            assert result.constraints_met is True

        # 比较不同方法的夏普比率
        sharpe_ratios = {method: result.sharpe_ratio for method, result in results.items()}
        max_sharpe_method = max(sharpe_ratios, key=sharpe_ratios.get)

        # 最大夏普比率方法应该给出最高的夏普比率
        assert sharpe_ratios[max_sharpe_method] >= sharpe_ratios[OptimizationMethod.MARKOWITZ]

    @pytest.mark.asyncio
    async def test_constraints_satisfaction(self, portfolio_optimizer, sample_returns_data):
        """测试约束满足"""
        assets = [
            Asset("TECH1", "Tech Company 1", 0.15, 0.25, "technology"),
            Asset("TECH2", "Tech Company 2", 0.12, 0.20, "technology"),
            Asset("TECH3", "Tech Company 3", 0.18, 0.30, "technology"),
            Asset("FIN1", "Finance Company 1", 0.08, 0.15, "finance"),
            Asset("FIN2", "Finance Company 2", 0.10, 0.18, "finance")
        ]

        constraints = {
            "min_weight": 0.05,
            "max_weight": 0.4,
            "sector_limits": {
                "technology": 0.6,
                "finance": 0.4
            }
        }

        result = await portfolio_optimizer.optimize_portfolio(
            assets=assets,
            returns_data=sample_returns_data[list(asset.symbol for asset in assets)],
            method=OptimizationMethod.MARKOWITZ,
            constraints=constraints
        )

        # 验证所有约束都满足
        for weight in result.weights.values():
            assert constraints["min_weight"] <= weight <= constraints["max_weight"]

        tech_weight = sum(result.weights[asset.symbol] for asset in assets if asset.category == "technology")
        finance_weight = sum(result.weights[asset.symbol] for asset in assets if asset.category == "finance")

        assert tech_weight <= constraints["sector_limits"]["technology"]
        assert finance_weight <= constraints["sector_limits"]["finance"]

    @pytest.mark.asyncio
    async def test_sensitivity_analysis(self, portfolio_optimizer, sample_assets, sample_returns_data):
        """测试敏感性分析"""
        base_result = await portfolio_optimizer.optimize_portfolio(
            assets=sample_assets,
            returns_data=sample_returns_data,
            method=OptimizationMethod.MARKOWITZ
        )

        # 测试不同无风险利率的影响
        risk_free_rates = [0.01, 0.03, 0.05]
        results_by_rfr = {}

        for rfr in risk_free_rates:
            portfolio_optimizer.risk_free_rate = rfr
            result = await portfolio_optimizer.optimize_portfolio(
                assets=sample_assets,
                returns_data=sample_returns_data,
                method=OptimizationMethod.MAXIMUM_SHARPE
            )
            results_by_rfr[rfr] = result

        # 验证无风险利率对最优组合的影响
        weights_by_rfr = {rfr: result.weights for rfr, result in results_by_rfr.items()}

        # 不同的无风险利率应该产生不同的权重
        weight_differences = []
        for i, rfr1 in enumerate(risk_free_rates):
            for rfr2 in risk_free_rates[i+1:]:
                w1 = weights_by_rfr[rfr1]
                w2 = weights_by_rfr[rfr2]
                diff = sum(abs(w1[symbol] - w2[symbol]) for symbol in w1.keys())
                weight_differences.append(diff)

        # 至少应该有一些差异
        assert any(diff > 0.01 for diff in weight_differences)