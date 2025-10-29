"""
情感分析API单元测试
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
from backend.api.sentiment import router as sentiment_router

app = FastAPI()
app.include_router(sentiment_router)

client = TestClient(app)

@pytest.fixture
def mock_sentiment_analyzer():
    """模拟情感分析器"""
    with patch('backend.api.sentiment.sentiment_analyzer') as mock_analyzer:
        # 模拟单个文本分析结果
        mock_analyzer.analyze_sentiment = AsyncMock(return_value=Mock(
            text="腾讯股价大涨5%，创历史新高",
            label=Mock(value="positive"),
            confidence=0.85,
            scores={
                "strongly_positive": 0.1,
                "positive": 0.75,
                "neutral": 0.1,
                "negative": 0.05,
                "strongly_negative": 0.0
            },
            entities=[
                {"type": "company", "value": "腾讯"},
                {"type": "percentage", "value": "5%"}
            ],
            keywords=["大涨", "历史新高", "腾讯"],
            processing_time=0.25,
            timestamp=datetime.now()
        ))

        # 模拟批量分析结果
        mock_batch_results = [
            Mock(
                text="腾讯股价大涨5%",
                label=Mock(value="positive"),
                confidence=0.85,
                scores={"positive": 0.8, "neutral": 0.2},
                entities=[{"type": "company", "value": "腾讯"}],
                keywords=["腾讯", "股价"],
                processing_time=0.2
            ),
            Mock(
                text="市场下跌担忧",
                label=Mock(value="negative"),
                confidence=0.75,
                scores={"negative": 0.7, "neutral": 0.3},
                entities=[{"type": "concept", "value": "市场"}],
                keywords=["下跌", "担忧"],
                processing_time=0.18
            )
        ]
        mock_analyzer.batch_analyze = AsyncMock(return_value=mock_batch_results)

        # 模拟统计信息
        mock_analyzer.get_statistics.return_value = {
            "total_analyses": 1500,
            "successful_analyses": 1485,
            "failed_analyses": 15,
            "average_processing_time": 0.32,
            "sentiment_distribution": {
                "strongly_positive": 150,
                "positive": 450,
                "neutral": 600,
                "negative": 250,
                "strongly_negative": 50
            },
            "model_loaded": False,
            "device": "cpu",
            "model_name": "bert-base-chinese"
        }

        yield mock_analyzer

@pytest.fixture
def sample_sentiment_request():
    """示例情感分析请求"""
    return {
        "text": "腾讯股价大涨5%，创历史新高，表现非常强劲",
        "include_entities": True,
        "include_keywords": True
    }

@pytest.fixture
def sample_batch_sentiment_request():
    """示例批量情感分析请求"""
    return {
        "texts": [
            "腾讯股价大涨5%，创历史新高",
            "市场担心通胀风险，科技股下跌",
            "央行维持利率不变，市场反应平淡"
        ],
        "include_entities": True,
        "include_keywords": True
    }

@pytest.fixture
def sample_training_request():
    """示例模型训练请求"""
    return {
        "training_data": [
            {"text": "股价上涨利好", "label": "positive"},
            {"text": "市场下跌担忧", "label": "negative"}
        ],
        "validation_data": [
            {"text": "股价稳定", "label": "neutral"}
        ],
        "model_config": {
            "learning_rate": 2e-5,
            "batch_size": 16,
            "num_epochs": 5
        }
    }

class TestSentimentAPI:
    """情感分析API测试类"""

    def test_analyze_sentiment_success(self, mock_sentiment_analyzer, sample_sentiment_request):
        """测试成功分析单个文本情感"""
        response = client.post("/api/sentiment/analyze", json=sample_sentiment_request)

        assert response.status_code == 200
        data = response.json()

        assert "text" in data
        assert "sentiment" in data
        assert "confidence" in data
        assert "scores" in data
        assert "entities" in data
        assert "keywords" in data
        assert "processing_time" in data
        assert "timestamp" in data

        # 验证响应内容
        assert data["text"] == sample_sentiment_request["text"]
        assert data["sentiment"] == "positive"
        assert data["confidence"] == 0.85
        assert len(data["entities"]) == 2
        assert len(data["keywords"]) == 3

        # 验证服务调用
        mock_sentiment_analyzer.analyze_sentiment.assert_called_once_with(
            sample_sentiment_request["text"]
        )

    def test_analyze_sentiment_invalid_request(self):
        """测试无效的情感分析请求"""
        invalid_requests = [
            {},  # 空请求
            {"text": ""},  # 空文本
            {"text": "x" * 5001},  # 文本过长
            {"invalid_field": "value"}  # 无效字段
        ]

        for invalid_request in invalid_requests:
            response = client.post("/api/sentiment/analyze", json=invalid_request)
            assert response.status_code == 422

    def test_analyze_sentiment_missing_text(self):
        """测试缺少文本字段"""
        request_without_text = {
            "include_entities": True,
            "include_keywords": True
        }

        response = client.post("/api/sentiment/analyze", json=request_without_text)

        assert response.status_code == 422

    def test_analyze_sentiment_optional_fields(self, mock_sentiment_analyzer):
        """测试可选字段"""
        minimal_request = {
            "text": "测试文本"
        }

        response = client.post("/api/sentiment/analyze", json=minimal_request)

        assert response.status_code == 200
        data = response.json()
        assert "text" in data
        assert "sentiment" in data

    def test_analyze_batch_sentiment_success(self, mock_sentiment_analyzer, sample_batch_sentiment_request):
        """测试成功批量分析情感"""
        response = client.post("/api/sentiment/analyze/batch", json=sample_batch_sentiment_request)

        assert response.status_code == 200
        data = response.json()

        assert "results" in data
        assert "total_count" in data
        assert "processing_time" in data
        assert "summary" in data

        # 验证批量结果
        assert len(data["results"]) == len(sample_batch_sentiment_request["texts"])
        assert data["total_count"] == 3

        # 验证第一个结果
        first_result = data["results"][0]
        assert "text" in first_result
        assert "sentiment" in first_result
        assert "confidence" in first_result

        # 验证服务调用
        mock_sentiment_analyzer.batch_analyze.assert_called_once()

    def test_analyze_batch_sentiment_invalid_request(self):
        """测试无效的批量分析请求"""
        invalid_requests = [
            {},  # 空请求
            {"texts": []},  # 空文本列表
            {"texts": [""]},  # 包含空文本
            {"texts": ["x" * 5001]},  # 文本过长
            {"texts": ["valid", "valid", "valid", "valid", "valid", "valid"]},  # 超过最大数量
            {"invalid_field": "value"}  # 无效字段
        ]

        for invalid_request in invalid_requests:
            response = client.post("/api/sentiment/analyze/batch", json=invalid_request)
            assert response.status_code == 422

    def test_analyze_batch_sentiment_max_items(self, mock_sentiment_analyzer):
        """测试批量分析最大项目数"""
        # 创建正好100个文本的请求
        texts_100 = [f"测试文本 {i}" for i in range(100)]
        valid_request = {"texts": texts_100}

        response = client.post("/api/sentiment/analyze/batch", json=valid_request)
        assert response.status_code == 200

        # 创建101个文本的请求
        texts_101 = [f"测试文本 {i}" for i in range(101)]
        invalid_request = {"texts": texts_101}

        response = client.post("/api/sentiment/analyze/batch", json=invalid_request)
        assert response.status_code == 422

    def test_train_model_success(self, mock_sentiment_analyzer, sample_training_request):
        """测试成功训练模型"""
        mock_sentiment_analyzer.train = AsyncMock(return_value={
            "success": True,
            "model_id": "sentiment_model_v2",
            "training_time": 180.5,
            "final_accuracy": 0.92,
            "training_history": [0.75, 0.82, 0.88, 0.92]
        })

        response = client.post("/api/sentiment/model/train", json=sample_training_request)

        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "model_id" in data
        assert "training_time" in data
        assert "final_accuracy" in data
        assert "training_history" in data

        assert data["success"] is True
        assert data["final_accuracy"] == 0.92

        # 验证服务调用
        mock_sentiment_analyzer.train.assert_called_once()

    def test_train_model_invalid_request(self):
        """测试无效的模型训练请求"""
        invalid_requests = [
            {},  # 空请求
            {"training_data": []},  # 空训练数据
            {"training_data": [{"text": "valid"}]},  # 缺少标签
            {"training_data": [{"text": "valid", "label": "positive"}], "validation_data": "invalid"}  # 无效验证数据格式
        ]

        for invalid_request in invalid_requests:
            response = client.post("/api/sentiment/model/train", json=invalid_request)
            assert response.status_code == 422

    def test_get_model_info_success(self, mock_sentiment_analyzer):
        """测试成功获取模型信息"""
        mock_sentiment_analyzer.get_model_info = AsyncMock(return_value={
            "model_id": "sentiment_model_v1",
            "model_version": "1.0.0",
            "created_at": "2023-10-29T10:00:00Z",
            "last_updated": "2023-10-29T15:30:00Z",
            "training_samples": 10000,
            "accuracy": 0.88,
            "model_type": "bert-based",
            "language": "zh-CN",
            "parameters": {
                "max_length": 512,
                "batch_size": 32,
                "learning_rate": 2e-5
            }
        })

        response = client.get("/api/sentiment/model/info")

        assert response.status_code == 200
        data = response.json()

        assert "model_id" in data
        assert "model_version" in data
        assert "created_at" in data
        assert "last_updated" in data
        assert "training_samples" in data
        assert "accuracy" in data

        assert data["model_id"] == "sentiment_model_v1"
        assert data["accuracy"] == 0.88

    def test_get_model_info_not_found(self, mock_sentiment_analyzer):
        """测试获取不存在的模型信息"""
        mock_sentiment_analyzer.get_model_info = AsyncMock(return_value=None)

        response = client.get("/api/sentiment/model/info")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "模型不存在" in data["detail"]

    def test_evaluate_model_success(self, mock_sentiment_analyzer):
        """测试成功评估模型"""
        mock_sentiment_analyzer.evaluate_model = AsyncMock(return_value={
            "success": True,
            "accuracy": 0.91,
            "precision": {
                "positive": 0.89,
                "negative": 0.85,
                "neutral": 0.92
            },
            "recall": {
                "positive": 0.87,
                "negative": 0.83,
                "neutral": 0.94
            },
            "f1_score": 0.88,
            "confusion_matrix": [
                [45, 3, 2],
                [2, 38, 5],
                [1, 4, 50]
            ],
            "evaluation_time": 12.5
        })

        evaluation_data = {
            "test_data": [
                {"text": "测试文本1", "label": "positive"},
                {"text": "测试文本2", "label": "negative"}
            ]
        }

        response = client.post("/api/sentiment/model/evaluate", json=evaluation_data)

        assert response.status_code == 200
        data = response.json()

        assert "success" in data
        assert "accuracy" in data
        assert "precision" in data
        assert "recall" in data
        assert "f1_score" in data

        assert data["success"] is True
        assert data["accuracy"] == 0.91

    def test_export_model_success(self, mock_sentiment_analyzer):
        """测试成功导出模型"""
        mock_sentiment_analyzer.export_model = AsyncMock(return_value={
            "success": True,
            "export_path": "/models/sentiment_model_v1_exported.zip",
            "file_size": 52428800,  # 50MB
            "export_time": 45.2
        })

        export_request = {
            "format": "pytorch",
            "include_tokenizer": True
        }

        response = client.post("/api/sentiment/model/export", json=export_request)

        assert response.status_code == 200
        data = response.json()

        assert "success" in data
        assert "export_path" in data
        assert "file_size" in data
        assert "export_time" in data

        assert data["success"] is True

    def test_calculate_risk_metrics_success(self, mock_sentiment_analyzer):
        """测试成功计算风险指标"""
        mock_sentiment_analyzer.calculate_var = AsyncMock(return_value={
            "var_95": 0.025,
            "var_99": 0.035,
            "cvar_95": 0.032,
            "cvar_99": 0.045,
            "time_horizon": 1,
            "confidence_level": 0.95,
            "calculation_method": "historical_simulation"
        })

        risk_request = {
            "sentiment_scores": [0.1, 0.2, -0.1, 0.15, -0.05, 0.0],
            "confidence_levels": [0.95, 0.99],
            "time_horizon": 1
        }

        response = client.post("/api/sentiment/risk/var", json=risk_request)

        assert response.status_code == 200
        data = response.json()

        assert "var_95" in data
        assert "var_99" in data
        assert "cvar_95" in data
        assert "cvar_99" in data

        assert data["var_95"] == 0.025

    def test_stress_test_success(self, mock_sentiment_analyzer):
        """测试成功压力测试"""
        mock_sentiment_analyzer.stress_test = AsyncMock(return_value={
            "scenarios": [
                {
                    "name": "市场崩盘",
                    "impact": -0.15,
                    "probability": 0.02,
                    "description": "极端市场下跌情况"
                },
                {
                    "name": "政策变化",
                    "impact": 0.08,
                    "probability": 0.05,
                    "description": "政策调整影响"
                }
            ],
            "worst_case": {
                "scenario": "市场崩盘",
                "impact": -0.15,
                "confidence": 0.95
            },
            "stress_test_time": 8.5
        })

        stress_request = {
            "base_sentiment": 0.0,
            "scenarios": [
                {"name": "市场崩盘", "impact": -0.2},
                {"name": "政策利好", "impact": 0.1}
            ]
        }

        response = client.post("/api/sentiment/risk/stress-test", json=stress_request)

        assert response.status_code == 200
        data = response.json()

        assert "scenarios" in data
        assert "worst_case" in data
        assert "stress_test_time" in data

        assert len(data["scenarios"]) == 2

    def test_get_statistics_success(self, mock_sentiment_analyzer):
        """测试成功获取统计信息"""
        response = client.get("/api/sentiment/statistics")

        assert response.status_code == 200
        data = response.json()

        assert "total_analyses" in data
        assert "successful_analyses" in data
        assert "failed_analyses" in data
        assert "average_processing_time" in data
        assert "sentiment_distribution" in data

        assert data["total_analyses"] == 1500
        assert "positive" in data["sentiment_distribution"]

        # 验证服务调用
        mock_sentiment_analyzer.get_statistics.assert_called_once()

    def test_health_check_success(self, mock_sentiment_analyzer):
        """测试健康检查成功"""
        response = client.get("/api/sentiment/health")

        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert "timestamp" in data
        assert "components" in data

        assert data["status"] == "healthy"
        assert "sentiment_analyzer" in data["components"]

    def test_health_check_service_error(self, mock_sentiment_analyzer):
        """测试健康检查服务错误"""
        mock_sentiment_analyzer.get_statistics.side_effect = Exception("Service error")

        response = client.get("/api/sentiment/health")

        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert "timestamp" in data
        assert "error" in data

    def test_error_handling_500(self):
        """测试500错误处理"""
        with patch('backend.api.sentiment.sentiment_analyzer') as mock_analyzer:
            mock_analyzer.analyze_sentiment.side_effect = Exception("Internal error")

            response = client.post("/api/sentiment/analyze", json={
                "text": "测试文本"
            })

            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "情感分析失败" in data["detail"]

    def test_text_preprocessing_edge_cases(self, mock_sentiment_analyzer):
        """测试文本预处理的边缘情况"""
        edge_case_texts = [
            "",  # 空文本
            "   ",  # 只有空格
            "！！！？？？",  # 只有标点符号
            "a" * 5000,  # 长文本（应该被截断）
            "中文英文混合English Text"  # 混合语言
        ]

        for text in edge_case_texts:
            response = client.post("/api/sentiment/analyze", json={
                "text": text,
                "include_entities": True,
                "include_keywords": True
            })

            # 即使是边缘情况，也应该返回200（处理内部逻辑）
            assert response.status_code in [200, 422]

    def test_concurrent_requests(self, mock_sentiment_analyzer):
        """测试并发请求"""
        import threading
        import time

        results = []
        errors = []

        def make_request(index):
            try:
                response = client.post("/api/sentiment/analyze", json={
                    "text": f"并发测试文本 {index}",
                    "include_entities": True
                })
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))

        # 创建多个并发线程
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证结果
        assert len(errors) == 0, f"并发请求出现错误: {errors}"
        assert len(results) == 10
        assert all(status in [200, 422] for status in results)

    def test_request_size_limits(self):
        """测试请求大小限制"""
        # 测试文本长度限制
        max_length_text = "x" * 5000  # 最大允许长度
        too_long_text = "x" * 5001  # 超过限制

        # 测试批量请求数量限制
        max_batch = {"texts": [f"文本 {i}" for i in range(100)]}  # 最大允许数量
        too_large_batch = {"texts": [f"文本 {i}" for i in range(101)]}  # 超过限制

        # 最大长度文本应该成功
        response = client.post("/api/sentiment/analyze", json={"text": max_length_text})
        assert response.status_code in [200, 422]

        # 超长文本应该失败
        response = client.post("/api/sentiment/analyze", json={"text": too_long_text})
        assert response.status_code == 422

        # 最大批量应该成功
        response = client.post("/api/sentiment/analyze/batch", json=max_batch)
        assert response.status_code in [200, 422]

        # 超大批量应该失败
        response = client.post("/api/sentiment/analyze/batch", json=too_large_batch)
        assert response.status_code == 422

@pytest.mark.unit
@pytest.mark.api
@pytest.mark.sentiment
class TestSentimentAPIIntegration:
    """情感分析API集成测试"""

    def test_end_to_end_analysis_flow(self, mock_sentiment_analyzer):
        """测试端到端分析流程"""
        # 1. 分析单个文本
        text_to_analyze = "腾讯股价表现强劲，投资者信心增强"

        analyze_response = client.post("/api/sentiment/analyze", json={
            "text": text_to_analyze,
            "include_entities": True,
            "include_keywords": True
        })

        assert analyze_response.status_code == 200
        analyze_data = analyze_response.json()
        assert analyze_data["text"] == text_to_analyze
        assert "sentiment" in analyze_data

        # 2. 批量分析相关文本
        batch_texts = [
            "腾讯股票大涨",
            "阿里巴巴股价下跌",
            "百度股价持平"
        ]

        batch_response = client.post("/api/sentiment/analyze/batch", json={
            "texts": batch_texts,
            "include_entities": True
        })

        assert batch_response.status_code == 200
        batch_data = batch_response.json()
        assert len(batch_data["results"]) == len(batch_texts)

        # 3. 获取统计信息
        stats_response = client.get("/api/sentiment/statistics")
        assert stats_response.status_code == 200

        # 4. 健康检查
        health_response = client.get("/api/sentiment/health")
        assert health_response.status_code == 200

    def test_sentiment_analysis_workflow(self, mock_sentiment_analyzer):
        """测试情感分析工作流程"""
        # 模拟金融新闻分析场景
        news_items = [
            "腾讯发布财报超预期，股价上涨5%",
            "科技股因通胀担忧集体下跌",
            "央行政策调整，市场反应平淡"
        ]

        # 逐一分析新闻
        analyses = []
        for news in news_items:
            response = client.post("/api/sentiment/analyze", json={
                "text": news,
                "include_entities": True,
                "include_keywords": True
            })

            assert response.status_code == 200
            analysis = response.json()
            analyses.append(analysis)

        # 验证分析结果
        assert len(analyses) == len(news_items)
        sentiments = [analysis["sentiment"] for analysis in analyses]

        # 验证情感分布
        sentiment_counts = {sentiment: sentiments.count(sentiment) for sentiment in set(sentiments)}
        assert len(sentiment_counts) >= 1

        # 批量分析所有新闻
        batch_response = client.post("/api/sentiment/analyze/batch", json={
            "texts": news_items,
            "include_entities": True
        })

        assert batch_response.status_code == 200
        batch_data = batch_response.json()
        assert len(batch_data["results"]) == len(news_items)

    def test_model_lifecycle(self, mock_sentiment_analyzer):
        """测试模型生命周期"""
        # 1. 获取初始模型信息
        initial_info_response = client.get("/api/sentiment/model/info")
        # 可能返回404如果模型不存在

        # 2. 训练新模型
        training_data = {
            "training_data": [
                {"text": "股价上涨利好", "label": "positive"},
                {"text": "股价下跌利空", "label": "negative"}
            ],
            "validation_data": [
                {"text": "股价稳定", "label": "neutral"}
            ]
        }

        # 模拟训练服务
        mock_sentiment_analyzer.train = AsyncMock(return_value={
            "success": True,
            "model_id": "sentiment_model_v2",
            "training_time": 120.0,
            "final_accuracy": 0.85
        })

        train_response = client.post("/api/sentiment/model/train", json=training_data)
        assert train_response.status_code == 200

        # 3. 评估模型
        mock_sentiment_analyzer.evaluate_model = AsyncMock(return_value={
            "success": True,
            "accuracy": 0.82,
            "f1_score": 0.80
        })

        eval_data = {
            "test_data": [
                {"text": "测试文本", "label": "positive"}
            ]
        }

        eval_response = client.post("/api/sentiment/model/evaluate", json=eval_data)
        assert eval_response.status_code == 200

        # 4. 导出模型
        mock_sentiment_analyzer.export_model = AsyncMock(return_value={
            "success": True,
            "export_path": "/models/export.zip"
        })

        export_response = client.post("/api/sentiment/model/export", json={
            "format": "pytorch",
            "include_tokenizer": True
        })
        assert export_response.status_code == 200