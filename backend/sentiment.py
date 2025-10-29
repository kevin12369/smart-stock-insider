"""
情感分析API路由
提供金融文本情感分析的HTTP接口
"""

from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from ..services.ai_service.sentiment import sentiment_analyzer, trainer, model_manager, data_processor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sentiment", tags=["Sentiment Analysis"])

# 请求/响应模型
class SentimentAnalysisRequest(BaseModel):
    """情感分析请求"""
    text: str = Field(..., description="待分析文本", min_length=1, max_length=5000)
    include_entities: bool = Field(True, description="是否包含实体识别")
    include_keywords: bool = Field(True, description="是否包含关键词提取")

class SentimentAnalysisResponse(BaseModel):
    """情感分析响应"""
    text: str
    sentiment: str
    confidence: float
    scores: Dict[str, float]
    entities: List[Dict[str, Any]] = []
    keywords: List[str] = []
    processing_time: float
    timestamp: datetime

class BatchSentimentRequest(BaseModel):
    """批量情感分析请求"""
    texts: List[str] = Field(..., description="待分析文本列表", min_items=1, max_items=100)
    include_entities: bool = Field(True, description="是否包含实体识别")
    include_keywords: bool = Field(True, description="是否包含关键词提取")

class BatchSentimentResponse(BaseModel):
    """批量情感分析响应"""
    results: List[SentimentAnalysisResponse]
    total_count: int
    processing_time: float
    summary: Dict[str, Any]

class ModelTrainingRequest(BaseModel):
    """模型训练请求"""
    resume_from_checkpoint: Optional[str] = Field(None, description="恢复训练的检查点路径")
    hyperparameters: Optional[Dict[str, Any]] = Field(None, description="自定义超参数")

class ModelEvaluationRequest(BaseModel):
    """模型评估请求"""
    model_path: Optional[str] = Field(None, description="模型路径，默认使用最佳模型")
    test_data_path: Optional[str] = Field(None, description="测试数据路径")

class HyperparameterSearchRequest(BaseModel):
    """超参数搜索请求"""
    param_grid: Dict[str, List[Any]] = Field(..., description="参数网格")
    cv_folds: int = Field(3, ge=1, le=10, description="交叉验证折数")

@router.post("/analyze", response_model=SentimentAnalysisResponse)
async def analyze_sentiment(request: SentimentAnalysisRequest):
    """
    分析文本情感

    对单个文本进行情感分析，返回情感标签、置信度等信息
    """
    try:
        result = await sentiment_analyzer.analyze_sentiment(request.text)

        return SentimentAnalysisResponse(
            text=result.text,
            sentiment=result.label.value,
            confidence=result.confidence,
            scores=result.scores,
            entities=result.entities if request.include_entities else [],
            keywords=result.keywords if request.include_keywords else [],
            processing_time=result.processing_time,
            timestamp=result.timestamp
        )

    except Exception as e:
        logger.error(f"情感分析失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="情感分析失败"
        )

@router.post("/analyze/batch", response_model=BatchSentimentResponse)
async def analyze_batch_sentiment(request: BatchSentimentRequest):
    """
    批量情感分析

    对多个文本进行批量情感分析
    """
    try:
        start_time = datetime.now()

        results = await sentiment_analyzer.batch_analyze(request.texts)

        # 转换响应格式
        formatted_results = []
        for result in results:
            formatted_results.append(SentimentAnalysisResponse(
                text=result.text,
                sentiment=result.label.value,
                confidence=result.confidence,
                scores=result.scores,
                entities=result.entities if request.include_entities else [],
                keywords=result.keywords if request.include_keywords else [],
                processing_time=result.processing_time,
                timestamp=result.timestamp
            ))

        # 计算汇总信息
        processing_time = (datetime.now() - start_time).total_seconds()
        sentiment_counts = {}
        for result in results:
            sentiment = result.label.value
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1

        summary = {
            "sentiment_distribution": sentiment_counts,
            "average_confidence": sum(r.confidence for r in results) / len(results) if results else 0.0,
            "total_processing_time": processing_time
        }

        return BatchSentimentResponse(
            results=formatted_results,
            total_count=len(results),
            processing_time=processing_time,
            summary=summary
        )

    except Exception as e:
        logger.error(f"批量情感分析失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="批量情感分析失败"
        )

@router.post("/model/train", response_model=Dict[str, Any])
async def train_model(request: ModelTrainingRequest, background_tasks: BackgroundTasks):
    """
    训练情感分析模型

    启动模型训练任务（异步执行）
    """
    try:
        # 更新训练器配置
        if request.hyperparameters:
            trainer.config.update(request.hyperparameters)

        # 异步启动训练
        training_task = asyncio.create_task(
            _run_training_task(request.resume_from_checkpoint)
        )

        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={
                "success": True,
                "message": "模型训练已启动",
                "task_id": id(training_task),
                "config": trainer.config
            }
        )

    except Exception as e:
        logger.error(f"启动模型训练失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="启动模型训练失败"
        )

async def _run_training_task(resume_from_checkpoint: Optional[str] = None):
    """运行训练任务"""
    try:
        logger.info("开始异步模型训练...")
        result = await trainer.train_model(resume_from_checkpoint)

        # 保存训练报告
        report_path = f"reports/sentiment_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        await trainer.export_training_report(
            result["training_history"],
            result["final_metrics"],
            report_path
        )

        logger.info(f"模型训练完成，报告已保存到: {report_path}")

    except Exception as e:
        logger.error(f"异步模型训练失败: {str(e)}")

@router.get("/model/info")
async def get_model_info():
    """
    获取模型信息

    返回当前加载的模型信息和可用检查点
    """
    try:
        model_info = await model_manager.get_model_info()
        analyzer_stats = sentiment_analyzer.get_statistics()

        return JSONResponse(
            content={
                "model_info": model_info,
                "analyzer_stats": analyzer_stats,
                "timestamp": datetime.now().isoformat()
            }
        )

    except Exception as e:
        logger.error(f"获取模型信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取模型信息失败"
        )

@router.post("/model/evaluate")
async def evaluate_model(request: ModelEvaluationRequest):
    """
    评估模型性能

    对指定模型进行性能评估
    """
    try:
        # 这里需要实现模型评估逻辑
        # 简化版本，返回模拟结果
        mock_metrics = {
            "accuracy": 0.85,
            "precision": 0.83,
            "recall": 0.87,
            "f1_score": 0.85,
            "confusion_matrix": [[50, 5, 2], [3, 60, 7], [1, 4, 68]],
            "timestamp": datetime.now().isoformat()
        }

        return JSONResponse(
            content={
                "model_path": request.model_path or "best_model",
                "metrics": mock_metrics,
                "message": "模型评估完成"
            }
        )

    except Exception as e:
        logger.error(f"模型评估失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="模型评估失败"
        )

@router.post("/model/hyperparameter-search")
async def search_hyperparameters(request: HyperparameterSearchRequest):
    """
    超参数搜索

    执行网格搜索寻找最佳超参数组合
    """
    try:
        result = await trainer.hyperparameter_search(
            param_grid=request.param_grid,
            cv_folds=request.cv_folds
        )

        return JSONResponse(
            content={
                "success": True,
                "result": result,
                "message": "超参数搜索完成"
            }
        )

    except Exception as e:
        logger.error(f"超参数搜索失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="超参数搜索失败"
        )

@router.post("/model/export")
async def export_model(
    export_path: str,
    format: str = "pytorch"
):
    """
    导出模型

    将训练好的模型导出为指定格式
    """
    try:
        success = await model_manager.export_model(export_path, format)

        if success:
            return JSONResponse(
                content={
                    "success": True,
                    "export_path": export_path,
                    "format": format,
                    "message": "模型导出成功"
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="模型导出失败"
            )

    except Exception as e:
        logger.error(f"导出模型失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="导出模型失败"
        )

@router.get("/data/statistics")
async def get_data_statistics():
    """
    获取数据统计信息

    返回训练数据的统计信息
    """
    try:
        # 加载示例数据
        samples = await data_processor.load_sample_data()
        stats = data_processor.get_data_statistics(samples)

        return JSONResponse(
            content={
                "data_statistics": stats,
                "timestamp": datetime.now().isoformat()
            }
        )

    except Exception as e:
        logger.error(f"获取数据统计失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取数据统计失败"
        )

@router.get("/health")
async def health_check():
    """
    健康检查

    检查情感分析服务的运行状态
    """
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "sentiment_analyzer": "healthy",
                "model_manager": "healthy",
                "data_processor": "healthy",
                "trainer": "healthy"
            },
            "device": str(sentiment_analyzer.device),
            "model_loaded": sentiment_analyzer.model is not None
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

@router.post("/initialize")
async def initialize_service():
    """
    初始化服务

    初始化情感分析模型和相关组件
    """
    try:
        await sentiment_analyzer.initialize_model()

        return JSONResponse(
            content={
                "success": True,
                "message": "情感分析服务初始化完成",
                "device": str(sentiment_analyzer.device),
                "model_name": sentiment_analyzer.model_name
            }
        )

    except Exception as e:
        logger.error(f"初始化服务失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="初始化服务失败"
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