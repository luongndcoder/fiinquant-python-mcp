"""Environment-driven settings for the personal FiinQuant MCP server."""

from __future__ import annotations

import os
from dataclasses import dataclass

from fiinquant_mcp.limits import (
    FREE_MAX_HISTORY_DAYS,
    FREE_MAX_REALTIME_TICKERS,
    FREE_REQUESTS_PER_MINUTE,
    FREE_REQUESTS_PER_SECOND,
    PlanLimits,
)


@dataclass(frozen=True, slots=True)
class Settings:
    """Runtime configuration loaded from environment variables."""

    username: str | None
    password: str | None
    timeout_s: float = 30.0
    max_rows: int = 500
    max_chars: int = 80_000
    log_level: str = "INFO"
    plan: str = "free"
    enforce_plan_limits: bool = True
    max_history_days: int = FREE_MAX_HISTORY_DAYS
    max_realtime_tickers: int = FREE_MAX_REALTIME_TICKERS
    requests_per_minute: int = FREE_REQUESTS_PER_MINUTE
    requests_per_second: int = FREE_REQUESTS_PER_SECOND

    @property
    def has_credentials(self) -> bool:
        return bool(self.username and self.password)

    def plan_limits(self) -> PlanLimits:
        return PlanLimits(
            plan=self.plan,
            enforce=self.enforce_plan_limits,
            max_connections=1,
            requests_per_minute=self.requests_per_minute,
            requests_per_second=self.requests_per_second,
            max_realtime_tickers=self.max_realtime_tickers,
            max_history_days=self.max_history_days,
        )


def _env_bool(env: dict[str, str], key: str, default: bool) -> bool:
    raw = env.get(key)
    if raw is None or raw == "":
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def load_settings(environ: dict[str, str] | None = None) -> Settings:
    """Load settings from *environ* or ``os.environ``."""
    env = environ if environ is not None else os.environ
    plan = (env.get("FIINQUANT_PLAN") or "free").strip().lower()
    # Paid/pro: still allow overrides via explicit max_* env vars
    default_history = FREE_MAX_HISTORY_DAYS if plan in {"free", "trial", "demo"} else 3650
    default_rt = FREE_MAX_REALTIME_TICKERS if plan in {"free", "trial", "demo"} else 500
    default_rpm = FREE_REQUESTS_PER_MINUTE if plan in {"free", "trial", "demo"} else 600
    default_rps = FREE_REQUESTS_PER_SECOND if plan in {"free", "trial", "demo"} else 200

    return Settings(
        username=env.get("FIINQUANT_USERNAME") or None,
        password=env.get("FIINQUANT_PASSWORD") or None,
        timeout_s=float(env.get("FIINQUANT_TIMEOUT_S", "30")),
        max_rows=int(env.get("FIINQUANT_MAX_ROWS", "500")),
        max_chars=int(env.get("FIINQUANT_MAX_CHARS", "80000")),
        log_level=(env.get("FIINQUANT_LOG_LEVEL") or "INFO").upper(),
        plan=plan,
        enforce_plan_limits=_env_bool(env, "FIINQUANT_ENFORCE_PLAN_LIMITS", True),
        max_history_days=int(env.get("FIINQUANT_MAX_HISTORY_DAYS", str(default_history))),
        max_realtime_tickers=int(
            env.get("FIINQUANT_MAX_REALTIME_TICKERS", str(default_rt))
        ),
        requests_per_minute=int(
            env.get("FIINQUANT_REQUESTS_PER_MINUTE", str(default_rpm))
        ),
        requests_per_second=int(
            env.get("FIINQUANT_REQUESTS_PER_SECOND", str(default_rps))
        ),
    )
