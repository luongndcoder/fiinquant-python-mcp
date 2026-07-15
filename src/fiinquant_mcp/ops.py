"""Operation registry: logical MCP op → SDK method aliases (FiinQuantX-oriented)."""

from __future__ import annotations

# Each key is the Gateway op name / tool backend.
# Values are tried in order against the live SDK session object.
OP_ALIASES: dict[str, tuple[str, ...]] = {
    # Market / prices
    "get_price_history": (
        "get_price_history",
        "get_stock_prices",
        "Fetch_Trading_Data",
        "fetch_trading_data",
        "get_historical_data",
        "ohlcv",
        "get_bars",
    ),
    "get_stock_prices": (
        "get_stock_prices",
        "Fetch_Trading_Data",
        "fetch_trading_data",
        "get_price_history",
        "get_historical_data",
    ),
    "get_market_statistics": (
        "get_market_statistics",
        "Fetch_Market_Statistics",
        "market_statistics",
    ),
    "get_market_breadth": (
        "get_market_breadth",
        "Fetch_Market_Breadth",
        "market_breadth",
    ),
    "get_money_flow_contribution": (
        "get_money_flow_contribution",
        "money_flow_contribution",
        "Fetch_Money_Flow",
    ),
    "get_index_constituents": (
        "get_index_constituents",
        "index_constituents",
        "Fetch_Index_Constituents",
        "get_index_members",
    ),
    "get_realtime_bid_ask": (
        "get_realtime_bid_ask",
        "realtime_bid_ask",
        "Fetch_Bid_Ask",
    ),
    # Universe / meta
    "list_tickers": (
        "list_tickers",
        "get_tickers",
        "Fetch_Ticker_List",
        "ticker_list",
        "get_universe",
    ),
    "ticker_info": (
        "ticker_info",
        "get_ticker_info",
        "Fetch_Ticker_Info",
        "company_info",
        "get_basic_info",
    ),
    "get_basic_info": (
        "get_basic_info",
        "basic_info",
        "Fetch_Basic_Info",
        "ticker_info",
        "company_info",
    ),
    "get_icb_industries": (
        "get_icb_industries",
        "icb_industries",
        "Fetch_ICB_Industries",
    ),
    # Fundamental
    "get_financial_ratios": (
        "get_financial_ratios",
        "financial_ratios",
        "Fetch_Financial_Ratio",
        "Fetch_Financial_Ratios",
    ),
    "get_financial_statements": (
        "get_financial_statements",
        "financial_statements",
        "Fetch_Financial_Statement",
        "Fetch_BCTC",
    ),
    "get_valuation_timeseries": (
        "get_valuation_timeseries",
        "valuation_timeseries",
        "Fetch_Valuation",
    ),
    "get_equity_snapshot": (
        "get_equity_snapshot",
        "equity_snapshot",
        "StockScreening",
        "stock_screening",
    ),
    # Screening / analysis
    "screen_stocks": (
        "screen_stocks",
        "StockScreening",
        "stock_screening",
        "screen",
        "screener",
    ),
    "get_technical_indicators": (
        "get_technical_indicators",
        "technical_indicators",
        "FiinIndicator",
        "fiin_indicator",
        "indicators",
    ),
    "detect_pattern": (
        "detect_pattern",
        "pattern",
        "Pattern",
        "calculate_pattern",
    ),
    "get_rrg_analysis": (
        "get_rrg_analysis",
        "rrg_analysis",
        "RRG",
        "rrg",
    ),
    "get_rebalance": (
        "get_rebalance",
        "rebalance",
        "calculate_rebalance",
    ),
    "run_custom_analysis": (
        "run_custom_analysis",
        "custom_analysis",
        "CustomAnalysis",
    ),
    # Escape hatches
    "search_methods": (
        "search_methods",
        "fiinquantx_search_methods",
        "list_methods",
        "discover_methods",
    ),
    "call_method": (
        "call_method",
        "fiinquantx_call_method",
        "invoke",
        "call",
    ),
}

SUPPORTED_OPS: tuple[str, ...] = tuple(sorted(OP_ALIASES.keys()))
