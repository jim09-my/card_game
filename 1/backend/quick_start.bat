@echo off
chcp 65001 >nul
echo ========================================
echo 后端服务快速启动
echo ========================================
echo.

cd /d %~dp0

echo 检查依赖...
python -c "import fastapi, uvicorn, sqlalchemy" 2>nul
if errorlevel 1 (
    echo 缺少依赖，正在安装...
    python -m pip install -r ../requirements.txt
    if errorlevel 1 (
        echo 依赖安装失败！
        pause
        exit /b 1
    )
)

echo.
echo 启动后端服务...
echo 访问地址: http://localhost:8000/docs
echo 按 Ctrl+C 停止服务
echo.

python start_server.py

pause

