#!/bin/bash
# CivilCortex Unified Startup Script
# Starts both FastAPI Backend (port 8000) and Vite Frontend (port 5173)

trap 'kill 0' EXIT INT TERM

echo "=========================================="
echo " Starting CivilCortex Application Suite..."
echo "=========================================="

# 1. Start Backend Server
cd backend
if [ -d ".venv" ]; then
    .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 &
elif [ -d "../.venv" ]; then
    ../.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 &
else
    uvicorn app.main:app --host 0.0.0.0 --port 8000 &
fi
BACKEND_PID=$!
cd ..

# 2. Start Frontend Dev Server
cd frontend
npm run dev -- --host &
FRONTEND_PID=$!
cd ..

echo ""
echo " Backend API:  http://localhost:8000"
echo " Frontend Web: http://localhost:5173"
echo " Press Ctrl+C to stop both servers."
echo "=========================================="

wait
