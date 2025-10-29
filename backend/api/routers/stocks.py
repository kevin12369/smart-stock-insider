"""
股票数据API路由

Author: Smart Stock Insider Team
Version: 1.0.0
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from services.data_service.stock_service import stock_service
from schemas.stock import (
    StockInfoResponse,
    StockPriceResponse,
    StockKLineRequest,
    StockKLineResponse,
    StockRealtimeRequest,
    StockRealtimeResponse
)

router = APIRouter()


@router.get("/list", response_model=List[StockInfoResponse])
async def get_stock_list(
    market: Optional[str] = Query(None, description="市场代码，如 SH, SZ"),
    sector: Optional[str] = Query(None, description="行业板块"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取股票列表

    - **market**: 市场代码 (SH=上海, SZ=深圳)
    - **sector**: 行业板块
    - **page**: 页码，从1开始
    - **size**: 每页数量，最大100
    """
    try:
        result = await stock_service.get_stock_list(
            market=market,
            sector=sector,
            page=page,
            size=size,
            db=db
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取股票列表失败: {str(e)}")


@router.get("/search", response_model=List[StockInfoResponse])
async def search_stocks(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    limit: int = Query(10, ge=1, le=50, description="返回结果数量限制"),
    db: AsyncSession = Depends(get_db)
):
    """
    搜索股票

    - **keyword**: 搜索关键词（股票代码或名称）
    - **limit**: 返回结果数量限制，最大50
    """
    try:
        result = await stock_service.search_stocks(
            keyword=keyword,
            limit=limit,
            db=db
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索股票失败: {str(e)}")


@router.get("/{symbol}/info", response_model=StockInfoResponse)
async def get_stock_info(
    symbol: str,
    db: AsyncSession = Depends(get_db)
):
    """
    获取股票基本信息

    - **symbol**: 股票代码（如 000001.SZ）
    """
    try:
        result = await stock_service.get_stock_info(symbol=symbol, db=db)
        if not result:
            raise HTTPException(status_code=404, detail="股票信息未找到")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取股票信息失败: {str(e)}")


@router.get("/{symbol}/price", response_model=StockPriceResponse)
async def get_stock_price(
    symbol: str,
    db: AsyncSession = Depends(get_db)
):
    """
    获取股票当前价格

    - **symbol**: 股票代码
    """
    try:
        result = await stock_service.get_current_price(symbol=symbol, db=db)
        if not result:
            raise HTTPException(status_code=404, detail="股票价格信息未找到")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取股票价格失败: {str(e)}")


@router.post("/{symbol}/kline", response_model=StockKLineResponse)
async def get_stock_kline(
    symbol: str,
    request: StockKLineRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    获取股票K线数据

    - **symbol**: 股票代码
    - **period**: K线周期 (1min, 5min, 15min, 30min, 1hour, 1day, 1week, 1month)
    - **start_date**: 开始日期
    - **end_date**: 结束日期
    - **limit**: 数据条数限制
    """
    try:
        result = await stock_service.get_kline_data(
            symbol=symbol,
            period=request.period,
            start_date=request.start_date,
            end_date=request.end_date,
            limit=request.limit,
            db=db
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取K线数据失败: {str(e)}")


@router.post("/realtime", response_model=List[StockRealtimeResponse])
async def get_realtime_data(
    request: StockRealtimeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    获取股票实时数据

    - **symbols**: 股票代码列表
    """
    try:
        if not request.symbols:
            raise HTTPException(status_code=400, detail="股票代码列表不能为空")

        result = await stock_service.get_realtime_data(
            symbols=request.symbols,
            db=db
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取实时数据失败: {str(e)}")


@router.get("/{symbol}/indicators")
async def get_technical_indicators(
    symbol: str,
    indicators: str = Query(..., description="技术指标，多个用逗号分隔，如 MA,MACD,RSA"),
    period: str = Query("1day", description="K线周期"),
    days: int = Query(100, ge=1, le=500, description="计算天数"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取股票技术指标

    - **symbol**: 股票代码
    - **indicators**: 技术指标 (MA,EMA,MACD,RSA,BOLL,CCI,WR,RSI,ATR,OBV)
    - **period**: K线周期
    - **days**: 计算天数
    """
    try:
        indicator_list = [ind.strip().upper() for ind in indicators.split(",")]
        result = await stock_service.get_technical_indicators(
            symbol=symbol,
            indicators=indicator_list,
            period=period,
            days=days,
            db=db
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取技术指标失败: {str(e)}")


@router.get("/sectors")
async def get_stock_sectors(db: AsyncSession = Depends(get_db)):
    """获取股票行业板块列表"""
    try:
        result = await stock_service.get_stock_sectors(db=db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取行业板块失败: {str(e)}")


@router.get("/markets")
async def get_stock_markets():
    """获取支持的市场列表"""
    try:
        result = await stock_service.get_markets()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取市场列表失败: {str(e)}")


@router.get("/{symbol}/heatmap")
async def get_stock_heatmap(
    symbol: str,
    period: str = Query("1day", description="时间周期"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取股票热力图数据

    - **symbol**: 股票代码
    - **period**: 时间周期
    """
    try:
        result = await stock_service.get_heatmap_data(
            symbol=symbol,
            period=period,
            db=db
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取热力图数据失败: {str(e)}")