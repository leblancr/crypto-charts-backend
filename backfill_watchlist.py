import asyncio
import httpx
from backend.database import SessionLocal
from backend.models import Watchlist

# Manual overrides for common tickers → correct CoinGecko IDs
# OVERRIDES = {
#     "btc": "bitcoin",
#     "eth": "ethereum",
#     "ada": "cardano",
# }

async def load_symbol_map():
    """Fetch symbol → id mapping from CoinGecko."""
    url = "https://api.coingecko.com/api/v3/coins/list"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return {c["symbol"].lower(): c["id"] for c in resp.json()}

def resolve_to_id(symbol: str, symbol_map: dict) -> str:
    """Resolve ticker symbol to a CoinGecko ID, with overrides for common coins."""
    sym = symbol.lower()
    if sym in OVERRIDES:
        return OVERRIDES[sym]
    return symbol_map.get(sym)

async def backfill():
    db = SessionLocal()
    symbol_map = await load_symbol_map()
    items = db.query(Watchlist).all()

    for item in items:
        sym = item.ticker.lower()
        cid = resolve_to_id(sym, symbol_map)
        item.coingecko_id = cid
        print(f"{sym} → {cid}")

    db.commit()
    db.close()

if __name__ == "__main__":
    asyncio.run(backfill())
