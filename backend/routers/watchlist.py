from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.database import get_db
from backend.models import Watchlist, User
from fastapi.security import OAuth2PasswordBearer
import jwt
from backend.config import JWT_SECRET

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_username(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload.get("sub")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

async def get_current_user(
    username: str = Depends(get_current_username),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).filter_by(username=username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# add coin to watchlist
@router.post("/{coingecko_id}")
async def add_coin_to_watchlist(
    coingecko_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    print(f" POST /watchlist/{coingecko_id} by user {current_user.id}")
    coingecko_id = coingecko_id.lower()
    result = await db.execute(
        select(Watchlist).filter_by(user_id=current_user.id, coingecko_id=coingecko_id)
    )
    existing = result.scalars().first()

    if existing:
        return {"detail": f"{coingecko_id.upper()} already in watchlist"}

    item = Watchlist(user_id=current_user.id, coingecko_id=coingecko_id)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return {"detail": f"{coingecko_id.upper()} added"}


# get current user’s watchlist
@router.get("/")
async def get_watchlist(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Watchlist).filter_by(user_id=current_user.id))
    items = result.scalars().all()
    return [
        {"id": item.id, "coingecko_id": item.coingecko_id}
        for item in items
    ]


# remove coin
@router.delete("/{coingecko_id}")
async def remove_coin_from_watchlist(
    coingecko_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    coingecko_id = coingecko_id.lower()
    result = await db.execute(
        select(Watchlist).filter_by(user_id=current_user.id, coingecko_id=coingecko_id)
    )
    item = result.scalars().first()

    if not item:
        raise HTTPException(status_code=404, detail=f"{coingecko_id.upper()} not in watchlist")

    await db.delete(item)
    await db.commit()
    return {"detail": f"{coingecko_id.upper()} removed"}
