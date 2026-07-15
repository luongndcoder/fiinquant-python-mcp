"""Best-effort adapter around a local FiinQuant Python SDK install.

The public surface of private FiinQuant packages varies. This adapter tries
common module/class names and method aliases. Prefer injecting a custom
client_factory when the inventory script reveals a stable API.
"""

from __future__ import annotations

import importlib
import logging
from typing import Any

from fiinquant_mcp.config import Settings
from fiinquant_mcp.errors import ErrorCode, GatewayError

logger = logging.getLogger(__name__)

_MODULE_CANDIDATES = ("fiinquant", "FiinQuantX", "fiinquantx")
_CLASS_CANDIDATES = ("FiinSession", "Session", "FiinQuant", "Client")


class SdkClientAdapter:
    """Wrap an opaque SDK session object to the Gateway client protocol."""

    def __init__(self, settings: Settings, session: Any | None = None) -> None:
        self._settings = settings
        self._session = session

    def login(self) -> None:
        if self._session is None:
            self._session = self._create_session()
        # Try common login entrypoints
        for name in ("login", "Login", "authenticate", "connect"):
            fn = getattr(self._session, name, None)
            if callable(fn):
                try:
                    fn()
                    return
                except TypeError:
                    # Some SDKs want credentials on login()
                    fn(self._settings.username, self._settings.password)
                    return
        # Session constructor may already authenticate
        if self._session is not None:
            return
        raise GatewayError(
            ErrorCode.AUTH,
            "SDK session has no login() method",
            hint="Run scripts/inventory_fiinquant_sdk.py and wire a custom adapter",
        )

    def get_price_history(
        self,
        tickers: list[str],
        start: str,
        end: str,
        **kwargs: Any,
    ) -> Any:
        return self._call_aliases(
            (
                "get_price_history",
                "Fetch_Trading_Data",
                "fetch_trading_data",
                "get_historical_data",
                "ohlcv",
                "get_bars",
            ),
            tickers=tickers,
            start=start,
            end=end,
            **kwargs,
        )

    def list_tickers(self, market: str | None = None) -> Any:
        return self._call_aliases(
            (
                "list_tickers",
                "get_tickers",
                "Fetch_Ticker_List",
                "ticker_list",
                "get_universe",
            ),
            market=market,
        )

    def ticker_info(self, ticker: str) -> Any:
        return self._call_aliases(
            (
                "ticker_info",
                "get_ticker_info",
                "Fetch_Ticker_Info",
                "company_info",
            ),
            ticker=ticker,
        )

    def _create_session(self) -> Any:
        last_err: Exception | None = None
        for mod_name in _MODULE_CANDIDATES:
            try:
                mod = importlib.import_module(mod_name)
            except ImportError as exc:
                last_err = exc
                continue
            for cls_name in _CLASS_CANDIDATES:
                cls = getattr(mod, cls_name, None)
                if cls is None:
                    continue
                for kwargs in (
                    {
                        "username": self._settings.username,
                        "password": self._settings.password,
                    },
                    {
                        "user": self._settings.username,
                        "password": self._settings.password,
                    },
                    {},
                ):
                    try:
                        return cls(**kwargs)
                    except TypeError as exc:
                        last_err = exc
                        continue
            # module-level factory
            for factory_name in ("login", "create_session", "FiinSession"):
                factory = getattr(mod, factory_name, None)
                if not callable(factory):
                    continue
                try:
                    return factory(
                        self._settings.username,
                        self._settings.password,
                    )
                except TypeError as exc:
                    last_err = exc
                    continue
        raise GatewayError(
            ErrorCode.INTERNAL,
            f"Could not import/create FiinQuant SDK session: {last_err}",
            hint="Install private fiinquant wheel; run inventory script",
        )

    def _call_aliases(self, names: tuple[str, ...], **kwargs: Any) -> Any:
        if self._session is None:
            raise GatewayError(
                ErrorCode.AUTH,
                "Not logged in",
                hint="Gateway should call login first",
            )
        cleaned = {k: v for k, v in kwargs.items() if v is not None}
        last_err: Exception | None = None
        for name in names:
            fn = getattr(self._session, name, None)
            if not callable(fn):
                continue
            try:
                return fn(**cleaned)
            except TypeError as exc:
                last_err = exc
                # try positional for common (tickers, start, end)
                try:
                    if "tickers" in cleaned and "start" in cleaned and "end" in cleaned:
                        return fn(cleaned["tickers"], cleaned["start"], cleaned["end"])
                    if "ticker" in cleaned:
                        return fn(cleaned["ticker"])
                    if "market" in cleaned:
                        return fn(cleaned["market"])
                except Exception as exc2:  # noqa: BLE001
                    last_err = exc2
                    continue
            except Exception as exc:  # noqa: BLE001
                raise GatewayError(
                    ErrorCode.SDK_ERROR,
                    str(exc),
                    hint=f"SDK method {name} failed",
                ) from exc
        raise GatewayError(
            ErrorCode.INTERNAL,
            f"No matching SDK method among {names}; last_error={last_err}",
            hint="Run scripts/inventory_fiinquant_sdk.py and map methods explicitly",
        )


def default_client_factory(settings: Settings) -> SdkClientAdapter:
    return SdkClientAdapter(settings)
