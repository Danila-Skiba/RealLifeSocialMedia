#!/bin/bash

echo "========================================="
echo "Запуск всех серверов с Reverse Proxy"
echo "========================================="

cd /Users/danilaskiba/git_repository/RealLifeSocialMedia/theme-project

source ../venv/bin/activate

echo ""
echo "[1/3] Запуск основного сервера (порт 8000)..."
uvicorn server.main:app --reload --port 8000 &
SERVER1_PID=$!

sleep 2

echo "[2/3] Запуск клиентского сервера (порт 8001)..."
uvicorn client.main:app --reload --port 8001 &
SERVER2_PID=$!

sleep 2

echo "[3/3] Запуск Caddy reverse proxy..."
caddy run --config Caddyfile &
CADDY_PID=$!

wait $SERVER1_PID $SERVER2_PID $CADDY_PID

