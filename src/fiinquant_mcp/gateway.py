"""FiinQuant Gateway — session owner, timeouts, error mapping."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable, Protocol

from fiinquant_mcp.config import Settings, load_settings
from fiinquant_mcp.errors import ErrorCode, GatewayError
from fiinquant_mcp.limits import RateLimiter, clamp_date_range_kwargs
from fiinquant_mcp.ops import SUPPORTED_OPS

logger = logging.getLogger(__name__)

_SESSION_EXPIRED_MARKERS = (
    "session expired",
    "unauthorized",
    "not logged in",
    "login required",
    "token expired",
    "authentication",
)


class FiinQuantClient(Protocol):
    """Client surface: named methods and/or generic run(op, **kwargs)."""

    def login(self) -> None: ...

    def run(self, op: str, **kwargs: Any) -> Any: ...


ClientFactory = Callable[[Settings], FiinQuantClient]


class FiinQuantGateway:
    """Owns SDK session lifecycle and applies reliability policy."""

    def __init__(
        self,
        settings: Settings | None = None,
        *,
        client_factory: ClientFactory | None = None,
    ) -> None:
        self.settings = settings if settings is not None else load_settings()
        self._client_factory = client_factory
        self._client: FiinQuantClient | None = None
        self._logged_in = False
        limits = self.settings.plan_limits()
        self._rate_limiter = RateLimiter(
            per_second=limits.requests_per_second,
            per_minute=limits.requests_per_minute,
            enabled=limits.enforce,
        )

    @property
    def is_logged_in(self) -> bool:
        return self._logged_in

    def _get_client(self) -> FiinQuantClient:
        if self._client is None:
            if self._client_factory is None:
                raise GatewayError(
                    ErrorCode.INTERNAL,
                    "No FiinQuant client factory configured",
                    hint="Install SDK and configure default factory, or inject client_factory for tests",
                )
            self._client = self._client_factory(self.settings)
        return self._client

    def ensure_session(self) -> None:
        """Lazy login. Raises GatewayError(AUTH) if credentials missing."""
        if not self.settings.has_credentials:
            raise GatewayError(
                ErrorCode.AUTH,
                "Missing FiinQuant credentials",
                hint="Set FIINQUANT_USERNAME and FIINQUANT_PASSWORD",
            )
        if self._logged_in:
            return
        client = self._get_client()
        try:
            client.login()
        except GatewayError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise GatewayError(
                ErrorCode.AUTH,
                f"Login failed: {exc}",
                hint="Check credentials and SDK install",
            ) from exc
        self._logged_in = True

    def _force_relogin(self) -> None:
        self._logged_in = False
        self.ensure_session()

    def _dispatch(self, op: str, **kwargs: Any) -> Any:
        if op not in SUPPORTED_OPS and not op.startswith("raw:"):
            raise GatewayError(
                ErrorCode.VALIDATION,
                f"Unknown operation: {op}",
                hint=f"Supported ops include: {', '.join(SUPPORTED_OPS[:12])}…",
            )
        client = self._get_client()
        # Prefer explicit method on client (tests / typed adapters)
        method = getattr(client, op, None)
        if callable(method) and op != "run":
            return method(**kwargs)
        # Generic run(op, **kwargs)
        run = getattr(client, "run", None)
        if callable(run):
            return run(op, **kwargs)
        raise GatewayError(
            ErrorCode.INTERNAL,
            f"Client cannot execute op '{op}'",
            hint="Client needs method '{op}' or run()",
        )

    def _is_session_expired(self, exc: BaseException) -> bool:
        msg = str(exc).lower()
        return any(m in msg for m in _SESSION_EXPIRED_MARKERS)

    def _sync_call(self, op: str, *, allow_reauth: bool, **kwargs: Any) -> Any:
        self.ensure_session()
        # Free-tier guards (history window, ticker batch, rate)
        self._rate_limiter.acquire()
        kwargs = clamp_date_range_kwargs(self.settings.plan_limits(), dict(kwargs))
        try:
            return self._dispatch(op, **kwargs)
        except GatewayError:
            raise
        except Exception as exc:  # noqa: BLE001
            if allow_reauth and self._is_session_expired(exc):
                logger.info("session expired heuristic matched; re-auth once")
                self._force_relogin()
                try:
                    return self._dispatch(op, **kwargs)
                except GatewayError:
                    raise
                except Exception as exc2:  # noqa: BLE001
                    raise GatewayError(
                        ErrorCode.SDK_ERROR,
                        str(exc2),
                        hint="SDK call failed after re-auth",
                    ) from exc2
            raise GatewayError(
                ErrorCode.SDK_ERROR,
                str(exc),
                hint="Inspect SDK error; reduce payload or retry",
            ) from exc

    async def call(self, op: str, **kwargs: Any) -> Any:
        """Run a named SDK operation with timeout + re-auth."""
        timeout = self.settings.timeout_s
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(self._sync_call, op, allow_reauth=True, **kwargs),
                timeout=timeout,
            )
        except TimeoutError as exc:
            raise GatewayError(
                ErrorCode.TIMEOUT,
                f"Operation '{op}' exceeded {timeout}s",
                hint="Increase FIINQUANT_TIMEOUT_S or narrow date range / tickers",
            ) from exc
        except GatewayError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise GatewayError(
                ErrorCode.INTERNAL,
                str(exc),
                hint="Unexpected gateway failure",
            ) from exc

    def session_status(self) -> dict[str, Any]:
        limits = self.settings.plan_limits()
        return {
            "logged_in": self._logged_in,
            "has_credentials": self.settings.has_credentials,
            "timeout_s": self.settings.timeout_s,
            "supported_ops": list(SUPPORTED_OPS),
            "plan": {
                "name": limits.plan,
                "enforce": limits.enforce,
                "max_connections": limits.max_connections,
                "max_history_days": limits.max_history_days,
                "max_realtime_tickers": limits.max_realtime_tickers,
                "requests_per_minute": limits.requests_per_minute,
                "requests_per_second": limits.requests_per_second,
                "rate": self._rate_limiter.snapshot(),
                "note": (
                    "Defaults match FiinQuant free (Trải nghiệm): "
                    "1 connection, 100k req/month, 90/min, 80/s, "
                    "realtime ≤33 tickers, history ≤1 month, TF 1m/5m/15m/1h/4h"
                ),
            },
        }
