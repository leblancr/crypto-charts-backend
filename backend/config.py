# FILE: backend/config.py
import socket
import os
from dotenv import load_dotenv
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_FILE)

DATABASE_URL = os.getenv("DATABASE_URL", "")
if not DATABASE_URL:
    raise SystemExit("❌ DATABASE_URL missing after loading .env")

# ✅ Add this:
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-key")

# print(f"🔍 Using DATABASE_URL: {DATABASE_URL}")
print(f"🔑 Loaded JWT_SECRET: {JWT_SECRET[:4]}****")  # optional partial print for safety

try:
    from sqlalchemy.engine.url import make_url
    url = make_url(DATABASE_URL)
    host, port = url.host or "127.0.0.1", url.port or 5432
    with socket.create_connection((host, port), timeout=2):
        print(f"✅ Database reachable at {host}:{port}")
except OSError as e:
    print(f"❌ Cannot reach database at {host}:{port} → {e}")
    print("   Check if Postgres is running or if the SSH tunnel is active.")
    raise SystemExit(1)
