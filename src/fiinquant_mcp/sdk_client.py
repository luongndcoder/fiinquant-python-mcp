"""Adapter for installed FiinQuantX (FiinSession) package."""

from __future__ import annotations

import logging
from typing import Any

from fiinquant_mcp.config import Settings
from fiinquant_mcp.errors import ErrorCode, GatewayError

logger = logging.getLogger(__name__)

_DEFAULT_OHLCV_FIELDS = ["open", "high", "low", "close", "volume"]


def _as_list(value: Any) -> list[Any] | None:
    if value is None:
        return None
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, str):
        return [p.strip() for p in value.replace(";", ",").split(",") if p.strip()]
    return [value]


def _df_or_obj(obj: Any) -> Any:
    """Prefer DataFrame if object exposes to_dataFrame/get."""
    if obj is None:
        return None
    if hasattr(obj, "to_dataFrame") and callable(obj.to_dataFrame):
        try:
            return obj.to_dataFrame()
        except Exception:  # noqa: BLE001
            pass
    if hasattr(obj, "get_data") and callable(obj.get_data):
        return obj.get_data()
    if hasattr(obj, "get") and callable(obj.get) and not isinstance(obj, dict):
        try:
            return obj.get()
        except TypeError:
            pass
    return obj


def _freq_map(frequency: str | None) -> str:
    if not frequency:
        return "1d"
    f = frequency.strip()
    mapping = {
        "Daily": "1d",
        "daily": "1d",
        "1d": "1d",
        "1D": "1d",
        "1m": "1m",
        "5m": "5m",
        "15m": "15m",
        "30m": "30m",
        "1h": "1h",
        "4h": "4h",
        "Weekly": "1w",
        "Monthly": "1M",
    }
    return mapping.get(f, f)


class SdkClientAdapter:
    """FiinQuantX-backed client implementing Gateway ops via ``run``."""

    def __init__(self, settings: Settings, session: Any | None = None) -> None:
        self._settings = settings
        self._session = session

    def login(self) -> None:
        if self._session is None:
            self._session = self._create_session()
        try:
            self._session.login()
        except Exception as exc:  # noqa: BLE001
            raise GatewayError(
                ErrorCode.AUTH,
                f"FiinQuantX login failed: {exc}",
                hint="Check FIINQUANT_USERNAME / FIINQUANT_PASSWORD",
            ) from exc

    def run(self, op: str, **kwargs: Any) -> Any:
        if self._session is None:
            raise GatewayError(ErrorCode.AUTH, "Not logged in")
        handlers = {
            "get_price_history": self._get_stock_prices,
            "get_stock_prices": self._get_stock_prices,
            "list_tickers": self._list_tickers,
            "ticker_info": self._ticker_info,
            "get_basic_info": self._get_basic_info,
            "get_icb_industries": self._get_icb_industries,
            "get_financial_ratios": self._get_financial_ratios,
            "get_financial_statements": self._get_financial_statements,
            "get_valuation_timeseries": self._get_valuation_timeseries,
            "get_equity_snapshot": self._get_equity_snapshot,
            "get_market_statistics": self._get_market_statistics,
            "get_market_breadth": self._get_market_breadth,
            "get_money_flow_contribution": self._get_money_flow,
            "get_index_constituents": self._get_index_constituents,
            "get_realtime_bid_ask": self._get_realtime_bid_ask,
            "screen_stocks": self._screen_stocks,
            "get_technical_indicators": self._get_technical_indicators,
            "detect_pattern": self._detect_pattern,
            "get_rrg_analysis": self._get_rrg,
            "get_rebalance": self._get_rebalance,
            "run_custom_analysis": self._run_custom_analysis,
            "search_methods": self._search_methods,
            "call_method": self._call_method,
        }
        fn = handlers.get(op)
        if fn is None:
            raise GatewayError(
                ErrorCode.VALIDATION,
                f"Unsupported op for FiinQuantX adapter: {op}",
            )
        try:
            return fn(**kwargs)
        except GatewayError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise GatewayError(
                ErrorCode.SDK_ERROR,
                str(exc),
                hint=f"FiinQuantX op '{op}' failed",
            ) from exc

    # Explicit methods for getattr(client, op) dispatch
    def get_price_history(self, **kwargs: Any) -> Any:
        return self.run("get_price_history", **kwargs)

    def list_tickers(self, **kwargs: Any) -> Any:
        return self.run("list_tickers", **kwargs)

    def ticker_info(self, **kwargs: Any) -> Any:
        return self.run("ticker_info", **kwargs)

    def _create_session(self) -> Any:
        try:
            from FiinQuantX import FiinSession
        except ImportError as exc:
            raise GatewayError(
                ErrorCode.INTERNAL,
                f"FiinQuantX not installed: {exc}",
                hint="pip install FiinQuantX into the same Python as the MCP server",
            ) from exc
        return FiinSession(
            username=self._settings.username or "",
            password=self._settings.password or "",
        )

    def _get_stock_prices(
        self,
        tickers: Any = None,
        start: str | None = None,
        end: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        frequency: str | None = "Daily",
        by: str | None = None,
        latest: bool = False,
        adjusted: bool = True,
        period: int | str | None = None,
        fields: list[str] | None = None,
        **_: Any,
    ) -> Any:
        tickers_l = _as_list(tickers) or []
        field_list = fields or list(_DEFAULT_OHLCV_FIELDS)
        by_val = by or _freq_map(frequency)
        period_i: int | None
        if period is None:
            period_i = None
        else:
            period_i = int(period)
        ftd = self._session.Fetch_Trading_Data(
            realtime=False,
            tickers=tickers_l if len(tickers_l) != 1 else tickers_l[0],
            fields=field_list,
            adjusted=adjusted,
            period=period_i,
            by=by_val,
            from_date=from_date or start,
            to_date=to_date or end,
            lasted=True if latest else None,
        )
        return _df_or_obj(ftd)

    def _list_tickers(self, market: str | None = None, **_: Any) -> Any:
        # TickerList API is thin; use StockScreening empty filter if needed
        try:
            tl = self._session.TickerList()
            return _df_or_obj(tl)
        except Exception:
            # fallback: BasicInfor needs tickers — return market hint
            return {
                "note": "TickerList empty; use get_basic_info with tickers or screen_stocks",
                "market": market,
            }

    def _ticker_info(self, ticker: str, **_: Any) -> Any:
        return self._get_basic_info(tickers=[ticker])

    def _get_basic_info(self, tickers: Any = None, **_: Any) -> Any:
        tickers_l = _as_list(tickers) or []
        info = self._session.BasicInfor(tickers_l if len(tickers_l) != 1 else tickers_l[0])
        return _df_or_obj(info)

    def _get_icb_industries(self, level: int = 2, **_: Any) -> Any:
        # Not always exposed as top-level; try StockScreening indicator configs
        try:
            ss = self._session.StockScreening()
            if hasattr(ss, "get_indicator_configs"):
                return ss.get_indicator_configs("sector")
        except Exception as exc:  # noqa: BLE001
            logger.debug("icb via screening failed: %s", exc)
        return {
            "level": level,
            "hint": "Use screen_stocks with sector filters; dedicated ICB list not on this SDK build",
        }

    def _get_financial_ratios(
        self,
        tickers: Any = None,
        years: list[int] | None = None,
        quarters: list | None = None,
        type: str = "consolidated",  # noqa: A002
        fields: list | None = None,
        **_: Any,
    ) -> Any:
        fa = self._session.FundamentalAnalysis()
        years_l = years or [2024, 2025]
        return fa.get_ratios(
            tickers=_as_list(tickers) or [],
            years=years_l,
            quarters=quarters,
            type=type if type in ("consolidated", "separate") else "consolidated",
            fields=fields,
        )

    def _get_financial_statements(
        self,
        tickers: Any = None,
        statement: str = "income_statement",
        years: list[int] | None = None,
        quarters: list | None = None,
        audited: bool | None = None,
        type: str = "consolidated",  # noqa: A002
        fields: list | str | None = None,
        **_: Any,
    ) -> Any:
        fa = self._session.FundamentalAnalysis()
        stmt_map = {
            "income_statement": "incomestatement",
            "incomestatement": "incomestatement",
            "balance_sheet": "balancesheet",
            "balancesheet": "balancesheet",
            "cashflow": "cashflow",
            "full": "full",
            "note": "full",
        }
        st = stmt_map.get((statement or "").lower(), "incomestatement")
        years_arg: Any = years if years is not None else 2024
        return fa.get_financial_statement(
            statement=st,
            tickers=_as_list(tickers) or [],
            years=years_arg,
            type=type if type in ("consolidated", "separate") else "consolidated",
            audited=audited,
            quarters=quarters,
            fields=fields,
        )

    def _get_valuation_timeseries(
        self,
        scope: str = "stock",
        tickers: Any = None,
        index: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        sector_level: int | None = None,
        **_: Any,
    ) -> Any:
        md = self._session.MarketDepth()
        tickers_l = _as_list(tickers) or ([index] if index else [])
        if not from_date:
            raise GatewayError(
                ErrorCode.VALIDATION,
                "from_date is required for valuation timeseries",
            )
        if scope == "index":
            return md.get_index_valuation(tickers_l, from_date, to_date or from_date)
        if scope == "sector":
            return md.get_sector_valuation(
                tickers_l, sector_level or 2, from_date, to_date or from_date
            )
        return md.get_stock_valuation(tickers_l, from_date, to_date or from_date)

    def _get_equity_snapshot(
        self,
        tickers: Any = None,
        metrics: list[str] | None = None,
        as_of_date: str | None = None,
        limit: int | None = None,
        **_: Any,
    ) -> Any:
        # Approximate via screening with empty/min filter + ticker constraint if supported
        tickers_l = _as_list(tickers) or []
        # latest prices as snapshot baseline
        df = self._get_stock_prices(tickers=tickers_l, latest=True, frequency="Daily")
        return {
            "snapshot": _df_or_obj(df),
            "metrics_requested": metrics,
            "as_of_date": as_of_date,
            "limit": limit,
            "note": "Snapshot approximated via latest prices; use screen_stocks for multi-metric filters",
        }

    def _get_market_statistics(
        self,
        tickers: Any = None,
        metric: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        time_filter: str = "Daily",
        **_: Any,
    ) -> Any:
        ps = self._session.PriceStatistics()
        tickers_l = _as_list(tickers) or []
        if not from_date:
            raise GatewayError(ErrorCode.VALIDATION, "from_date is required")
        to = to_date or from_date
        metric_l = (metric or "overview").lower()
        if metric_l in ("foreign", "khoingoai"):
            return ps.get_foreign(tickers_l, time_filter, from_date, to)
        if metric_l in ("freefloat", "free_float"):
            return ps.get_freefloat(tickers_l, from_date, to)
        if metric_l in ("ceilingfloor", "ceiling_floor"):
            return ps.get_ceilingfloor(tickers_l, from_date, to)
        if metric_l in ("investor", "value_by_investor"):
            return ps.get_value_by_investor(tickers_l, from_date, to)
        return ps.get_overview(tickers_l, time_filter, from_date, to)

    def _get_market_breadth(
        self,
        index: str = "VNINDEX",
        from_date: str | None = None,
        to_date: str | None = None,
        **_: Any,
    ) -> Any:
        mb = self._session.MarketBreadth()
        # API takes tickers optionally
        return mb.get(tickers=index)

    def _get_money_flow(
        self,
        index: str | None = None,
        direction: str | None = None,
        contribution_day: str | None = None,
        limit: int | None = None,
        **_: Any,
    ) -> Any:
        mf = self._session.MoneyFlow()
        ticker = index or "VNINDEX"
        day = contribution_day or "1Day"
        if day not in ("1Day", "5Day", "10Day", "20Day"):
            day = "1Day"
        typ = direction or "topGainers"
        if typ not in ("topGainers", "topLosers"):
            typ = "topGainers"
        return mf.get_contribution(
            ticker=ticker,
            contribution_day=day,
            type=typ,
            top=limit or 15,
        )

    def _get_index_constituents(self, index: str = "VN30", **_: Any) -> Any:
        # Often available via screening or ticker list; try StockScreening
        ss = self._session.StockScreening()
        # Best-effort: filter by index membership if indicator exists
        try:
            return ss.get(
                filter=[{"indicator": "index", "operator": "eq", "value": index}],
                exchanges=[],
            )
        except Exception:
            return {
                "index": index,
                "hint": "Constituents filter may need custom screen; try screen_stocks",
            }

    def _get_realtime_bid_ask(
        self,
        tickers: Any = None,
        max_realtime_events: int = 1,
        **_: Any,
    ) -> Any:
        # BidAsk is callback/streaming — return guidance + try one-shot if possible
        return {
            "tickers": _as_list(tickers),
            "max_realtime_events": max_realtime_events,
            "note": (
                "FiinQuantX BidAsk is streaming/callback-based; "
                "use get_stock_prices(latest=true) for last trade on free tier"
            ),
        }

    def _screen_stocks(
        self,
        filters: list | dict | None = None,
        exchanges: list | None = None,
        sectors: list | None = None,
        screener_date: str | None = None,
        **_: Any,
    ) -> Any:
        ss = self._session.StockScreening()
        filt = filters if isinstance(filters, list) else ([] if filters is None else [filters])
        kwargs: dict[str, Any] = {
            "filter": filt,
            "exchanges": exchanges or [],
            "sectors": sectors or [],
        }
        if screener_date:
            kwargs["screenerDate"] = screener_date
        return ss.get(**kwargs)

    def _get_technical_indicators(
        self,
        tickers: Any = None,
        indicators: Any = None,
        by: str = "1d",
        lasted: bool = True,
        adjusted: bool = True,
        period: int | str | None = None,
        **_: Any,
    ) -> Any:
        # Fetch OHLCV then apply FiinIndicator if available
        tickers_l = _as_list(tickers) or []
        df = self._get_stock_prices(
            tickers=tickers_l,
            by=by,
            adjusted=adjusted,
            period=period or 100,
            latest=False,
        )
        try:
            ind = self._session.FiinIndicator()
            # FiinIndicator API varies; return price df + requested indicators
            return {
                "prices": df if not hasattr(df, "to_dict") else df,
                "indicators_requested": indicators,
                "engine": type(ind).__name__,
                "note": "Prices fetched; apply indicator methods via fiinquantx_call_method if needed",
            }
        except Exception:
            return {"prices": df, "indicators_requested": indicators}

    def _detect_pattern(self, pattern: str, params: dict | None = None, **_: Any) -> Any:
        params = params or {}
        tickers = params.get("tickers") or params.get("ticker")
        if not tickers:
            raise GatewayError(
                ErrorCode.VALIDATION,
                "params.tickers required for detect_pattern",
                hint='params={"tickers":["FPT"],"from_date":"2026-06-01"}',
            )
        df = self._get_stock_prices(
            tickers=tickers,
            from_date=params.get("from_date"),
            to_date=params.get("to_date"),
            by=params.get("by", "1d"),
            period=params.get("period", 100),
        )
        pat = self._session.Pattern()
        name = pattern.strip().lower().replace("-", "_")
        method_map = {
            "doji": "detect_doji",
            "engulfing": "detect_engulfing",
            "hammer": "detect_hammer_shooting",
            "harami": "detect_harami",
            "star": "detect_star_patterns",
            "support_resistance": "calculate_support_resistance",
            "trendline": "detect_trendline",
            "triangle": "detect_triangle_pattern",
            "wedge": "detect_wedge",
            "channel": "detect_channel",
        }
        method_name = method_map.get(name, name if name.startswith("detect_") else f"detect_{name}")
        method = getattr(pat, method_name, None)
        if not callable(method):
            raise GatewayError(
                ErrorCode.VALIDATION,
                f"Unknown pattern '{pattern}'",
                hint=f"Try: {', '.join(method_map)}",
            )
        # inject df as first arg
        return method(df, **{k: v for k, v in params.items() if k not in ("tickers", "ticker", "from_date", "to_date", "by", "period")})

    def _get_rrg(
        self,
        tickers: Any = None,
        benchmark: str = "VNINDEX",
        params: dict | None = None,
        **kwargs: Any,
    ) -> Any:
        params = params or {}
        rrg = self._session.RRG(
            tickers=_as_list(tickers) or [],
            benchmark=benchmark,
            by=params.get("by", kwargs.get("by", "1d")),
            from_date=params.get("from_date", kwargs.get("from_date")),
            to_date=params.get("to_date", kwargs.get("to_date")),
            period=params.get("period", kwargs.get("period")),
        )
        return rrg.get()

    def _get_rebalance(self, index: str = "VN30", budget: float = 1_000_000_000, **_: Any) -> Any:
        reb = self._session.Rebalance()
        return reb.get(Budget=int(budget), Ticker=index)

    def _run_custom_analysis(
        self,
        analysis_id: str | None = None,
        params: dict | None = None,
        **_: Any,
    ) -> Any:
        return {
            "analysis_id": analysis_id,
            "params": params,
            "available": [
                "use StockScreening, MoneyFlow, RRG, Pattern via domain tools",
            ],
            "note": "Custom analysis registry is MCP-server-side on official; here map to domain tools",
        }

    def _search_methods(self, query: str = "", limit: int = 10, **_: Any) -> Any:
        names = [a for a in dir(self._session) if not a.startswith("_") and query.lower() in a.lower()]
        return {"query": query, "methods": names[:limit], "session_type": type(self._session).__name__}

    def _call_method(
        self,
        method_id: str,
        params: dict | None = None,
        dry_run: bool = False,
        **_: Any,
    ) -> Any:
        params = params or {}
        if dry_run:
            return {"dry_run": True, "method_id": method_id, "params": params}
        # Support dotted paths like FundamentalAnalysis.get_ratios
        parts = method_id.split(".")
        obj: Any = self._session
        for p in parts:
            obj = getattr(obj, p)
            if callable(obj) and p != parts[-1]:
                obj = obj()
        if callable(obj):
            return obj(**params)
        return obj


def default_client_factory(settings: Settings) -> SdkClientAdapter:
    return SdkClientAdapter(settings)
