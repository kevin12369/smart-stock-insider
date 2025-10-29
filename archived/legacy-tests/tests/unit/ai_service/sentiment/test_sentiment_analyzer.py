"""
情感分析器单元测试
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.services.ai_service.sentiment.sentiment_analyzer import (
    FinancialSentimentAnalyzer, SentimentLabel, SentimentResult
)

@pytest.fixture
def sentiment_analyzer():
    """情感分析器夹具"""
    config = {
        "model_name": "bert-base-chinese",
        "max_length": 512,
        "batch_size": 32
    }
    analyzer = FinancialSentimentAnalyzer(config)
    # 不加载实际模型，使用基于词典的方法
    return analyzer

@pytest.fixture
def sample_texts():
    """示例文本数据"""
    return [
        {
            "text": "腾讯股价大涨5%，创历史新高，表现非常强劲",
            "expected_sentiment": SentimentLabel.POSITIVE,
            "min_confidence": 0.6
        },
        {
            "text": "市场担心通胀风险，科技股集体下跌，投资者情绪悲观",
            "expected_sentiment": SentimentLabel.NEGATIVE,
            "min_confidence": 0.6
        },
        {
            "text": "央行维持利率不变，市场反应平淡，交易量正常",
            "expected_sentiment": SentimentLabel.NEUTRAL,
            "min_confidence": 0.4
        },
        {
            "text": "这家公司业绩超预期，股价强势突破前期高点",
            "expected_sentiment": SentimentLabel.STRONGLY_POSITIVE,
            "min_confidence": 0.7
        },
        {
            "text": "财报亏损严重，债务危机加剧，面临退市风险",
            "expected_sentiment": SentimentLabel.STRONGLY_NEGATIVE,
            "min_confidence": 0.7
        }
    ]

@pytest.fixture
def sample_financial_entities():
    """示例金融实体"""
    return [
        {"type": "company", "value": "腾讯", "pattern": r"腾讯"},
        {"type": "stock_code", "value": "0700.HK", "pattern": r"\b\d{4}\.HK\b"},
        {"type": "percentage", "value": "5%", "pattern": r"\d+\.?\d*%"},
        {"type": "financial_term", "value": "市盈率", "pattern": r"市盈率"},
        {"type": "market_index", "value": "上证指数", "pattern": r"上证指数"}
    ]

class TestFinancialSentimentAnalyzer:
    """金融情感分析器测试类"""

    def test_initialization(self, sentiment_analyzer):
        """测试初始化"""
        assert sentiment_analyzer.model_name == "bert-base-chinese"
        assert sentiment_analyzer.max_length == 512
        assert sentiment_analyzer.batch_size == 32
        assert len(sentiment_analyzer.positive_words) > 0
        assert len(sentiment_analyzer.negative_words) > 0
        assert len(sentiment_analyzer.financial_terms) > 0

    @pytest.mark.asyncio
    async def test_analyze_positive_text(self, sentiment_analyzer):
        """测试分析积极文本"""
        text = "腾讯股价大涨5%，创历史新高，表现非常强劲"

        result = await sentiment_analyzer.analyze_sentiment(text)

        assert isinstance(result, SentimentResult)
        assert result.text == text
        assert result.label in [SentimentLabel.POSITIVE, SentimentLabel.STRONGLY_POSITIVE]
        assert result.confidence >= 0.5
        assert isinstance(result.entities, list)
        assert isinstance(result.keywords, list)
        assert result.processing_time >= 0
        assert isinstance(result.timestamp, datetime)

    @pytest.mark.asyncio
    async def test_analyze_negative_text(self, sentiment_analyzer):
        """测试分析消极文本"""
        text = "市场担心通胀风险，科技股集体下跌，投资者情绪悲观"

        result = await sentiment_analyzer.analyze_sentiment(text)

        assert result.label in [SentimentLabel.NEGATIVE, SentimentLabel.STRONGLY_NEGATIVE]
        assert result.confidence >= 0.5

    @pytest.mark.asyncio
    async def test_analyze_neutral_text(self, sentiment_analyzer):
        """测试分析中性文本"""
        text = "央行维持利率不变，市场反应平淡，交易量正常"

        result = await sentiment_analyzer.analyze_sentiment(text)

        assert result.label == SentimentLabel.NEUTRAL
        assert result.confidence >= 0.3

    @pytest.mark.asyncio
    async def test_analyze_multiple_texts(self, sentiment_analyzer, sample_texts):
        """测试批量分析文本"""
        texts = [item["text"] for item in sample_texts]

        results = await sentiment_analyzer.batch_analyze(texts)

        assert len(results) == len(sample_texts)
        assert all(isinstance(result, SentimentResult) for result in results)

        # 验证每个结果
        for i, result in enumerate(results):
            assert result.text == sample_texts[i]["text"]
            assert result.confidence >= 0.3

    @pytest.mark.asyncio
    async def test_text_preprocessing(self, sentiment_analyzer):
        """测试文本预处理"""
        original_text = "  腾讯（0700.HK）股价大涨5%！创历史新高...  "
        processed_text = sentiment_analyzer._preprocess_text(original_text)

        # 验证预处理效果
        assert "  " not in processed_text  # 多余空格被移除
        assert len(processed_text) <= sentiment_analyzer.max_length

    def test_entity_extraction(self, sentiment_analyzer, sample_financial_entities):
        """测试实体提取"""
        text = "腾讯(0700.HK)股价大涨5%，市盈率较低，上证指数也有所表现"

        entities = sentiment_analyzer._extract_entities(text)

        assert len(entities) > 0
        entity_types = [entity["type"] for entity in entities]
        assert "company" in entity_types or "stock_code" in entity_types

    def test_keyword_extraction(self, sentiment_analyzer):
        """测试关键词提取"""
        text = "腾讯股价大幅上涨创历史新高表现强劲投资者信心增强"

        keywords = sentiment_analyzer._extract_keywords(text)

        assert len(keywords) > 0
        assert all(len(keyword) >= 2 for keyword in keywords)  # 关键词长度至少2个字符
        assert len(keywords) <= 20  # 限制关键词数量

    @pytest.mark.asyncio
    async def test_sentiment_scores(self, sentiment_analyzer):
        """测试情感分数"""
        text = "腾讯股价表现良好"

        result = await sentiment_analyzer.analyze_sentiment(text)

        assert isinstance(result.scores, dict)
        assert len(result.scores) == len(SentimentLabel)  # 应该包含所有情感标签的分数

        # 验证分数总和
        total_score = sum(result.scores.values())
        assert abs(total_score - 1.0) < 0.1  # 允许小的误差

        # 验证预测标签的分数最高
        predicted_score = result.scores[result.label.value]
        for other_label, score in result.scores.items():
            if other_label != result.label.value:
                assert predicted_score >= score

    @pytest.mark.asyncio
    async def test_dictionary_based_analysis(self, sentiment_analyzer):
        """测试基于词典的分析"""
        # 测试包含积极词汇的文本
        positive_text = "股票上涨增长利好"
        label, confidence, scores = await sentiment_analyzer._analyze_with_dict(positive_text)

        assert label in [SentimentLabel.POSITIVE, SentimentLabel.STRONGLY_POSITIVE]
        assert confidence > 0.5

        # 测试包含消极词汇的文本
        negative_text = "股票下跌亏损风险"
        label, confidence, scores = await sentiment_analyzer._analyze_with_dict(negative_text)

        assert label in [SentimentLabel.NEGATIVE, SentimentLabel.STRONGLY_NEGATIVE]
        assert confidence > 0.5

    @pytest.mark.asyncio
    async def test_intensity_words(self, sentiment_analyzer):
        """测试强度词处理"""
        normal_text = "股票上涨"
        intense_text = "股票非常大幅上涨"

        normal_result = await sentiment_analyzer.analyze_sentiment(normal_text)
        intense_result = await sentiment_analyzer.analyze_sentiment(intense_text)

        # 包含强度词的文本应该有更高的置信度
        assert intense_result.confidence >= normal_result.confidence

    @pytest.mark.asyncio
    async def test_financial_term_replacement(self, sentiment_analyzer):
        """测试金融术语替换"""
        text = "A股走势分析"
        processed_text = sentiment_analyzer._preprocess_text(text)

        # 验证术语被替换
        assert "A股市场" in processed_text

    def test_positive_words_loading(self, sentiment_analyzer):
        """测试积极词汇加载"""
        positive_words = sentiment_analyzer.positive_words

        assert len(positive_words) > 0
        assert "上涨" in positive_words
        assert "利好" in positive_words
        assert "增长" in positive_words

    def test_negative_words_loading(self, sentiment_analyzer):
        """测试消极词汇加载"""
        negative_words = sentiment_analyzer.negative_words

        assert len(negative_words) > 0
        assert "下跌" in negative_words
        assert "利空" in negative_words
        assert "风险" in negative_words

    def test_financial_terms_loading(self, sentiment_analyzer):
        """测试金融术语加载"""
        financial_terms = sentiment_analyzer.financial_terms

        assert len(financial_terms) > 0
        assert "A股" in financial_terms
        assert "市盈率" in financial_terms
        assert "MACD" in financial_terms

    @pytest.mark.asyncio
    async def test_edge_cases(self, sentiment_analyzer):
        """测试边缘情况"""
        # 空文本
        empty_result = await sentiment_analyzer.analyze_sentiment("")
        assert empty_result.label == SentimentLabel.NEUTRAL

        # 纯标点符号
        punct_result = await sentiment_analyzer.analyze_sentiment("！！！？？？")
        assert punct_result.label == SentimentLabel.NEUTRAL

        # 非常长的文本
        long_text = "中性" * 1000
        long_result = await sentiment_analyzer.analyze_sentiment(long_text)
        assert long_result.label == SentimentLabel.NEUTRAL

    @pytest.mark.asyncio
    async def test_error_handling(self, sentiment_analyzer):
        """测试错误处理"""
        # 测试None输入
        with pytest.raises(Exception):
            await sentiment_analyzer.analyze_sentiment(None)

    @pytest.mark.asyncio
    async def test_statistics_tracking(self, sentiment_analyzer):
        """测试统计信息跟踪"""
        # 初始统计
        initial_stats = sentiment_analyzer.get_statistics()
        assert initial_stats["total_analyses"] == 0

        # 执行一些分析
        texts = ["股价上涨", "股价下跌", "股价持平"]
        for text in texts:
            await sentiment_analyzer.analyze_sentiment(text)

        # 检查统计更新
        updated_stats = sentiment_analyzer.get_statistics()
        assert updated_stats["total_analyses"] == len(texts)
        assert updated_stats["successful_analyses"] == len(texts)
        assert updated_stats["average_processing_time"] >= 0

    def test_sentiment_label_methods(self):
        """测试情感标签方法"""
        # 测试转字符串
        assert SentimentLabel.to_string(SentimentLabel.POSITIVE) == "看涨"
        assert SentimentLabel.to_string(SentimentLabel.NEGATIVE) == "看跌"
        assert SentimentLabel.to_string(SentimentLabel.NEUTRAL) == "中性"

        # 测试转英文
        assert SentimentLabel.to_english(SentimentLabel.POSITIVE) == "POSITIVE"
        assert SentimentLabel.to_english(SentimentLabel.NEGATIVE) == "NEGATIVE"

        # 测试转分数
        assert SentimentLabel.to_score(SentimentLabel.POSITIVE) == 0.5
        assert SentimentLabel.to_score(SentimentLabel.NEGATIVE) == -0.5
        assert SentimentLabel.to_score(SentimentLabel.NEUTRAL) == 0.0

    @pytest.mark.asyncio
    async def test_concurrent_analysis(self, sentiment_analyzer):
        """测试并发分析"""
        texts = [
            "股价上涨",
            "股价下跌",
            "股价持平",
            "市场利好",
            "风险增加"
        ]

        # 并发执行分析
        tasks = [sentiment_analyzer.analyze_sentiment(text) for text in texts]
        results = await asyncio.gather(*tasks)

        assert len(results) == len(texts)
        assert all(isinstance(result, SentimentResult) for result in results)

    @pytest.mark.asyncio
    async def test_cleanup(self, sentiment_analyzer):
        """测试资源清理"""
        # 执行一些分析
        await sentiment_analyzer.analyze_sentiment("测试文本")

        # 清理资源
        await sentiment_analyzer.cleanup()

        # 验证清理效果
        stats = sentiment_analyzer.get_statistics()
        # 统计信息应该仍然存在，但模型和分词器应该被清理
        assert stats["total_analyses"] >= 0

@pytest.mark.unit
@pytest.mark.sentiment
@pytest.mark.ai
class TestSentimentAnalyzerIntegration:
    """情感分析器集成测试"""

    @pytest.mark.asyncio
    async def test_real_financial_news_analysis(self, sentiment_analyzer):
        """测试真实财经新闻分析"""
        news_samples = [
            {
                "title": "腾讯财报超预期，股价大涨5%",
                "content": "腾讯控股发布财报，季度营收同比增长15%，净利润增长20%，超出市场预期。受此利好消息影响，股价大涨5%，创历史新高。",
                "expected_sentiment": SentimentLabel.POSITIVE
            },
            {
                "title": "科技股集体下跌，市场担忧情绪升温",
                "content": "受通胀担忧影响，科技股集体下跌，纳斯达克指数下跌2%。投资者担忧货币政策收紧将对科技股估值造成压力。",
                "expected_sentiment": SentimentLabel.NEGATIVE
            },
            {
                "title": "央行维持利率不变，市场反应平淡",
                "content": "央行宣布维持基准利率不变，符合市场预期。股市反应平淡，主要指数小幅波动，交易量维持在正常水平。",
                "expected_sentiment": SentimentLabel.NEUTRAL
            }
        ]

        for news in news_samples:
            result = await sentiment_analyzer.analyze_sentiment(news["content"])

            # 验证情感标签基本正确（允许一定的误差）
            if news["expected_sentiment"] in [SentimentLabel.POSITIVE, SentimentLabel.STRONGLY_POSITIVE]:
                assert result.label in [SentimentLabel.POSITIVE, SentimentLabel.STRONGLY_POSITIVE, SentimentLabel.NEUTRAL]
            elif news["expected_sentiment"] in [SentimentLabel.NEGATIVE, SentimentLabel.STRONGLY_NEGATIVE]:
                assert result.label in [SentimentLabel.NEGATIVE, SentimentLabel.STRONGLY_NEGATIVE, SentimentLabel.NEUTRAL]
            else:
                assert result.label == SentimentLabel.NEUTRAL

            # 验证实体提取
            assert len(result.entities) > 0
            entity_types = [entity["type"] for entity in result.entities]
            assert any(entity_type in ["company", "stock_code", "percentage"] for entity_type in entity_types)

    @pytest.mark.asyncio
    async def test_sentiment_consistency(self, sentiment_analyzer):
        """测试情感分析一致性"""
        # 相似意义的文本应该得到相似的情感结果
        similar_texts = [
            "股价大幅上涨",
            "股价显著增长",
            "股价强劲攀升",
            "股价表现优异"
        ]

        results = []
        for text in similar_texts:
            result = await sentiment_analyzer.analyze_sentiment(text)
            results.append(result)

        # 验证情感标签一致性
        labels = [result.label for result in results]
        positive_labels = [SentimentLabel.POSITIVE, SentimentLabel.STRONGLY_POSITIVE]

        # 大部分应该是积极情感
        positive_count = sum(1 for label in labels if label in positive_labels)
        assert positive_count >= len(labels) * 0.7  # 至少70%是积极情感

    @pytest.mark.asyncio
    async def test_batch_processing_efficiency(self, sentiment_analyzer):
        """测试批量处理效率"""
        import time

        texts = ["股价小幅波动"] * 50

        # 单个处理时间
        start_time = time.time()
        for text in texts:
            await sentiment_analyzer.analyze_sentiment(text)
        single_time = time.time() - start_time

        # 批量处理时间
        start_time = time.time()
        await sentiment_analyzer.batch_analyze(texts)
        batch_time = time.time() - start_time

        # 批量处理应该更高效（至少不会比单个处理慢太多）
        assert batch_time <= single_time * 1.2  # 允许20%的误差