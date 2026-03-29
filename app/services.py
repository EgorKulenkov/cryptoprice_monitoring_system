import asyncio
import httpx
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .database import async_session
from .models import User_DB, Subscription_DB

class CryptoService:
    BASE_URL = "https://api.binance.com/api/v3/ticker/price"

    @classmethod
    async def get_price(cls,symbol: str) -> float:
        ticker = f"{symbol.upper()}USDT"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                        cls.BASE_URL,
                        params={"symbol":ticker},
                        timeout=5.0
                        )
                response.raise_for_status() #it returns error in case of 4xx or 5xx

                data = response.json()
                return float(data['price'])
            except httpx.RequestError as e:
                raise HTTPException(status_code=503, detail=f"API is unavailable,{e}")


async def price_watcher():
    print("nigga")
    while True: 
        async with async_session() as db: 
            query = select(User_DB).options(selectinload(User_DB.subscriptions))
            data = await db.execute(query)
            users = data.scalars().all()

            for user in users:
                for sub in user.subscriptions:
                    current_price = await CryptoService.get_price(sub.asset_name)

                    if current_price < sub.target_price:
                        print(f"{user.login}, {sub.asset_name} : {current_price}, awaitable price: {sub.target_price}", flush=True)

                    if current_price >= sub.target_price:
                        print(f"ALLERT {user.login}! {sub.asset_name} reach {sub.target_price}", flush=True)

        await asyncio.sleep(300)






