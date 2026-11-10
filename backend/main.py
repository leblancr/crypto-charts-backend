from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.routers import watchlist, coins, auth
from contextlib import asynccontextmanager
from .database import engine
from .models import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # create tables once at startup (use Alembic later for prod)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # no teardown needed

app = FastAPI(lifespan=lifespan)

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # lock this down in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
# Grouped resources
app.include_router(watchlist.router, prefix="/watchlist", tags=["watchlist"])
app.include_router(coins.router, prefix="/coins", tags=["coins"])

# Auth endpoints under /auth/*
app.include_router(auth.router, prefix="/auth", tags=["auth"])

# ✅ Serve compiled Svelte from dist/
# app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")
