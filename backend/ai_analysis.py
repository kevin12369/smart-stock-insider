"""
AI分析数据模型

Author: Smart Stock Insider Team
Version: 1.0.0
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AIAnalysis(Base):
    """AI分析记录"""
    __tablename__ = "ai_analysis"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    symbol = Column(String(10), nullable=False, index=True, comment="股票代码")
    role = Column(String(50), nullable=False, index=True, comment="分析师角色")
    question = Column(Text, nullable=False, comment="分析问题")
    answer = Column(Text, nullable=False, comment="AI回答")
    confidence = Column(Float, nullable=False, default=0.0, comment="置信度")
    reasoning = Column(Text, nullable=True, comment="推理过程")
    suggestions = Column(JSON, nullable=True, comment="建议列表")
    analysis_metadata = Column(JSON, nullable=True, comment="元数据")
    context = Column(JSON, nullable=True, comment="分析上下文")
    data = Column(JSON, nullable=True, comment="分析数据")
    processing_time = Column(Float, nullable=True, comment="处理时间(秒)")
    tokens_used = Column(Integer, nullable=True, comment="使用的token数量")
    model_name = Column(String(100), nullable=True, comment="使用的模型名称")
    user_id = Column(String(100), nullable=True, index=True, comment="用户ID")
    session_id = Column(String(100), nullable=True, index=True, comment="会话ID")
    status = Column(String(20), nullable=False, default="completed", comment="状态")
    error_message = Column(Text, nullable=True, comment="错误信息")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关联
    feedback = relationship("AIAnalysisFeedback", back_populates="analysis", cascade="all, delete-orphan")

    # 索引
    __table_args__ = (
        Index('idx_ai_analysis_symbol_role', 'symbol', 'role'),
        Index('idx_ai_analysis_created_at', 'created_at'),
        Index('idx_ai_analysis_user_session', 'user_id', 'session_id'),
        {'comment': 'AI分析记录表'}
    )

    def __repr__(self):
        return f"<AIAnalysis(id={self.id}, symbol={self.symbol}, role={self.role})>"


class AIAnalysisFeedback(Base):
    """AI分析反馈"""
    __tablename__ = "ai_analysis_feedback"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    analysis_id = Column(Integer, ForeignKey("ai_analysis.id"), nullable=False, comment="分析记录ID")
    rating = Column(Integer, nullable=False, comment="评分(1-5)")
    feedback_text = Column(Text, nullable=True, comment="反馈内容")
    helpful = Column(Integer, nullable=False, default=1, comment="是否有用(1有用, 0无用)")
    category = Column(String(50), nullable=True, comment="反馈类别")
    user_id = Column(String(100), nullable=True, index=True, comment="用户ID")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment="创建时间")

    # 关联
    analysis = relationship("AIAnalysis", back_populates="feedback")

    # 索引
    __table_args__ = (
        Index('idx_ai_feedback_analysis_id', 'analysis_id'),
        Index('idx_ai_feedback_user_id', 'user_id'),
        {'comment': 'AI分析反馈表'}
    )

    def __repr__(self):
        return f"<AIAnalysisFeedback(id={self.id}, analysis_id={self.analysis_id}, rating={self.rating})>"


class AIAnalysisSession(Base):
    """AI分析会话"""
    __tablename__ = "ai_analysis_session"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(100), nullable=False, unique=True, index=True, comment="会话ID")
    user_id = Column(String(100), nullable=True, index=True, comment="用户ID")
    title = Column(String(200), nullable=True, comment="会话标题")
    symbols = Column(JSON, nullable=True, comment="涉及的股票代码列表")
    roles_used = Column(JSON, nullable=True, comment="使用的分析师角色")
    message_count = Column(Integer, nullable=False, default=0, comment="消息数量")
    total_tokens = Column(Integer, nullable=False, default=0, comment="总token使用量")
    is_active = Column(Integer, nullable=False, default=1, comment="是否活跃(1活跃, 0结束)")
    last_activity = Column(DateTime, nullable=False, default=datetime.utcnow, comment="最后活动时间")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 索引
    __table_args__ = (
        Index('idx_ai_session_user_id', 'user_id'),
        Index('idx_ai_session_last_activity', 'last_activity'),
        {'comment': 'AI分析会话表'}
    )

    def __repr__(self):
        return f"<AIAnalysisSession(id={self.id}, session_id={self.session_id}, user_id={self.user_id})>"


class AIAnalysisTemplate(Base):
    """AI分析模板"""
    __tablename__ = "ai_analysis_template"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="模板名称")
    description = Column(Text, nullable=True, comment="模板描述")
    role = Column(String(50), nullable=False, index=True, comment="分析师角色")
    question_template = Column(Text, nullable=False, comment="问题模板")
    variables = Column(JSON, nullable=True, comment="模板变量")
    category = Column(String(50), nullable=True, index=True, comment="模板分类")
    tags = Column(JSON, nullable=True, comment="标签列表")
    usage_count = Column(Integer, nullable=False, default=0, comment="使用次数")
    rating = Column(Float, nullable=True, comment="平均评分")
    is_public = Column(Integer, nullable=False, default=1, comment="是否公开(1公开, 0私有)")
    created_by = Column(String(100), nullable=True, index=True, comment="创建者ID")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 索引
    __table_args__ = (
        Index('idx_ai_template_role', 'role'),
        Index('idx_ai_template_category', 'category'),
        Index('idx_ai_template_public', 'is_public'),
        {'comment': 'AI分析模板表'}
    )

    def __repr__(self):
        return f"<AIAnalysisTemplate(id={self.id}, name={self.name}, role={self.role})>"


class AIAnalysisCache(Base):
    """AI分析缓存"""
    __tablename__ = "ai_analysis_cache"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cache_key = Column(String(255), nullable=False, unique=True, index=True, comment="缓存键")
    symbol = Column(String(10), nullable=False, index=True, comment="股票代码")
    role = Column(String(50), nullable=False, index=True, comment="分析师角色")
    question_hash = Column(String(64), nullable=False, index=True, comment="问题哈希")
    answer = Column(Text, nullable=False, comment="AI回答")
    confidence = Column(Float, nullable=False, default=0.0, comment="置信度")
    analysis_metadata = Column(JSON, nullable=True, comment="元数据")
    expires_at = Column(DateTime, nullable=False, comment="过期时间")
    hit_count = Column(Integer, nullable=False, default=0, comment="命中次数")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 索引
    __table_args__ = (
        Index('idx_ai_cache_symbol_role', 'symbol', 'role'),
        Index('idx_ai_cache_question_hash', 'question_hash'),
        Index('idx_ai_cache_expires_at', 'expires_at'),
        {'comment': 'AI分析缓存表'}
    )

    def __repr__(self):
        return f"<AIAnalysisCache(id={self.id}, cache_key={self.cache_key}, symbol={self.symbol})>"