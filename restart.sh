#!/bin/sh
# restart.sh — safely restart the FastAPI Crypto Dashboard backend

APP_DIR="/srv/crypto-charts"
PORT=9000
LOGFILE="$APP_DIR/gunicorn.log"

echo "🔹 Stopping any process on port $PORT..."
sockstat -4 -l | grep $PORT | awk '{print $3}' | xargs -r kill -9 2>/dev/null

echo "🔹 Confirming port is free..."
sockstat -4 -l | grep $PORT && { echo "❌ Port still in use"; exit 1; }

echo "🔹 Starting Gunicorn with async Uvicorn worker..."
cd "$APP_DIR" || exit 1
nohup poetry run gunicorn backend.main:app \
  --workers 3 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 127.0.0.1:$PORT > "$LOGFILE" 2>&1 &

sleep 2
echo "🔹 Active processes on port $PORT:"
sockstat -4 -l | grep $PORT || echo "❌ Nothing running"

echo "🔹 Done."
