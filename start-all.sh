#!/bin/bash

echo "========================================"
echo "  智能对话助手 - 启动脚本"
echo "========================================"

echo ""
echo "[1/3] 启动 Python Agent..."
cd agent
python main.py &
AGENT_PID=$!
cd ..
sleep 5

echo "[2/3] 启动 Java 后端..."
cd backend
mvn spring-boot:run &
BACKEND_PID=$!
cd ..
sleep 10

echo "[3/3] 启动前端..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================"
echo "  所有服务已启动！"
echo "  - Python Agent: http://localhost:8000 (PID: $AGENT_PID)"
echo "  - Java Backend: http://localhost:8080 (PID: $BACKEND_PID)"
echo "  - Frontend: http://localhost:5173 (PID: $FRONTEND_PID)"
echo "========================================"
echo ""
echo "按 Ctrl+C 停止所有服务"

trap "kill $AGENT_PID $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT

wait
