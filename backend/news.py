"""
新闻数据模型

Author: Smart Stock Insider Team
Version: 1.0.0
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, Text,
    Index, ForeignKey
)
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class NewsSource(Base):
    """新闻来源表"""
    __tablename__ = "news_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, comment="来源名称")
    url = Column(String(500), comment="来源URL")
    description = Column(Text, comment="来源描述")
    language = Column(String(10), default="zh-CN", comment="语言")
    country = Column(String(10), comment="国家")
    category = Column(String(50), comment="类别")
    is_active = Column(Boolean, default=True, comment="是否活跃")
    last_fetch = Column(DateTime, comment="最后抓取时间")
    fetch_interval = Column(Integer, default=300, comment="抓取间隔(秒)")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    news = relationship("News", back_populates="source")

    # 索引
    __table_args__ = (
        Index('idx_source_name', 'name'),
        Index('idx_source_active', 'is_active'),
        Index('idx_source_category', 'category'),
        Index('idx_source_last_fetch', 'last_fetch'),
    )

    def __repr__(self):
        return f"<NewsSource(name={self.name}, active={self.is_active})>"


class News(Base):
    """新闻表"""
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("news_sources.id"), nullable=False, comment="来源ID")
    title = Column(String(500), nullable=False, comment="标题")
    content = Column(Text, comment="内容")
    summary = Column(Text, comment="摘要")
    url = Column(String(1000), unique=True, nullable=False, comment="原文URL")
    author = Column(String(100), comment="作者")
    publish_time = Column(DateTime, nullable=False, comment="发布时间")
    fetch_time = Column(DateTime, default=datetime.utcnow, comment="抓取时间")
    category = Column(String(50), comment="分类")
    tags = Column(String(500), comment="标签，逗号分隔")
    language = Column(String(10), default="zh-CN", comment="语言")
    word_count = Column(Integer, comment="字数")
    read_count = Column(Integer, default=0, comment="阅读次数")
    is_deleted = Column(Boolean, default=False, comment="是否已删除")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    source = relationship("NewsSource", back_populates="news")
    sentiments = relationship("NewsSentiment", back_populates="news", cascade="all, delete-orphan")
    entities = relationship("NewsEntity", back_populates="news", cascade="all, delete-orphan")

    # 索引
    __table_args__ = (
        Index('idx_news_publish_time', 'publish_time'),
        Index('idx_news_fetch_time', 'fetch_time'),
        Index('idx_news_category', 'category'),
        Index('idx_news_source', 'source_id'),
        Index('idx_news_deleted', 'is_deleted'),
        Index('idx_news_title_fulltext', 'title'),
    )

    def __repr__(self):
        return f"<News(id={self.id}, title={self.title[:50]}..., source={self.source.name if self.source else None})>"


class NewsSentiment(Base):
    """新闻情感分析表"""
    __tablename__ = "news_sentiments"

    id = Column(Integer, primary_key=True, index=True)
    news_id = Column(Integer, ForeignKey("news.id"), nullable=False, comment="新闻ID")
    model_name = Column(String(50), nullable=False, comment="分析模型名称")
    sentiment_label = Column(String(20), nullable=False, comment="情感标签")
    sentiment_score = Column(Float, nullable=False, comment="情感分数")
    confidence = Column(Float, comment="置信度")
    positive_prob = Column(Float, comment="积极概率")
    negative_prob = Column(Float, comment="消极概率")
    neutral_prob = Column(Float, comment="中性概率")
    analysis_time = Column(DateTime, default=datetime.utcnow, comment="分析时间")
    metadata_json = Column(Text, comment="额外数据JSON")

    # 关系
    news = relationship("News", back_populates="sentiments")

    # 复合索引
    __table_args__ = (
        UniqueConstraint('news_id', 'model_name', name='uq_news_sentiment_model'),
        Index('idx_sentiment_news', 'news_id'),
        Index('idx_sentiment_label', 'sentiment_label'),
        Index('idx_sentiment_score', 'sentiment_score'),
        Index('idx_sentiment_analysis_time', 'analysis_time'),
    )

    def __repr__(self):
        return f"<NewsSentiment(news_id={self.news_id}, label={self.sentiment_label}, score={self.sentiment_score})>"


class NewsEntity(Base):
    """新闻实体表"""
    __tablename__ = "news_entities"

    id = Column(Integer, primary_key=True, index=True)
    news_id = Column(Integer, ForeignKey("news.id"), nullable=False, comment="新闻ID")
    entity_text = Column(String(100), nullable=False, comment="实体文本")
    entity_type = Column(String(50), nullable=False, comment="实体类型")
    entity_subtype = Column(String(50), comment="实体子类型")
    start_position = Column(Integer, comment="开始位置")
    end_position = Column(Integer, comment="结束位置")
    confidence = Column(Float, comment="置信度")
    metadata_json = Column(Text, comment="额外数据JSON")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关系
    news = relationship("News", back_populates="entities")

    # 索引
    __table_args__ = (
        Index('idx_entity_news', 'news_id'),
        Index('idx_entity_type', 'entity_type'),
        Index('idx_entity_text', 'entity_text'),
        Index('idx_entity_subtype', 'entity_subtype'),
    )

    def __repr__(self):
        return f"<NewsEntity(news_id={self.news_id}, text={self.entity_text}, type={self.entity_type})>"


class NewsCategory(Base):
    """新闻分类表"""
    __tablename__ = "news_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, comment="分类名称")
    code = Column(String(20), unique=True, nullable=False, comment="分类代码")
    parent_code = Column(String(20), comment="父分类代码")
    level = Column(Integer, default=1, comment="层级")
    description = Column(Text, comment="分类描述")
    is_active = Column(Boolean, default=True, comment="是否活跃")
    sort_order = Column(Integer, default=0, comment="排序")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 索引
    __table_args__ = (
        Index('idx_category_code', 'code'),
        Index('idx_category_parent', 'parent_code'),
        Index('idx_category_level', 'level'),
        Index('idx_category_active', 'is_active'),
        Index('idx_category_sort', 'sort_order'),
    )

    def __repr__(self):
        return f"<NewsCategory(code={self.code}, name={self.name})>"


class NewsTag(Base):
    """新闻标签表"""
    __tablename__ = "news_tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, comment="标签名称")
    color = Column(String(10), comment="标签颜色")
    description = Column(Text, comment="标签描述")
    usage_count = Column(Integer, default=0, comment="使用次数")
    is_active = Column(Boolean, default=True, comment="是否活跃")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 索引
    __table_args__ = (
        Index('idx_tag_name', 'name'),
        Index('idx_tag_usage', 'usage_count'),
        Index('idx_tag_active', 'is_active'),
    )

    def __repr__(self):
        return f"<NewsTag(name={self.name}, usage={self.usage_count})>"


class NewsStockRelation(Base):
    """新闻股票关联表"""
    __tablename__ = "news_stock_relations"

    id = Column(Integer, primary_key=True, index=True)
    news_id = Column(Integer, ForeignKey("news.id"), nullable=False, comment="新闻ID")
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False, comment="股票ID")
    relevance_score = Column(Float, comment="相关性分数")
    mention_type = Column(String(20), comment="提及类型")
    mention_count = Column(Integer, default=1, comment="提及次数")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关系
    news = relationship("News")
    stock = relationship("Stock")

    # 复合索引
    __table_args__ = (
        UniqueConstraint('news_id', 'stock_id', name='uq_news_stock_relation'),
        Index('idx_relation_news', 'news_id'),
        Index('idx_relation_stock', 'stock_id'),
        Index('idx_relation_score', 'relevance_score'),
    )

    def __repr__(self):
        return f"<NewsStockRelation(news_id={self.news_id}, stock_id={self.stock_id}, score={self.relevance_score})>"