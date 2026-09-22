"""
AlphaLens FastAPI REST API Routes
Provides endpoints for market intelligence, probabilistic signals, stock deep dives,
causal explanations, portfolio risk, backtesting, prediction ledgers, natural language search,
universal real-time ticker lookup, and AI customer buy/avoid advisory recommendations.
"""

import json
from fastapi import APIRouter, Query, HTTPException
from typing import Dict, Any, Optional

from backend.pipeline.live_pipeline import live_pipeline
from backend.services.market_data_service import market_data_service
from backend.services.advisory_engine import advisory_engine
from backend.services.explanation_engine import explanation_engine
from backend.services.risk_engine import risk_engine
from backend.services.backtest_engine import backtest_engine
from backend.services.search_engine import search_engine

router = APIRouter()


@router.get("/market")
def get_market():
    """Returns today's live indices (NIFTY 50, SENSEX, BANK NIFTY, INDIA VIX), benchmark returns, and macroeconomic outlook."""
    overview = live_pipeline.get_market_overview()
    overview["session"] = market_data_service.get_market_session_status()
    return overview


@router.get("/market/session")
def get_market_session():
    """Returns real-time Indian Exchange (NSE/BSE) trading session status and hours."""
    return market_data_service.get_market_session_status()


@router.get("/stocks/{ticker}/depth")
def get_stock_market_depth(ticker: str):
    """Returns Level-2 Market Depth (5 Best Bids and 5 Best Asks) and live spread."""
    return market_data_service.fetch_market_depth(ticker)


@router.get("/stocks")
def get_stocks():
    """Returns all universe stocks with live model outlooks and customer advisory signals."""
    return live_pipeline.get_all_stocks()


@router.get("/search/tickers")
def search_tickers(q: str = Query(..., min_length=1)):
    """Universal symbol search & autocomplete across NSE, BSE, and Global tickers."""
    return market_data_service.search_tickers(q)


@router.get("/recommendations")
def get_recommendations():
    """Returns categorized AI customer recommendations: Top Buys, Stocks to Avoid, Breakouts, and Value Accumulate."""
    return live_pipeline.get_all_recommendations()


@router.get("/stocks/{ticker}")
def get_stock_detail(ticker: str):
    """Returns deep-dive multi-modal model analysis & customer advisory for any ticker (live fetched if new)."""
    stock = live_pipeline.get_stock(ticker)
    if not stock:
        raise HTTPException(status_code=404, detail=f"Ticker {ticker} not found in tracked universe.")
    
    news = live_pipeline.get_recent_news(ticker)
    return {
        "stock": stock,
        "recent_news": news
    }


@router.get("/stocks/{ticker}/advisory")
def get_stock_advisory(ticker: str):
    """Returns dedicated customer buy/avoid advisory breakdown, entry zones, targets, and stop losses."""
    return live_pipeline.get_advisory(ticker)


@router.get("/stocks/{ticker}/history")
def get_stock_history(ticker: str, days: int = Query(30, ge=1, le=5000)):
    """Returns real OHLCV price history and rolling indicators for interactive charting."""
    return live_pipeline.get_stock_price_history(ticker, days=days)


@router.get("/stocks/{ticker}/why-moving")
def get_why_moving(ticker: str):
    """Signature Feature: Dynamic causal explanation of primary drivers behind current move."""
    stock = live_pipeline.get_stock(ticker)
    if not stock:
        raise HTTPException(status_code=404, detail="Ticker not found.")
    
    # Reconstruct Series from cached stock record
    stock_series = pd_series_from_stock(stock)
    news = live_pipeline.get_recent_news(ticker)
    return explanation_engine.explain_why_moving(stock_series, news)


@router.get("/stocks/{ticker}/what-changed")
def get_what_changed(ticker: str):
    """Signature Feature: Comprehensive delta comparison from yesterday's close to today."""
    stock_today = live_pipeline.get_stock(ticker)
    if not stock_today:
        raise HTTPException(status_code=404, detail="Ticker not found.")
    
    today_series = pd_series_from_stock(stock_today)
    yesterday_series = live_pipeline.get_stock_yesterday(ticker)
    news = live_pipeline.get_recent_news(ticker)
    return explanation_engine.explain_what_changed(today_series, yesterday_series, news)


@router.get("/portfolio")
def get_portfolio():
    """Returns user portfolio metrics, sector allocation, and factor risk breakdown."""
    return risk_engine.analyze_portfolio(live_pipeline.latest_stocks_cache)


@router.get("/portfolio/scenario")
def simulate_portfolio_scenario(scenario: str = Query("nifty_drop_5pct")):
    """Simulates macro shock impact on user portfolio."""
    port_val = risk_engine.analyze_portfolio(live_pipeline.latest_stocks_cache).get("total_value", 284320.0)
    return risk_engine.simulate_scenario(scenario, port_val)


@router.get("/backtest")
def run_backtest(
    strategy: str = Query("finsight_signal"),
    capital: float = Query(100000.0, ge=10000.0, le=10000000.0),
    start_year: int = Query(2021, ge=2020, le=2025),
    end_year: int = Query(2026, ge=2021, le=2026)
):
    """Runs walk-forward backtest simulation with transaction costs and benchmark comparison."""
    return backtest_engine.run_backtest(
        strategy=strategy,
        initial_capital=capital,
        start_year=start_year,
        end_year=end_year
    )


@router.get("/predictions/ledger")
def get_prediction_ledger():
    """Returns 500+ verified historical predictions audit log with empirical calibration curves."""
    try:
        with open("data/processed/prediction_ledger.json", "r") as f:
            ledger = json.load(f)
        return ledger
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load prediction ledger: {e}")


@router.get("/model/stats")
def get_model_stats():
    """Returns overall ML ensemble metrics and walk-forward validation results."""
    try:
        with open("models/direction/metrics.json", "r") as f:
            dir_metrics = json.load(f)
        with open("models/return/metrics.json", "r") as f:
            ret_metrics = json.load(f)
        with open("models/ensemble/walk_forward_results.json", "r") as f:
            wf_results = json.load(f)
        return {
            "direction_model": dir_metrics,
            "return_model": ret_metrics,
            "walk_forward_validation": wf_results
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/search")
def search_intelligence(q: str = Query(...)):
    """Translates natural language financial queries into structured analyses and stock suggestions."""
    portfolio_data = risk_engine.analyze_portfolio(live_pipeline.latest_stocks_cache)
    return search_engine.process_query(q, live_pipeline.latest_stocks_cache, portfolio_data)


# -----------------------------------------------------------------------------
# 🤖 AI Financial Copilot Chatbot Endpoints
# -----------------------------------------------------------------------------

@router.post("/chat/message")
def chat_message(payload: Dict[str, Any]):
    """Receives user chat messages, executes context-aware quantitative analysis, and returns intelligent advice."""
    from backend.services.chatbot_service import chatbot_service
    message = payload.get("message", "").strip()
    session_id = payload.get("session_id", "default_user")
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    return chatbot_service.process_message(message, session_id=session_id)


@router.get("/chat/history")
def chat_history(session_id: str = Query("default_user")):
    """Retrieves session conversation history."""
    from backend.services.chatbot_service import chatbot_service
    return {"history": chatbot_service.get_session_history(session_id)}


@router.post("/chat/clear")
def chat_clear(payload: Dict[str, Any] = None):
    """Resets session conversation history."""
    from backend.services.chatbot_service import chatbot_service
    session_id = (payload or {}).get("session_id", "default_user")
    chatbot_service.clear_session_history(session_id)
    return {"success": True, "message": "Chat history reset."}


def pd_series_from_stock(stock_dict: Dict[str, Any]):
    import pandas as pd
    tech = stock_dict.get("technicals", {})
    fund = stock_dict.get("fundamentals", {})
    ev = stock_dict.get("evidence", {})
    flat = {
        "ticker": stock_dict.get("ticker"),
        "name": stock_dict.get("name"),
        "sector": stock_dict.get("sector"),
        "close": stock_dict.get("price", 1000.0),
        "return_1d": stock_dict.get("change_1d_pct", 0.0) / 100.0,
        "volume_ratio": tech.get("volume_ratio", 1.25),
        "rsi_14": tech.get("rsi_14", 50.0),
        "macd_hist": tech.get("macd_hist", 0.4),
        "news_sentiment": 0.35 if ev.get("news_sentiment") == "Positive" else -0.35,
        "nifty_return_1d": 0.0082,
        "india_vix": 13.8,
        "pe_ratio": float(fund.get("pe_ratio", 25.0)),
        "roe": float(str(fund.get("roe", "18%")).replace("%", "")),
        "market_regime": "BULL_TREND"
    }
    return pd.Series(flat)
