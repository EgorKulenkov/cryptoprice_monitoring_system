from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status

from typing import List

from pydantic import BaseModel, Field, EmailStr, field_validator

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from sqlalchemy.orm import selectinload

from .database import async_session, engine, init_models
from .models import User_DB, Subscription_DB
from .pydantic_models import User, Subscription, ALLOWED_ASSETS
from .services import CryptoService, price_watcher

import httpx
import asyncio

#Pydantic models - validation for entrane data
#SQLAlchemy models - work with database

@asynccontextmanager
async def lifespan(app: FastAPI):
    #before FastAPI will get requests
    await init_models()
    task = asyncio.create_task(price_watcher())
    print("background task initialized")
    yield 
    task.cancel()

app = FastAPI(lifespan=lifespan)

async def get_db():
    async with async_session() as session:
        yield session


@app.get("/")
def read_root():
    return {"message":"success"}

@app.post("/create_user")
async def create_user(user: User, db: AsyncSession = Depends(get_db)):
    query = select(User_DB).where(User_DB.login == user.login)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail=f"User: {user.login} is already exists")

    try:
        db_subscriptions = [
                Subscription_DB(asset_name=sub.asset_name, target_price=sub.target_price)
                for sub in user.subscriptions
                ]

        new_user = User_DB(login=user.login,
                           subscriptions=db_subscriptions
                           )
        db.add(new_user)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"DB ERROR: {e}")

    return {"status":"OK", "message":f"User: {user.login} was successfully created!"}


@app.delete("/delete_user")
async def delete_user(id_user: int, db: AsyncSession = Depends(get_db)):
    try:
        query = select(User_DB).where(User_DB.id == id_user)
        result = await db.execute(query)
        existing_user = result.scalar_one_or_none()
    except Exception as e:
        return {"status":"it's not okay", "message":str(e)}

    if not existing_user:
        raise HTTPException(status_code=401, detail=f"Item with {user.id} is not found!")

    try:
        await db.delete(existing_user)
        await db.commit()
    except Exception as e:
        return {"status":"it's not okay", "message":str(e)}

    
    return {"status":"ok", "message":f"User {user.login} was successfully deleted!"}


@app.get("/get_all_users")
async def get_all_users(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(User_DB).options(selectinload(User_DB.subscriptions)))
        users = result.scalars().all()
    except Exception as e:
        raise
    else:
        return users

@app.get("/get_all_subs")
async def get_all_subs(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Subscription_DB))
        subs = result.scalars().all()
    except Exception as e:
        raise
    else:
        return subs

@app.get("/test-db")
async def test_db(db: AsyncSession = Depends(get_db)):
	try:
		res = await db.execute(text("SELECT 1"))
		return {"status":"ok", "details": res.scalar()}
	except Exception as e:
		return {"status": "it is not okay bro", "message": str(e)}



@app.get("/crypto_price/{symbol}")
async def get_crypto_price(symbol: str):
    price = await CryptoService.get_price(symbol)
    return {"info":f"{symbol.upper()}: {price}"}





