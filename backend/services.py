import httpx
import asyncio

COINS = ["bitcoin", "ethereum", "cardano"]

async def fetch_coin_price(client: httpx.AsyncClient, coin: str):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
    resp = await client.get(url)
    resp.raise_for_status()
    return {coin: resp.json()[coin]["usd"]}

async def get_crypto_prices():
    async with httpx.AsyncClient(timeout=10) as client:
        tasks = [fetch_coin_price(client, coin) for coin in COINS]
        results = await asyncio.gather(*tasks)
        return {k: v for d in results for k, v in d.items()}
