"""FastMCP stdio server entry with P0 tools registered."""

from __future__ import annotations

import logging

from mcp.server.fastmcp import FastMCP

from fiinquant_mcp import __version__
from fiinquant_mcp.tools import health, market, universe

mcp = FastMCP("fiinquant_mcp")


@mcp.tool(
    name="fq_ping",
    annotations={
        "title": "FiinQuant MCP Ping",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def tool_fq_ping() -> str:
    """Health check for the personal FiinQuant MCP process (no credentials required)."""
    return await health.fq_ping()


@mcp.tool(
    name="fq_session_status",
    annotations={
        "title": "FiinQuant Session Status",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def tool_fq_session_status() -> str:
    """Show whether credentials are configured and if the Gateway session is logged in."""
    return await health.fq_session_status()


@mcp.tool(
    name="fq_get_price_history",
    annotations={
        "title": "Get Price History (OHLCV)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def tool_fq_get_price_history(tickers: str, start: str, end: str) -> str:
    """Fetch price/OHLCV history via FiinQuant SDK.

    Args:
        tickers: Comma-separated tickers (e.g. FPT,VNM)
        start: Start date YYYY-MM-DD
        end: End date YYYY-MM-DD
    """
    return await market.fq_get_price_history(tickers, start, end)


@mcp.tool(
    name="fq_list_tickers",
    annotations={
        "title": "List Tickers",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def tool_fq_list_tickers(market: str | None = None) -> str:
    """List available tickers, optionally filtered by market (HOSE/HNX/UPCOM)."""
    return await universe.fq_list_tickers(market=market)


@mcp.tool(
    name="fq_ticker_info",
    annotations={
        "title": "Ticker Info",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def tool_fq_ticker_info(ticker: str) -> str:
    """Return basic metadata for one ticker symbol."""
    return await universe.fq_ticker_info(ticker)


def main() -> None:
    """Run MCP over stdio."""
    logging.basicConfig(level=logging.INFO)
    logging.getLogger(__name__).info(
        "starting fiinquant_mcp v%s (stdio)",
        __version__,
    )
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
