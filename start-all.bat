@echo off
echo ========================================
echo   智能对话助手 - 启动脚本
echo ========================================

echo.
echo [1/3] 启动 Python Agent...
start "Python Agent" cmd /c "cd agent && python main.py"
timeout /t 5 /nobreak > nul

echo [2/3] 启动 Java 后端...
start "Java Backend" cmd /c "cd backend && mvn spring-boot:run"
timeout /t 10 /nobreak > nul

echo [3/3] 启动前端...
start "Frontend" cmd /c "cd frontend && npm run dev"

echo.
echo ========================================
echo   所有服务已启动！
echo   - Python Agent: http://localhost:8000
echo   - Java Backend: http://localhost:8080
echo   - Frontend: http://localhost:5173
echo ========================================
echo.
pause
