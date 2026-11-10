from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from backend.models import User

_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def add_to_watchlist(db: AsyncSession, user_id: int, coingecko_id: str):
    coingecko_id = coingecko_id.lower()
    existing = db.query(Watchlist).filter(
        Watchlist.user_id == user_id,
        Watchlist.coingecko_id == coingecko_id
    ).first()

    if existing:
        return {"detail": f"{coingecko_id.upper()} already in watchlist"}

    item = Watchlist(user_id=user_id, coingecko_id=coingecko_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"detail": f"{coingecko_id.upper()} added"}

# Users
def create_user(db: AsyncSession, username: str, password: str):
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        return None  # let the router raise HTTPException
    hashed = pwd_context.hash(password)
    user = User(username=username, password_hash=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: AsyncSession, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if user and pwd_context.verify(password, user.password_hash):
        return user
    return None

# Watchlist
def get_watchlist(db: AsyncSession, user_id: int):
    return db.query(Watchlist).filter(Watchlist.user_id == user_id).all()

def hash_password(password: str) -> str:
    return _pwd_ctx.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_ctx.verify(plain, hashed)

async def create_user(username: str, password: str, db: AsyncSession) -> bool:
    result = await db.execute(select(User).filter_by(username=username))
    existing = result.scalars().first()
    if existing:
        return False

    user = User(username=username, password_hash=hash_password(password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return True

async def authenticate_user(
    username: str,
    password: str | None,
    db: AsyncSession,
    *,
    check_password: bool = True,
):
    result = await db.execute(select(User).filter_by(username=username))
    user = result.scalars().first()
    if not user:
        return None
    if check_password:
        if password is None or not verify_password(password, user.password_hash):
            return None
    return user

def remove_from_watchlist(db: AsyncSession, user_id: int, coingecko_id: str):
    coingecko_id = coingecko_id.lower()
    item = db.query(Watchlist).filter(
        Watchlist.user_id == user_id,
        Watchlist.coingecko_id == coingecko_id
    ).first()

    if not item:
        return {"detail": f"{coingecko_id.upper()} not in watchlist"}

    db.delete(item)
    db.commit()
    return {"detail": f"{coingecko_id.upper()} removed"}
