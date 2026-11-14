import asyncio
import time
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Query

router = APIRouter()

COINGECKO = "https://api.coingecko.com/api/v3"
_cache: dict = {}
_locks: dict = {}


async def cached_get(path: str, params: dict, ttl: int):
    """GET from CoinGecko with a TTL cache. If CoinGecko errors or
    rate-limits, serve the last good (stale) copy instead of failing."""
    key = (path, tuple(sorted(params.items())))
    lock = _locks.setdefault(key, asyncio.Lock())
    async with lock:
        now = time.time()
        hit = _cache.get(key)
        if hit and now - hit[0] < ttl:
            return hit[1]

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{COINGECKO}{path}", params=params)
        except httpx.HTTPError:
            resp = None

        if resp is not None and resp.status_code == 200:
            data = resp.json()
            _cache[key] = (now, data)
            return data

        if hit:  # upstream failed, serve stale data
            return hit[1]

        status = resp.status_code if resp is not None else 502
        detail = resp.text if resp is not None else "Price service unreachable"
        raise HTTPException(status_code=status, detail=detail)


@router.get("/current")
async def get_current_prices(symbols: str = Query(..., description="Comma-separated ids, e.g. bitcoin,ethereum")):
    """Return current USD prices for one or more coins"""
    coins = [s.strip().lower() for s in symbols.split(",") if s.strip()]
    params = {"ids": ",".join(coins), "vs_currencies": "usd"}
    return await cached_get("/simple/price", params, ttl=60)


@router.get("/{symbol}/history")
async def get_historical_prices(symbol: str, days: str = "30", interval: Optional[str] = None):
    """Return historical chart data for a coin"""
    params = {"vs_currency": "usd", "days": str(days)}
    if interval:
        params["interval"] = interval
    data = await cached_get(f"/coins/{symbol.lower()}/market_chart", params, ttl=300)
    return [{"timestamp": ts, "price": price} for ts, price in data.get("prices", [])]


@router.get("/top50")
async def get_top_50():
    """Return top 50 coins by market cap"""
    params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 50, "page": 1, "sparkline": "false"}
    data = await cached_get("/coins/markets", params, ttl=3600)
    return [{"id": c["id"], "symbol": c["symbol"], "name": c["name"]} for c in data]
