"""
投资组合优化API路由
提供投资组合优化、风险分析和资产配置的HTTP接口
"""

from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import logging

from ..services.ai_service.portfolio import portfolio_optimizer, risk_model, var_model, cvar_model

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/portfolio", tags=["Portfolio Optimization"])

# 请求/响应模型
class AssetModel(BaseModel):
    """资产模型"""
    symbol: str = Field(..., description="资产代码")
    name: str = Field(..., description="资产名称")
    expected_return: float = Field(..., description="预期收益率")
    volatility: float = Field(..., description="波动率", ge=0)
    category: str = Field("equity", description="资产类别")
    market_cap: Optional[float] = Field(None, description="市值")

class OptimizationRequest(BaseModel):
    """投资组合优化请求"""
    assets: List[AssetModel] = Field(..., description="资产列表", min_items=1)
    method: str = Field("markowitz", description="优化方法")
    constraints: Optional[Dict[str, Any]] = Field(None, description="约束条件")
    returns_data: Optional[List[Dict[str, float]]] = Field(None, description="历史收益率数据")

class OptimizationResponse(BaseModel):
    """投资组合优化响应"""
    weights: Dict[str, float]
    expected_return: float
    expected_volatility: float
    sharpe_ratio: float
    method: str
    optimization_time: float
    constraints_met: bool
    risk_contributions: Dict[str, float]
    timestamp: datetime

class RiskAnalysisRequest(BaseModel):
    """风险分析请求"""
    portfolio_returns: List[float] = Field(..., description="投资组合收益率序列")
    benchmark_returns: Optional[List[float]] = Field(None, description="基准收益率序列")
    confidence_levels: List[float] = Field([0.95, 0.99], description="置信度水平")
    method: str = Field("historical", description="风险计算方法")

class RiskAnalysisResponse(BaseModel):
    """风险分析响应"""
    var_95: float
    var_99: float
    cvar_95: float
    cvar_99: float
    max_drawdown: float
    volatility: float
    sharpe_ratio: float
    beta: float
    tracking_error: float
    information_ratio: float

class StressTestRequest(BaseModel):
    """压力测试请求"""
    portfolio_returns: List[float] = Field(..., description="投资组合收益率序列")
    scenarios: Dict[str, Dict[str, float]] = Field(..., description="压力情景")

class EfficientFrontierRequest(BaseModel):
    """有效前沿请求"""
    assets: List[AssetModel] = Field(..., description="资产列表")
    num_portfolios: int = Field(100, ge=10, le=500, description="投资组合数量")

class RebalancingRequest(BaseModel):
    """再平衡请求"""
    current_weights: Dict[str, float] = Field(..., description="当前权重")
    target_weights: Dict[str, float] = Field(..., description="目标权重")
    transaction_costs: Optional[Dict[str, float]] = Field(None, description="交易成本")

@router.post("/optimize", response_model=OptimizationResponse)
async def optimize_portfolio(request: OptimizationRequest):
    """
    优化投资组合

    使用现代投资组合理论优化资产配置
    """
    try:
        from ..services.ai_service.portfolio.optimizer import Asset, OptimizationMethod

        # 转换资产数据
        assets = []
        for asset_model in request.assets:
            asset = Asset(
                symbol=asset_model.symbol,
                name=asset_model.name,
                expected_return=asset_model.expected_return,
                volatility=asset_model.volatility,
                category=asset_model.category,
                market_cap=asset_model.market_cap
            )
            assets.append(asset)

        # 转换优化方法
        try:
            method = OptimizationMethod(request.method)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的优化方法: {request.method}"
            )

        # 准备收益率数据
        returns_data = None
        if request.returns_data:
            import pandas as pd
            returns_df = pd.DataFrame(request.returns_data)
            returns_data = returns_df

        # 执行优化
        result = await portfolio_optimizer.optimize_portfolio(
            assets=assets,
            returns_data=returns_data,
            method=method,
            constraints=request.constraints
        )

        return OptimizationResponse(
            weights=result.weights,
            expected_return=result.expected_return,
            expected_volatility=result.expected_volatility,
            sharpe_ratio=result.sharpe_ratio,
            method=result.method.value,
            optimization_time=result.optimization_time,
            constraints_met=result.constraints_met,
            risk_contributions=result.risk_contributions,
            timestamp=result.timestamp
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"投资组合优化失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="投资组合优化失败"
        )

@router.post("/risk/analyze", response_model=RiskAnalysisResponse)
async def analyze_portfolio_risk(request: RiskAnalysisRequest):
    """
    分析投资组合风险

    计算各种风险指标，包括VaR、CVaR、最大回撤等
    """
    try:
        import pandas as pd
        from ..services.ai_service.portfolio.risk_models import RiskMethod

        # 转换数据格式
        portfolio_returns = pd.Series(request.portfolio_returns)
        benchmark_returns = pd.Series(request.benchmark_returns) if request.benchmark_returns else None

        # 转换风险计算方法
        try:
            method = RiskMethod(request.method)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的风险计算方法: {request.method}"
            )

        # 配置风险模型
        risk_model.confidence_levels = request.confidence_levels

        # 计算风险指标
        risk_metrics = await risk_model.calculate_portfolio_risk(
            portfolio_returns=portfolio_returns,
            benchmark_returns=benchmark_returns,
            method=method
        )

        return RiskAnalysisResponse(
            var_95=risk_metrics.var_95,
            var_99=risk_metrics.var_99,
            cvar_95=risk_metrics.cvar_95,
            cvar_99=risk_metrics.cvar_99,
            max_drawdown=risk_metrics.max_drawdown,
            volatility=risk_metrics.volatility,
            sharpe_ratio=risk_metrics.sharpe_ratio,
            beta=risk_metrics.beta,
            tracking_error=risk_metrics.tracking_error,
            information_ratio=risk_metrics.information_ratio
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"风险分析失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="风险分析失败"
        )

@router.post("/risk/var")
async def calculate_var(portfolio_returns: List[float],
                       confidence_level: float = 0.95,
                       method: str = "historical"):
    """
    计算VaR（风险价值）

    """
    try:
        import pandas as pd
        from ..services.ai_service.portfolio.risk_models import RiskMethod

        returns_series = pd.Series(portfolio_returns)
        risk_method = RiskMethod(method)

        # 配置VaR模型
        var_model.method = risk_method

        # 计算VaR
        var = await var_model.calculate_var(returns_series, confidence_level)

        return JSONResponse(
            content={
                "var": var,
                "confidence_level": confidence_level,
                "method": method,
                "interpretation": f"在{confidence_level*100:.0f}%的置信度下，单日最大损失预计不超过{abs(var)*100:.2f}%"
            }
        )

    except Exception as e:
        logger.error(f"VaR计算失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="VaR计算失败"
        )

@router.post("/risk/cvar")
async def calculate_cvar(portfolio_returns: List[float],
                        confidence_level: float = 0.95,
                        method: str = "historical"):
    """
    计算CVaR（条件风险价值）

    """
    try:
        import pandas as pd
        from ..services.ai_service.portfolio.risk_models import RiskMethod

        returns_series = pd.Series(portfolio_returns)
        risk_method = RiskMethod(method)

        # 配置CVaR模型
        cvar_model.method = risk_method

        # 计算CVaR
        cvar = await cvar_model.calculate_cvar(returns_series, confidence_level)

        return JSONResponse(
            content={
                "cvar": cvar,
                "confidence_level": confidence_level,
                "method": method,
                "interpretation": f"在{confidence_level*100:.0f}%的置信度下，超出VaR的平均损失为{abs(cvar)*100:.2f}%"
            }
        )

    except Exception as e:
        logger.error(f"CVaR计算失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="CVaR计算失败"
        )

@router.post("/risk/stress-test")
async def stress_test(request: StressTestRequest):
    """
    压力测试

    在不同市场情景下评估投资组合风险
    """
    try:
        import pandas as pd

        portfolio_returns = pd.Series(request.portfolio_returns)

        # 执行压力测试
        stress_results = await risk_model.stress_testing(portfolio_returns, request.scenarios)

        return JSONResponse(
            content={
                "stress_test_results": stress_results,
                "summary": {
                    "total_scenarios": len(request.scenarios),
                    "successful_scenarios": len([r for r in stress_results.values() if 'error' not in r])
                }
            }
        )

    except Exception as e:
        logger.error(f"压力测试失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="压力测试失败"
        )

@router.post("/efficient-frontier")
async def calculate_efficient_frontier(request: EfficientFrontierRequest):
    """
    计算有效前沿

    生成风险-收益最优组合的曲线
    """
    try:
        from ..services.ai_service.portfolio.optimizer import Asset

        # 转换资产数据
        assets = []
        for asset_model in request.assets:
            asset = Asset(
                symbol=asset_model.symbol,
                name=asset_model.name,
                expected_return=asset_model.expected_return,
                volatility=asset_model.volatility,
                category=asset_model.category,
                market_cap=asset_model.market_cap
            )
            assets.append(asset)

        # 计算有效前沿
        efficient_portfolios = await portfolio_optimizer.efficient_frontier(
            assets=assets,
            num_portfolios=request.num_portfolios
        )

        return JSONResponse(
            content={
                "efficient_frontier": efficient_portfolios,
                "num_portfolios": len(efficient_portfolios),
                "asset_symbols": [asset.symbol for asset in assets]
            }
        )

    except Exception as e:
        logger.error(f"有效前沿计算失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="有效前沿计算失败"
        )

@router.post("/rebalance")
async def calculate_rebalancing(request: RebalancingRequest):
    """
    计算投资组合再平衡

    """
    try:
        # 计算权重变化
        weight_changes = {}
        for asset, target_weight in request.target_weights.items():
            current_weight = request.current_weights.get(asset, 0.0)
            weight_changes[asset] = target_weight - current_weight

        # 计算交易成本
        total_transaction_cost = 0.0
        if request.transaction_costs:
            for asset, change in weight_changes.items():
                cost_rate = request.transaction_costs.get(asset, 0.001)  # 默认0.1%
                total_transaction_cost += abs(change) * cost_rate

        # 计算再平衡指标
        turnover = sum(abs(change) for change in weight_changes.values()) / 2
        needs_rebalancing = any(abs(change) > 0.05 for change in weight_changes.values())  # 5%阈值

        return JSONResponse(
            content={
                "weight_changes": weight_changes,
                "turnover": turnover,
                "total_transaction_cost": total_transaction_cost,
                "needs_rebalancing": needs_rebalancing,
                "recommendation": "建议再平衡" if needs_rebalancing else "无需再平衡",
                "rebalancing_plan": {
                    "assets_to_buy": {k: v for k, v in weight_changes.items() if v > 0.01},
                    "assets_to_sell": {k: v for k, v in weight_changes.items() if v < -0.01}
                }
            }
        )

    except Exception as e:
        logger.error(f"再平衡计算失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="再平衡计算失败"
        )

@router.get("/methods")
async def get_optimization_methods():
    """
    获取可用的优化方法

    返回所有支持的投资组合优化方法
    """
    try:
        from ..services.ai_service.portfolio.optimizer import OptimizationMethod

        methods = {
            "markowitz": {
                "name": "马科维茨均值-方差优化",
                "description": "经典的现代投资组合理论方法",
                "objective": "在给定收益率下最小化风险",
                "suitable_for": "长期投资者，风险厌恶型"
            },
            "black_litterman": {
                "name": "Black-Litterman模型",
                "description": "结合投资者观点的均衡收益模型",
                "objective": "结合市场均衡和主观观点",
                "suitable_for": "有明确市场观点的投资者"
            },
            "risk_parity": {
                "name": "风险平价",
                "description": "等风险贡献投资组合",
                "objective": "使各资产风险贡献相等",
                "suitable_for": "风险分散化需求强烈的投资者"
            },
            "minimum_variance": {
                "name": "最小方差",
                "description": "最小化组合方差",
                "objective": "实现最低风险",
                "suitable_for": "极度风险厌恶型投资者"
            },
            "maximum_sharpe": {
                "name": "最大夏普比率",
                "description": "最大化风险调整收益",
                "objective": "实现最优风险收益比",
                "suitable_for": "追求风险调整收益的投资者"
            },
            "equal_weight": {
                "name": "等权重",
                "description": "简单的等权重分配",
                "objective": "简化的分散化投资",
                "suitable_for": "新手投资者或作为基准"
            },
            "hrp": {
                "name": "层次风险平价",
                "description": "基于聚类的风险平价方法",
                "objective": "考虑资产相关性的风险分散",
                "suitable_for": "复杂资产配置"
            }
        }

        return JSONResponse(
            content={
                "methods": methods,
                "default_method": "markowitz"
            }
        )

    except Exception as e:
        logger.error(f"获取优化方法失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取优化方法失败"
        )

@router.get("/health")
async def health_check():
    """
    健康检查

    检查投资组合优化服务的运行状态
    """
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "portfolio_optimizer": "healthy",
                "risk_model": "healthy",
                "var_model": "healthy",
                "cvar_model": "healthy"
            },
            "statistics": portfolio_optimizer.get_optimization_statistics()
        }

        return JSONResponse(content=health_status)

    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
        )

# 错误处理器
@router.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )

@router.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理"""
    logger.error(f"未处理的异常: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "内部服务器错误",
            "status_code": 500
        }
    )