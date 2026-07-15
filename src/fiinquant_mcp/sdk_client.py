"""Best-effort adapter around a local FiinQuant / FiinQuantX Python SDK."""

from __future__ import annotations

import importlib
import logging
from typing import Any

from fiinquant_mcp.config import Settings
from fiinquant_mcp.errors import ErrorCode, GatewayError
from fiinquant_mcp.ops import OP_ALIASES

logger = logging.getLogger(__name__)

_MODULE_CANDIDATES = ("FiinQuantX", "fiinquantx", "fiinquant")
_CLASS_CANDIDATES = ("FiinSession", "Session", "FiinQuant", "Client", "FiinQuantX")


class SdkClientAdapter:
    """Wrap an opaque SDK session object for the Gateway."""

    def __init__(self, settings: Settings, session: Any | None = None) -> None:
        self._settings = settings
        self._session = session

    def login(self) -> None:
        if self._session is None:
            self._session = self._create_session()
        for name in ("login", "Login", "authenticate", "connect"):
            fn = getattr(self._session, name, None)
            if callable(fn):
                try:
                    fn()
                    return
                except TypeError:
                    fn(self._settings.username, self._settings.password)
                    return
        if self._session is not None:
            return
        raise GatewayError(
            ErrorCode.AUTH,
            "SDK session has no login() method",
            hint="Run scripts/inventory_fiinquant_sdk.py and wire a custom adapter",
        )

    def run(self, op: str, **kwargs: Any) -> Any:
        """Execute a logical op using method alias table."""
        if op.startswith("raw:"):
            method_name = op.split(":", 1)[1]
            return self._call_aliases((method_name,), **kwargs)
        aliases = OP_ALIASES.get(op)
        if not aliases:
            aliases = (op,)
        return self._call_aliases(aliases, **kwargs)

    # Explicit methods so getattr(client, op) works for tests / typed use
    def get_price_history(self, **kwargs: Any) -> Any:
        return self.run("get_price_history", **kwargs)

    def list_tickers(self, **kwargs: Any) -> Any:
        return self.run("list_tickers", **kwargs)

    def ticker_info(self, **kwargs: Any) -> Any:
        return self.run("ticker_info", **kwargs)

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
            hint="Install private FiinQuantX/fiinquant wheel; run inventory script",
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
                try:
                    return self._positional_fallback(fn, cleaned)
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
            hint="Run scripts/inventory_fiinquant_sdk.py and map methods in ops.py",
        )

    def _positional_fallback(self, fn: Any, cleaned: dict[str, Any]) -> Any:
        if "tickers" in cleaned and "start" in cleaned and "end" in cleaned:
            return fn(cleaned["tickers"], cleaned["start"], cleaned["end"])
        if "tickers" in cleaned and "from_date" in cleaned and "to_date" in cleaned:
            return fn(cleaned["tickers"], cleaned["from_date"], cleaned["to_date"])
        if "ticker" in cleaned:
            return fn(cleaned["ticker"])
        if "tickers" in cleaned:
            return fn(cleaned["tickers"])
        if "market" in cleaned:
            return fn(cleaned["market"])
        if "index" in cleaned:
            return fn(cleaned["index"])
        if "method_id" in cleaned:
            return fn(cleaned["method_id"], cleaned.get("params") or {})
        raise TypeError("no positional fallback matched")


def default_client_factory(settings: Settings) -> SdkClientAdapter:
    return SdkClientAdapter(settings)
